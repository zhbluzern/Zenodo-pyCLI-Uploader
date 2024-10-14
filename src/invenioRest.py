import json
import requests
from dotenv import load_dotenv
import os
from datetime import datetime


# Invenio REST-API Class
#   combines all methods which requires authentication (ACCESS-TOKEN)
#   create and edit drafts and records, handle requests and files
class Invenio:

    #Initialize Invenio REST Class with  Record-ID, fetch API-Key from .env file
    def __init__(self, recordId=""):
        load_dotenv()
        self.ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
        self.API_URL = os.getenv("API_URL")
        self.HEADERS = ({"Content-Type" : "application/json", "Authorization" : f"Bearer {self.ACCESS_TOKEN}"})
        self.recordSchema = Invenio.resetRecord(self)
        self.recordId = recordId
        # if self.recordId != "":
        #     self.recordId = recordId
        #     self.draft = Invenio.getDraft(self)

    def resetRecord(self):
        self.recordSchema = self.getMinimalRecord()
        return self.recordSchema

    def getMinimalRecord(self):
        with open('src/InvenioData.json', 'r') as dataFile:
            InvenioData=dataFile.read()
        return json.loads(InvenioData)
    
    def createDraft(self, data={}):
        apiUrl = f"{self.API_URL}records"
        r = requests.post(url=apiUrl, headers=self.HEADERS, json=data )
        return r.json()

    def publishDraft(self, recordId):
        apiUrl = f"{self.API_URL}records/{recordId}/draft/actions/publish"
        r = requests.post(url=apiUrl, headers=self.HEADERS)
        return r.json()
       
    def startDraftFiles(self, recordId, data):
        apiUrl = f"{self.API_URL}records/{recordId}/draft/files"
        print(data)
        r = requests.post(url=apiUrl, headers=self.HEADERS, json=data)
        return r.json()
    
    def uploadFileContent(self, recordId, fileName, fileContent):
        apiUrl = f"{self.API_URL}records/{recordId}/draft/files/{fileName}/content"
        headers = self.HEADERS
        headers["Content-Type"] = "application/octet-stream"
        r = requests.put(url=apiUrl, headers=headers,data=fileContent)
        return r.json()       

    def commitFileUpload(self, recordId, fileName):
        apiUrl = f"{self.API_URL}records/{recordId}/draft/files/{fileName}/commit"
        r = requests.post(url=apiUrl, headers=self.HEADERS)
        return r.json()

    def editRecord(self, recordId):
        apiUrl = f"{self.API_URL}records/{recordId}/draft"
        #print(apiUrl)
        r = requests.post(url=apiUrl, headers=self.HEADERS)
        print(r.status_code)
        return r.json()

    def updateRecord(self, recordId, data):
        apiUrl = f"{self.API_URL}records/{recordId}/draft"
        r = requests.put(url=apiUrl, headers=self.HEADERS, data=json.dumps(data))
        return r.json()
            
    def getDraft(self, recordId=""):
        apiUrl = f"{self.API_URL}records/{recordId}/draft"
        print(apiUrl)
        r = requests.get(url=apiUrl, headers=self.HEADERS)
        return r.json()

    def getRecord(self, recordId=""):
        apiUrl = f"{self.API_URL}records/{recordId}"
        print(apiUrl)
        r = requests.get(url=apiUrl, headers=self.HEADERS)
        return r.json()   

    def setPersonOrOrg(self, name, type="personal",  splitChar="", persIdScheme="", persId="", affiliation="", role="", familyNameFirst=True):
        personOrOrg = {"person_or_org": { "type": type, "name": name} }
        if type=="personal": 
            namePart = name.split(splitChar)
            if familyNameFirst == True:
                personOrOrg["person_or_org"]["family_name"] = namePart[0]
                personOrOrg["person_or_org"]["given_name"] = namePart[1]
            else:
                personOrOrg["person_or_org"]["family_name"] = namePart[1]
                personOrOrg["person_or_org"]["given_name"] = namePart[0]               
            if affiliation != "":
                personOrOrg["person_or_org"]["affiliations"] = [{"name":affiliation}]

            if role != "":
                personOrOrg["person_or_org"]["role"] = {"id": role }

        if persId != "" and persIdScheme != "":
                personOrOrg["person_or_org"]["identifiers"] = [{"scheme": persIdScheme, "identifier": persId}]

        return personOrOrg
            
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
    
    def addRectoCommunity(self, recordId, data):
        url = f"{self.API_URL}records/{recordId}/communities"
        print(url)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, params={'access_token': self.ACCESS_TOKEN}, data=json.dumps(data), headers=headers)
        return r
    
    def removeRecFromCommunity(self, recordId, data):
        url = f"{self.API_URL}records/{recordId}/communities"
        headers = {"Content-Type": "application/json"}
        r = requests.delete(url, params={'access_token': self.ACCESS_TOKEN}, data=json.dumps(data), headers=headers)
        return r

if __name__ == "__main__":
    #(os.chdir("src"))
    zenodo = Invenio()

    """
    zenodo.recordSchema["metadata"]["title"] = "Testdatensatz"
    zenodo.recordSchema["metadata"]["resource_type"] = {"id":"publication-other"}
    zenodo.recordSchema["metadata"]["publication_date"] = datetime.today().strftime('%Y-%m-%d')
    zenodo.recordSchema["metadata"]["publisher"] = "Zentral- und Hochschulbibliothek Luzern"
    zenodo.recordSchema["metadata"]["languages"] = [{"id":"deu"}]

    creator = zenodo.setPersonOrOrg("Erlinger, Christian", splitChar=", ", persIdScheme="GND", persId="123456789", affiliation="ZHB Luzern")
    zenodo.recordSchema["metadata"]["creators"].append(creator)
    creator = zenodo.setPersonOrOrg("Zentral- und Hochschulbibliothek Luzern",type="organizational", persId="4647881-4", persIdScheme="GND")
    zenodo.recordSchema["metadata"]["creators"].append(creator)
    
    zenodo.recordSchema["metadata"]["contributors"] = []
    contrib = zenodo.setPersonOrOrg(name="End, Gotthard", splitChar=", ", persId="120183366", persIdScheme="GND", role="other")
    zenodo.recordSchema["metadata"]["contributors"].append(contrib)
    
    zenodo.recordSchema["metadata"]["rights"] = [{"id": "cc-by-4.0","icon": "cc-by-icon", "title": {"en": "Creative Commons Attribution 4.0 International"}, "description": {"en": "The Creative Commons Attribution license allows re-distribution and re-use of a licensed work on the condition that the creator is appropriately credited."}, "link": "https://creativecommons.org/licenses/by/4.0/"}]

    zenodo.recordSchema["metadata"]["subjects"] = [{"subject": "Nachlass"}]
    print(json.dumps(zenodo.recordSchema,indent=1))

    zenodo.resetRecord()
    print(zenodo.recordSchema)
    """
    # recordId = "30420"
    # req = zenodo.searchRequests(f"topic.record:{recordId}")
    # results = req.json()
    # print(results)
    # for hit in results["hits"]["hits"]:
    #     print(hit["id"])
    #     print(hit["type"])
    #     #print(hit["links"]["actions"]["accept"])
    #     print(zenodo.acceptRequest(hit["id"]).text)

    recordId = "117334"
    zenodo.addRectoCommunity(recordId,{"communities":[{"id":"lory_hslu_dfk_bnl"}, {"id":"lory"}, {"id":"lory_hslu"}]})