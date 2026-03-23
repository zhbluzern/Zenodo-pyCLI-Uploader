print("--- IMPORTS")
# IMPORTS
import json
import requests
from dotenv import load_dotenv
import os
from datetime import datetime
import re
import pandas as pd

import warnings
warnings.filterwarnings(
    "ignore",
    message="Data Validation extension is not supported and will be removed"
)



print("*** IMPORTS OK")

# ------------------------------------------------------------------------------------

# VARS
domain = "hslu_sa"

# ------------------------------------------------------------------------------------

print("--- CREDENTIALS")
# CREDENTIALS
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_URL= os.getenv("API_URL")
print("*** CREDENTIALS OK")

# ------------------------------------------------------------------------------------

print("--- INVENIO CLASS")
# INVENIO REST 
# Invenio REST-API Class
#   combines all methods which requires authentication (ACCESS-TOKEN)
#   create and edit drafts and records, handle requests and files
class Invenio:

    #Initialize Invenio REST Class with  Record-ID, fetch API-Key from .env file
    def __init__(self, recordId=""):
        load_dotenv()
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.API_URL = API_URL
        self.BASE_URL = re.sub("api/","",self.API_URL)
        self.HEADERS = ({"Content-Type" : "application/json",
                         "Accept" : "application/vnd.inveniordm.v1+json",
                         "Authorization" : f"Bearer {self.ACCESS_TOKEN}"})
        
        self.recordSchema = Invenio.resetRecord(self)
        self.recordId = recordId
        # if self.recordId != "":
        #     self.recordId = recordId
        #     self.draft = Invenio.getDraft(self)

    def resetRecord(self):
        self.recordSchema = self.getMinimalRecord()
        return self.recordSchema

    def getMinimalRecord(self):
        with open('json/InvenioData.json', 'r') as dataFile:
            InvenioData=dataFile.read()
        return json.loads(InvenioData)
    
    def createDraft(self, data={}):
        apiUrl = f"{self.API_URL}records"
        r = requests.post(url=apiUrl, headers=self.HEADERS, json=data )
        # return r.json()
        return r

    def publishDraft(self, recordId):
        apiUrl = f"{self.API_URL}records/{recordId}/draft/actions/publish"
        r = requests.post(url=apiUrl, headers=self.HEADERS)
        # return r.json()
        return r
       
    def startDraftFiles(self, recordId, data):
        apiUrl = f"{self.API_URL}records/{recordId}/draft/files"
        #print(apiUrl)
        #print(data)
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
        # return r.json()
        return r

    # Creates a draft for an already published record (this is the first step to update a record)
    def editRecord(self, recordId):
        apiUrl = f"{self.API_URL}records/{recordId}/draft"
        # print(apiUrl)
        headers = self.HEADERS
        headers["Content-Type"] = "application/vnd.inveniordm.v1+json"
        headers["Accept"] = "application/vnd.inveniordm.v1+json"
        r = requests.post(url=apiUrl, headers=headers)
        #print(r.status_code)
        # print(r.json())
        return r.json()

    def updateRecord(self, recordId, data):
        apiUrl = f"{self.API_URL}records/{recordId}/draft"
        print(apiUrl)
        headers = self.HEADERS
        headers["Content-Type"] = "application/json"
        r = requests.put(url=apiUrl, headers=headers, data=json.dumps(data))
        print(r.json())
        return r.json()
            
    def getDraft(self, recordId=""):
        apiUrl = f"{self.API_URL}records/{recordId}/draft"
        r = requests.get(url=apiUrl, headers=self.HEADERS)
        return r.json()

    def getRecord(self, recordId=""):
        apiUrl = f"{self.API_URL}records/{recordId}"
        r = requests.get(url=apiUrl, headers=self.HEADERS)
        return r.json()   

    def getLatestRecordId(self, recordId=""):
        apiUrl = f"{self.API_URL}records/{recordId}/versions/latest"
        r = requests.get(url=apiUrl, headers=self.HEADERS)
        record = r.json()
        return record["id"]
    
    def getLatestRecordIdByDOI(self, doi):
        recordId = re.sub(r"^.+10\.5281\/zenodo\.","",doi)
        latestId = self.getLatestRecordId(recordId)
        return latestId
      
    # Export the Record in several formats as available in the UI (e.g. json, json-ld, datacite-json etc.)
    def exportRecord(self, recordId, format="json"):
        apiUrl = f"{self.BASE_URL}records/{recordId}/export/{format}"
        print (apiUrl)
        r = requests.get(url=apiUrl, headers=self.HEADERS)
        record = r.json()
        # #Remove media_files in Old Data to avoid validation error
        record.pop("media_files")
        return record

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
                if isinstance(affiliation, str):
                    personOrOrg["affiliations"] = [{"name":affiliation}]
                elif isinstance(affiliation, list):
                    personOrOrg["affiliations"] = []
                    for affiliation_str in affiliation:
                        personOrOrg["affiliations"].append({"name":affiliation_str.strip()})
            if role != "":
                personOrOrg["role"] = {"id": role }

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
        #print(url)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, params={'access_token': self.ACCESS_TOKEN}, data=json.dumps(data), headers=headers)
        #print(r.json())
        return r

    
    def removeRecFromCommunity(self, recordId, data):
        url = f"{self.API_URL}records/{recordId}/communities"
        headers = {"Content-Type": "application/json"}
        r = requests.delete(url, params={'access_token': self.ACCESS_TOKEN}, data=json.dumps(data), headers=headers)
        return r

