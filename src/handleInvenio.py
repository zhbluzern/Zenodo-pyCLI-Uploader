import src.ZenodoSearch as ZenodoSearch
import glob
import os
from datetime import datetime


def acceptAllRequests(zen, newRecord):
    #Search for alle Requests by the new Record-ID
    zenRequ = zen.searchRequests(f"topic.record:{newRecord['id']}")
    results = (zenRequ.json())
    
    for hit in results["hits"]["hits"]:
        print(hit["id"])
        print(hit["type"])
        #print(hit["links"]["actions"]["accept"])
        print(zen.acceptRequest(hit["id"]).text)
