import os
from urllib.parse import urlparse
import urllib.request
import glob

def downloadFile(fileUrl, localPath, fileName=""):
    if fileName == "":
        fileName =  getFileName(fileUrl)  
    urllib.request.urlretrieve(fileUrl, f"{localPath}/{fileName}")

def getFileName(fileUrl):
    a = urlparse(fileUrl)
    #print(a.path)                    
    return (os.path.basename(a.path))

def uploadFile(zenodo, listFiles, newRecord):
    uploadFiles = [os.path.basename(file) for file in listFiles]
    listOfFiles = []
    for file in uploadFiles:
        listOfFiles.append({"key":file})
        #handleFiles.downloadFile(fileUrl[0].text, localPath="nlv/Files")
    fileDraft = zenodo.startDraftFiles(newRecord["id"], data=listOfFiles)

    for filename in uploadFiles:
        with open(f"bnl/Files/{filename}", 'rb') as f:
            data = f.read()
        fileUpload = zenodo.uploadFileContent(newRecord["id"], fileName=filename, fileContent=data)
        #print(fileUpload)
        print(zenodo.commitFileUpload(newRecord["id"], fileName=filename))