# if __name__ == "__main__":
#     #(os.chdir("src"))
#     invenio = Invenio()
#     recordId = "117334"
#     invenio.addRectoCommunity(recordId,{"communities":[{"id":"lory_hslu_dfk_bnl"}, {"id":"lory"}, {"id":"lory_hslu"}]})

# ------------------------------------------------------------------------------------

print("--- RETRY FUNCTION")
# RETRY FUNCTION
import time
import random
import requests

import logging
import sys

def setup_notebook_logging(level=logging.INFO):
    # Bestehende Handler entfernen (wichtig in Jupyter, sonst wird basicConfig ignoriert)
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)

    console = logging.StreamHandler(stream=sys.stdout)  # unbedingt stdout
    console.setLevel(level)
    console.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    ))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(console)

    # Optional: IPython-Logger (falls genutzt) mitpropagieren lassen
    ipy = logging.getLogger("IPython")
    ipy.setLevel(level)
    ipy.propagate = True

    logging.info("✅ Notebook-Logging aktiviert.")

def call_with_retries(
    func,
    *args,
    max_retries: int = 5,
    base_backoff: float = 1.0,
    retryable_statuses: set = None,
    **kwargs
):
    """
    Ruft `func(*args, **kwargs)` mit Retry-Logik auf.
    - max_retries: maximale Versuche (inkl. Erstversuch)
    - base_backoff: Basiswartezeit (exponentiell + Jitter)
    - retryable_statuses: HTTP-Statuscodes, bei denen Retry versucht wird
    """
    if retryable_statuses is None:
        retryable_statuses = {408, 409, 429}  # typische transiente 4xx
        # retryable_statuses = {408, 409, 429, 403 }  # typische transiente 4xx

    last_exc = None

    for attempt in range(1, max_retries + 1):
        try:
            logging.debug(f"[call_with_retries] Versuch {attempt}/{max_retries} after {attempt} attempts")
            resp = func(*args, **kwargs)  # z. B. invenio.createDraft(record)

            status = getattr(resp, "status_code", None)

            # 5xx → retry
            if status and 500 <= status < 600:
                raise requests.HTTPError(f"Server error {status}", response=resp)

            # bestimmte 4xx → retry (408, 409, 429)
            if status in retryable_statuses:
                raise requests.HTTPError(f"Transient client error {status}", response=resp)

            # übrige 4xx → kein retry
            if status and 400 <= status < 500:
                logging.error(f"[call_with_retries] Client-Fehler {status}: {resp.text[:500]} after {attempt} attempts")
                # r.raise_for_status() wirft eine Exception, wir wollen hier *gezielt* abbrechen
                return resp  # gib die Response zurück, damit der Call-Site damit umgehen kann

            # Erfolg
            logging.info(f"[call_with_retries] Erfolg (HTTP {status}) after {attempt} attempts")
            return resp

        except (requests.Timeout, requests.ConnectionError) as net_err:
            last_exc = net_err
            logging.warning(f"[call_with_retries] Netz-/Timeout-Fehler: {net_err} after {attempt} attempts")
        except requests.HTTPError as http_err:
            last_exc = http_err
            # Wenn Response vorhanden, Status ausgeben
            r = getattr(http_err, "response", None)
            st = getattr(r, "status_code", None)
            logging.warning(f"[call_with_retries] HTTP-Fehler (Status {st}): {http_err} after {attempt} attempts")
        except Exception as e:
            # Unbekannt: i. d. R. kein Retry sinnvoll, aber hier retryen wir nur,
            # wenn noch Versuche übrig sind und du das möchtest. Default: abbrechen.
            last_exc = e
            logging.exception(f"[call_with_retries] Unerwarteter Fehler: {e} after {attempt} attempts")
            # Abbrechen ohne weitere Versuche:
            break

        # Falls wir hier sind → ein retrybarer Fehler ist aufgetreten
        if attempt < max_retries:
            # Exponentieller Backoff + Jitter
            sleep_s = base_backoff * (2 ** (attempt - 1))
            jitter = random.uniform(0, sleep_s * 0.2)  # bis zu 20% Jitter
            wait = sleep_s + jitter
            logging.warning(f"[call_with_retries] Backoff {wait:.2f}s, nächster Versuch…  after {attempt} attempts")
            time.sleep(wait)
        else:
            logging.error(f"[call_with_retries] Alle {max_retries} Versuche fehlgeschlagen. after {attempt} attempts")
            # Option: letzte Exception werfen
            if last_exc:
                raise last_exc

    # Falls wir hier landen
    return None
