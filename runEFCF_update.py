import pandas as pd
import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio

import json
import re
from datetime import datetime

#Read a Metadata-Excel-File
data = pd.read_excel(r'EFCF/UpdateData.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns

print(df.head())

for index, row in df.iterrows():
    
    #create Zenodo-Record
    zenodo = InvenioRest.Invenio()
    record = zenodo.recordSchema
    zenSearch = ZenodoSearch.ZenodoSearch()

#    https://inveniordm.docs.cern.ch/reference/metadata/#description-0-1


    # UPDATE DRAFT
#     zenodo.editRecord(row["ZenodoId"])
#     existingRecord = zenodo.getDraft(row["ZenodoId"])
#    # existingRecord = zenodo.exportRecord(row["ZenodoId"])
    
#     updateData = existingRecord
#     updateData["metadata"]["title"] = "foobar"
    
#     print(zenodo.updateRecord(row["ZenodoId"], updateData))

    existingDraftId = row["ZenodoId"]
    
    # ADD TO COMMUNITY
  #  print(zenodo.addRectoCommunity(existingDraftId, {"communities": [{"id": "lara"}]}))

    
