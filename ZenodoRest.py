import json
import requests
from dotenv import load_dotenv
import os

class Zenodo:

    # Initialisiere Zenodo-Klasse mit Zenodo-Record-ID, hole API-Key aus .env-File
    def __init__(self, ZenodoId=""):
        load_dotenv()
        self.ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
        if ZenodoId == "":
            self.ZenodoId = self.createDeposit()
        else:
            self.ZenodoId = ZenodoId

    # createDeposit-Methode - lege einen neuen leeren Datensatz an
    def createDeposit(self):
        headers = {"Content-Type": "application/json"}
        params = {'access_token': self.ACCESS_TOKEN}
        r = requests.post('https://zenodo.org/api/deposit/depositions',
                        params=params,
                        json={},
                        headers=headers)
        deposition_id = r.json()["id"]
        return deposition_id

    # uploadFile Methode
    def uploadFile(self, fileName, filePath=""):
        url = f"https://zenodo.org/api/deposit/depositions/{self.ZenodoId}/files?access_token={self.ACCESS_TOKEN}"
        data = {'name': fileName}
        files = {'file': open(filePath+fileName, 'rb')}
        r = requests.post(url, data=data, files=files)
        return r

    # setEdit-Methode - versetzt einen publizierten Datensatz in den Draft-Status zur Bearbeitung
    def setEdit(self):
        r = requests.post(f'https://zenodo.org/api/deposit/depositions/{self.ZenodoId}/actions/edit',
                  params={'access_token': self.ACCESS_TOKEN})
        return r

    # getRecordData-Methode holt den Metadatensatz zur weiteren Bearbeitung
    def getRecordData(self):
        r = requests.get(f"https://zenodo.org/api/deposit/depositions/{self.ZenodoId}?access_token={self.ACCESS_TOKEN}")
        data_r = (r.json())
        return data_r

    #putRecord-Data-Methode lädt Metadatenrecord nach Zenodo zurück
    def putRecordData(self, data):
        url = f"https://zenodo.org/api/deposit/depositions/{self.ZenodoId}?access_token={self.ACCESS_TOKEN}"
        headers = {"Content-Type": "application/json"}
        r = requests.put(url, data=json.dumps(data), headers=headers)
        return r

    def publishRecord(self):
        url = f"https://zenodo.org/api/deposit/depositions/{self.ZenodoId}/actions/publish"
        r = requests.post(url, params={'access_token': self.ACCESS_TOKEN})
        return r