print("*** INVENIO CLASS + RETRY FUNCTION OK")

# ------------------------------------------------------------------------------------

print("--- DRAFT")
# DRAFT 

# ------------------------------------------------------------------------------------

### Read a Metadata-Excel-File
data = pd.read_excel(f"{domain}/input/draft.xlsx", header=0, skiprows=[1])
df = pd.DataFrame(data)
df = df[(df['status']) > 0]
initColumns = df.columns
# df.info()
df.head(3)

for index, row in df.iterrows():
    #create Zenodo-Record
    invenio = Invenio()

    #Build the empty deposition metadata dict
    metadata = {"metadata" : {}}

    custom_fields = {"custom_fields" : {}}

    #List of Creators
    creators = row.creators.replace('\n\n', '\n').split("\n")
    
    metadata["metadata"].update({"creators": []})
    for creator in creators:
        creatorDict = {}
        creatorNameList = creator.split(",")
        creatorDict["name"] = creatorNameList[1].strip()
        creatorDict["family_name"] = creatorNameList[0].strip()
        creatorDict["affiliation"] = "Hochschule Luzern – Soziale Arbeit"

        creatorName = creatorDict["name"] + ";" + creatorDict["family_name"]
        metadata["metadata"]["creators"].append(invenio.setPersonOrOrg(
                name=creatorName,
                splitChar=";",
                familyNameFirst=False,
                affiliation=creatorDict["affiliation"],
        ))

    
    #Abstract - Description
    # if row.description.endswith(".docx") == True:
    #     descriptionTxt = docx.get_docx_text(f"hslu_sa/Files/{row.description}")
    if row.description.endswith(".txt") == True:
        txtF = open(f"hslu_sa/Files/{row.description}", encoding="utf8")
        descriptionTxt = txtF.read()
    else:
        descriptionTxt = row.description
    #print(descriptionTxt)
    metadata["metadata"].update({"description": descriptionTxt})

    #Title
    metadata["metadata"]["title"] = row.title

    #additional_descriptions
    addDesc = {"description": row.additional_descriptions, "type": {"id":"notes", "title": {"de":"Anmerkungen", "en":"Notes"}}}
    metadata["metadata"].update({"additional_descriptions": []})
    metadata["metadata"]["additional_descriptions"].append(addDesc)
    
    #publicationDate, publisher
     
    # LICENSE, PUBLISHER, VERSION ---------------------------------------------
    metadata["metadata"]["rights"] = [ {"id":"cc-by-nc-nd-4.0"}]
    # metadata["metadata"]["publisher"] = row.publisher   
    metadata["metadata"]["publisher"] = "Hochschule Luzern – Soziale Arbeit"   
    metadata["metadata"]["publication_date"] = row.publication_date.strftime("%Y-%m-%d")

    if row.resource_type == "publication-report":
        # metadata["metadata"]["upload_type"] = "publication"
        # metadata["metadata"]["publication_type"] = "report"
        metadata["metadata"]["resource_type"] = {"id":"publication-report"}
    
    elif row.resource_type == "publication-thesis" or row.resource_type == "publication-dissertation":
         
        metadata["metadata"]["upload_type"] = "publication"
        metadata["metadata"]["publication_type"] = "thesis"  
        metadata["metadata"]["thesis_university"] = "Hochschule Luzern – Soziale Arbeit"   
       
        # ACHTUNG: publication-thesis existiert nicht auf Sandbox!!!
        metadata["metadata"]["resource_type"] = {
            "id":"publication-dissertation",
            "id":"publication-thesis",
            "title": {
                "de": "Abschlussarbeit",
                "en": "Thesis"
            }
        }
        
        
        custom_fields["custom_fields"] = {
                "thesis:thesis" : {
                   "university": "Hochschule Luzern – Soziale Arbeit",
                   "type" : row.typ
                }
            }
        
    record = invenio.recordSchema
    record["metadata"] = metadata["metadata"]
    record["custom_fields"] = custom_fields["custom_fields"]
    
  #  newRecord = invenio.createDraft(record)
    newRecord = call_with_retries(lambda: invenio.createDraft(record), max_retries=5)
    
    newRecordJson = newRecord.json()
    print(newRecordJson["id"],newRecordJson["metadata"]["title"], ":",newRecord.status_code)

    prefixProd = "10.5281/zenodo."

    df.at[index, "ZenodoId"] = str(newRecordJson["id"])
    df.at[index, "ZenodoConceptId"] = str(newRecordJson["parent"]["id"])
    df.at[index, "ConceptDOI"] = prefixProd+ str(newRecordJson["parent"]["id"])  
     
    df.at[index, "DOI"] = prefixProd+str(newRecordJson["id"])
    df.at[index, "drafted-code"] = newRecord.status_code
    

timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")

df.to_excel(f"{domain}/output/drafted_{timestamp}.xlsx", index=False, engine="openpyxl")
df.to_excel(f"{domain}/output/drafted.xlsx", index=False, engine="openpyxl")
df.to_excel(f"{domain}/input/upload.xlsx", index=False, engine="openpyxl")
# Iterate through items

print("*** DRAFTS OK")

# ------------------------------------------------------------------------------------

print("--- UPLOADS")
# UPLOAD 

# ------------------------------------------------------------------------------------
# Uploads
import os
from urllib.parse import urlparse
import urllib.request
import glob
from IPython.display import clear_output

def downloadFile(fileUrl, localPath, fileName=""):
    if fileName == "":
        fileName =  getFileName(fileUrl)  
    urllib.request.urlretrieve(fileUrl, f"{localPath}/{fileName}")

def getFileName(fileUrl):
    a = urlparse(fileUrl)
    #print(a.path)                    
    return (os.path.basename(a.path))

def uploadFile(invenio, listFiles, recordId, filePath=""):
    # print(listFiles)
    uploadFiles = [os.path.basename(file) for file in listFiles]
    listOfFilesInvenioData = []
    for file in uploadFiles:
        listOfFilesInvenioData.append({"key":file})
        #handleFiles.downloadFile(fileUrl[0].text, localPath="nlv/Files")
        #print(listOfFilesInvenioData)
    fileDraft = invenio.startDraftFiles(recordId, data=listOfFilesInvenioData)
    # print("foo",fileDraft)
    for filename in uploadFiles:
        with open(f"{filePath}/{filename}", 'rb') as f:
            data = f.read()
            #print(data)
        fileUpload = invenio.uploadFileContent(recordId, fileName=filename, fileContent=data)
        r = invenio.commitFileUpload(recordId, fileName=filename)
        return r

