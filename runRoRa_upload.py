import pandas as pd
import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio

import json
import re
from datetime import datetime

#Read a Metadata-Excel-File
data = pd.read_excel(r'RoRa/upload.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns

#print(df.head())

for index, row in df.iterrows():
    
    #create Zenodo-Record
    zenodo = InvenioRest.Invenio()
    record = zenodo.recordSchema
    zenSearch = ZenodoSearch.ZenodoSearch()

#    https://inveniordm.docs.cern.ch/reference/metadata/#description-0-1


    # UPLOAD FILE
    existingDraft = zenodo.getDraft(row["ZenodoId"])

    listOfFiles = []
    print(row["File"])
    listOfFiles.append(row["File"])
    print(handleFiles.uploadFile(zenodo,listOfFiles,existingDraft,"RoRa/files/"))

  #  print(existingDraft)
        
timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
df.to_excel(f"RoRa/uploaded_{timestamp}.xlsx", index=False, engine="openpyxl")
