import json
import requests
from dotenv import load_dotenv
import os


# Zenodo Class
#   combines all methods which requires authentication (ACCESS-TOKEN)
#   create and edit drafts and records, handle requests and files
class Zenodo:

    # Initialisiere Zenodo-Klasse mit Zenodo-Record-ID, hole API-Key aus .env-File
    def __init__(self, ZenodoId=""):
        load_dotenv()
        self.ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
        self.API_URL = os.getenv("API_URL")
        if ZenodoId == "":
            self.ZenodoId = self.createDeposit()
        else:
            self.ZenodoId = ZenodoId

    # createDeposit-Methode - lege einen neuen leeren Datensatz an und gibt die Record-Id zurück
    def createDeposit(self):
        headers = {"Content-Type": "application/json"}
        params = {'access_token': self.ACCESS_TOKEN}
        r = requests.post(f'{self.API_URL}deposit/depositions',
                        params=params,
                        json={},
                        headers=headers)
        deposition_id = r.json()["id"]
        return deposition_id

    # uploadFile Methode
    def uploadFile(self, fileName, filePath=""):
        url = f"{self.API_URL}deposit/depositions/{self.ZenodoId}/files?access_token={self.ACCESS_TOKEN}"
        data = {'name': fileName}
        files = {'file': open(filePath+fileName, 'rb')}
        r = requests.post(url, data=data, files=files)
        return r

    # setEdit-Methode - versetzt einen publizierten Datensatz in den Draft-Status zur Bearbeitung
    def setEdit(self):
        r = requests.post(f'{self.API_URL}deposit/depositions/{self.ZenodoId}/actions/edit',
                  params={'access_token': self.ACCESS_TOKEN})
        return r

    # getRecordData-Methode holt den Metadatensatz zur weiteren Bearbeitung
    def getRecordData(self):
        r = requests.get(f"{self.API_URL}deposit/depositions/{self.ZenodoId}?access_token={self.ACCESS_TOKEN}")
        data_r = (r.json())
        return data_r

    #putRecord-Data-Methode lädt Metadatenrecord nach Zenodo zurück
    def putRecordData(self, data):
        url = f"{self.API_URL}deposit/depositions/{self.ZenodoId}?access_token={self.ACCESS_TOKEN}"
        headers = {"Content-Type": "application/json"}
        r = requests.put(url, data=json.dumps(data), headers=headers)
        return r

    def publishRecord(self):
        url = f"{self.API_URL}deposit/depositions/{self.ZenodoId}/actions/publish"
        r = requests.post(url, params={'access_token': self.ACCESS_TOKEN})
        return r
    
    def acceptRequest(self,requestId, payload=""):
        url = f"{self.API_URL}requests/{requestId}/actions/accept"
        headers = {"Content-Type": "application/json"}
        if payload == "":
            payload = {}
            payload["payload"] = {"content" : "Automatischer Accept Request via REST-API (ERCH)", "format" : "html"}
        r = requests.post(url, params={'access_token': self.ACCESS_TOKEN}, data=json.dumps(payload), headers=headers )
        return r
    
    def searchRequests(self,queryString=""):
        url = f"{self.API_URL}requests"
        r = requests.get(url=url, params={'access_token': self.ACCESS_TOKEN, 'q' : queryString})
        return r
    

# ZenodoSearch Class 
#    combines several methods for GET-Request which don't need API-KEY authentification
#    classical "query"-Requests (records, communities, requests)
class ZenodoSearch:
    def __init__(self):
        load_dotenv()
        self.ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
        self.API_URL = os.getenv("API_URL")

    def searchCommunityBySlug(self, slug):
        url = f"{self.API_URL}communities"
        r = requests.get(url=url, params={'q' : f"slug:{slug}"})
        return r
    
    def getCommunityIdBySlug(self, slug):
        results = self.searchCommunityBySlug(slug).json()
        if (len(results["hits"]["hits"])) == 1 and results["hits"]["hits"][0]["slug"] == slug: #1 Result means probably an exact match for the community slug
            for hit in results["hits"]["hits"]:
                print(f"searched for community {slug} and matched slug {hit['slug']} with id {hit['id']}")
                return hit["id"]

