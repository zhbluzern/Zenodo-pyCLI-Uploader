# test heka / 23.5.25

import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio
import json
import re
import pandas as pd


#Read a Metadata-Excel-File
data = pd.read_excel(r'lory_zhb_test.xlsx')
df = pd.DataFrame(data)
initColumns = df.columns

print(df.head())
#df = df.iloc[[10, 13, 31], :] #three selected articles as test sample
#df = df.iloc[[9], :] #one selected article as test sample

for index, row in df.iterrows():

    #create note
    dlza_note = {
        "description": "Langzeitarchivierung durch : "+row["organisation"]+" - "+row["signature"]+" - "+row["last_changed"][0:10],
        "type": {
            "id": "notes",
            "title": {
                "de": "Anmerkungen",
                "en": "Notes"
            }
        }
    }
    dlza_identifier = {
        "identifier": row["signature"],
        "scheme": "other"
        
    } 

    recordId = row["signature"].split("_")[-1]
    print(recordId)
    #create Zenodo-Record
    zenodo = InvenioRest.Invenio()
    #record = zenodo.recordSchema
   
    zenodo.editRecord(recordId)
    record = zenodo.exportRecord(recordId)

    #record["metadata"].append("additional_descriptions: "+str(dlza_note))
    if "additional_descriptions" not in record["metadata"]:
        record["metadata"]["additional_descriptions"] = []
    record["metadata"]["additional_descriptions"].append(dlza_note)

    print(record["metadata"]["additional_descriptions"][-1]["description"])

    if "identifiers" not in record["metadata"]:
        record["metadata"]["identifiers"] = []
    record["metadata"]["identifiers"].append(dlza_identifier)

    print(record["metadata"]["identifiers"][-1]["identifier"])
    #print(record["metadata"])

    zenodo.updateRecord(recordId, record)
    print(zenodo.publishDraft(recordId))    
    #break