# ------------------------------------------------------------------------------------
# Test whether files exist 
from pathlib import Path

#Read a Metadata-Excel-File
data = pd.read_excel(f"{domain}/input/upload.xlsx", header=0)

dfu = pd.DataFrame(data)
dfu = dfu[(dfu['status']) > 0]
initColumns = dfu.columns
listOfFiles = []

for index, row in dfu.iterrows():
    listOfFiles.append(row["files"])
    
uploadFiles = [os.path.basename(file) for file in listOfFiles]
filePath=f"{domain}/files"
for filename in uploadFiles:
    file = Path(filePath) / filename
    if file.exists():
        print(f"{filename} upload file exists")
    else:
        print(f"{filename} missing !!!")
# ------------------------------------------------------------------------------------
# Upload
#Read a Metadata-Excel-File
data = pd.read_excel(f"{domain}/input/upload.xlsx", header=0)

dfu = pd.DataFrame(data)
dfu = dfu[(dfu['status']) > 0]
initColumns = dfu.columns

for index, row in dfu.iterrows():
    # clear_output()
    
    #create Zenodo-Record
    invenio = Invenio()
    record = invenio.recordSchema

    # UPLOAD FILE
#    existingDraftId = invenio.getDraft(row["ZenodoId"])["id"]
    existingDraft = call_with_retries(lambda: invenio.getDraft(row["ZenodoId"]), max_retries=5)
    existingDraftId = existingDraft["id"]

    # print(existingDraftId)

    listOfFiles = []
    # print(row["File"])
    listOfFiles.append(row["files"])
   # uploadResponse = uploadFile(invenio,listOfFiles,existingDraftId,f"{domain}/files/")
    uploadResponse = call_with_retries(lambda: uploadFile(invenio,listOfFiles,existingDraftId,f"{domain}/files/"), max_retries=5)
    print(index, "Upload: ", existingDraftId,uploadResponse.status_code)
    dfu.at[index, "uploaded-code"] = uploadResponse.status_code
    
        
timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")

dfu.to_excel(f"{domain}/output/uploaded_{timestamp}.xlsx", index=False, engine="openpyxl")
dfu.to_excel(f"{domain}/output/uploaded.xlsx", index=False, engine="openpyxl")
dfu.to_excel(f"{domain}/input/publish.xlsx", index=False, engine="openpyxl")

print("*** UPLOADS OK")

# ------------------------------------------------------------------------------------

print("--- PUBLISH")

# PUBLISH
# ------------------------------------------------------------------------------------

# FOR DEBUGGING
#communities = [{"id": "roracom"}]

#Read a Metadata-Excel-File
data = pd.read_excel(f"{domain}/input/publish.xlsx", header=0)

dfp = pd.DataFrame(data)
dfp = dfp[(dfp['status']) > 0]
initColumns = dfp.columns

for index, row in dfp.iterrows():    
    #create Zenodo-Record
    invenio = Invenio()

    # PUBLISH FILE
    recId = row["ZenodoId"]

  #  publishResponse = invenio.publishDraft(recId)
    publishResponse = call_with_retries(lambda: invenio.publishDraft(recId), max_retries=5)
    print(index, "Published: ",recId, publishResponse.status_code)  
    dfp.at[index, "published-code"] = publishResponse.status_code
    
    
    # Communities
# communities = [{"id": "lara"},{"id": "lara_sa"},{"id": "lara_sa_hslu_sa"}]

    communities = []
    communitiesList = row.communities.split("\n")

    for community in communitiesList:
        communities.append({"id":community.strip()})

    
   # communityResponse = invenio.addRectoCommunity(recId, {"communities": communities})
    communityResponse =  call_with_retries(lambda: invenio.addRectoCommunity(recId, {"communities": communities}), max_retries=5)
    print(index,"Community: ", recId,communityResponse.status_code, communities)
    dfp.at[index, "communities-status"] = communityResponse.status_code

timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
dfp.to_excel(f"{domain}/output/published_{timestamp}.xlsx", index=False, engine="openpyxl")
dfp.to_excel(f"{domain}/output/published.xlsx", index=False, engine="openpyxl")

print("*** PUBLISH OK")


