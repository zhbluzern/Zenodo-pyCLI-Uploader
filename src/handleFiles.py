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

def uploadFile(zenodo, listFiles, recordId, filePath=""):
    print(listFiles)
    uploadFiles = [os.path.basename(file) for file in listFiles]
    listOfFilesInvenioData = []
    for file in uploadFiles:
        listOfFilesInvenioData.append({"key":file})
        #handleFiles.downloadFile(fileUrl[0].text, localPath="nlv/Files")
        #print(listOfFilesInvenioData)
    fileDraft = zenodo.startDraftFiles(recordId, data=listOfFilesInvenioData)
    #print(fileDraft)
    for filename in uploadFiles:
        with open(f"{filePath}/{filename}", 'rb') as f:
            data = f.read()
            #print(data)
        fileUpload = zenodo.uploadFileContent(recordId, fileName=filename, fileContent=data)
        print(fileUpload)
        r = zenodo.commitFileUpload(recordId, fileName=filename)
