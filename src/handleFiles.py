import os
from urllib.parse import urlparse
import urllib.request

def downloadFile(fileUrl, localPath):    
    urllib.request.urlretrieve(fileUrl, f"{localPath}/{getFileName(fileUrl)}")

def getFileName(fileUrl):
    a = urlparse(fileUrl)
    #print(a.path)                    
    return (os.path.basename(a.path)) 