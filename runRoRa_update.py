import pandas as pd
import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio

import json
import re
from datetime import datetime

#Read a Metadata-Excel-File
data = pd.read_excel(r'RoRa/update.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns

# print(df.head())j

###########################################################################
###########################################################################
###########################################################################
###########################################################################

# My Analysis by 2025-08-14:

# Drafts cannot be updated because the data from GET /api/records/{id}/draft 
# (as well as from /api/records/{id}/ )
# is not in the needed format compared to the data coming from GET /api/records/{id}/export and describend 
# https://inveniordm.docs.cern.ch/reference/rest_api_drafts_records/#get-a-draft-record



###########################################################################
###########################################################################
###########################################################################
###########################################################################


for index, row in df.iterrows():
    
    zenodo = InvenioRest.Invenio()
    recordId = row["ZenodoId"]
    recordId = "311734"
    
    ## For published records --->
    zenodo.editRecord(recordId)
    record = zenodo.exportRecord(recordId)
    
    #record2 = zenodo.getDraft(recordId)
    #record3 = zenodo.getRecord(recordId)
    
    #print(record3)
    
    # UPDATE DRAFT
    
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    record["metadata"]["title"] = "foobar-"+timestamp
    
    additionalDescriptions = []
    additionalDescriptions.append(
        {
            "description": "<p>Contact authors: <a href='https://www.EFCF.com/ContactRequest' target='_blank' >www.EFCF.com/ContactRequest</a></p><p>Library: <a href='https://www.efcf.com/Library' target='_blank' >www.efcf.com/Library</a>&nbsp;</p>",
            "type": {
            "id": "notes",
            "title": {
                "de": "Anmerkungen",
                "en": "Notes"
                }
            }
        }
    )
    
    record["metadata"]["additional_descriptions"] = additionalDescriptions
    
       
    
    zenodo.updateRecord(recordId, record)

    # <---
    
    
timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
# df.to_excel(f"RoRa/updated_{timestamp}.xlsx", index=False, engine="openpyxl")

