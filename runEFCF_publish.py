import pandas as pd
import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio

import json
import re
from datetime import datetime

#Read a Metadata-Excel-File
data = pd.read_excel(r'EFCF/publish.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns

#print(df.head())

for index, row in df.iterrows():
    
    #create Zenodo-Record
    zenodo = InvenioRest.Invenio()
    record = zenodo.recordSchema
    zenSearch = ZenodoSearch.ZenodoSearch()

#    https://inveniordm.docs.cern.ch/reference/metadata/#description-0-1


    # PUBLISH FILE
    existingRecord = zenodo.getDraft(row["ZenodoId"])
    recId = row["ZenodoId"]
    print(zenodo.publishDraft(recId))
  
    df.at[index, "published"] = "True"
    
     # ADD TO COMMUNITIES
    print(zenodo.addRectoCommunity(recId, {"communities": [{"id": "lara_conf_efcf"},{"id": "lara"}]}))

df.to_excel("EFCF/published.xlsx", index=False, engine="openpyxl")
