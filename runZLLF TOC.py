import pandas as pd
import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio
import bnl.bnlParser as bnlParser
import json
import re
from datetime import datetime

# ****************************************************
# Hinweise
# 
# Am 29.03.2025 wurden für den Sammelband Draft-Records angelegt
# Es fehlen folgende Metadaten:
# * PublicationDate (aus XLS oder fix implementieren)
# * Communities
# * ggf. Page-Range im imprimt:imprint
# 
# Am 26.08.2025 erfolgte eine Korrektur der Metadaten (tlw. Personen, tlw. Titel, Rechte)
# und File-Upload. 

#Read a Metadata-Excel-File
data = pd.read_excel(r'Files/Sammelband-ZLLF-Raster_DOI_20250826.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns
#Define new Columns with explicit dtype for correct export
# df['ZenodoId'] = pd.Series(dtype='str')
# df['DOI'] = pd.Series(dtype='str')
print(df.head())

#Fetch Containing Book Record
zenodo = InvenioRest.Invenio()
recordId = "15065419"
record = zenodo.editRecord(recordId)
record = zenodo.exportRecord(recordId)
# print(book["metadata"]["creators"])
# print(book["metadata"]["title"])
# print(book["metadata"]["resource_type"])
print(record["metadata"]["related_identifiers"])
description = "Dieser Sammelband umfasst folgende Einzelbeiträge: <ul>"

def format_citation(authors):
    def format_name(name):
        parts = name.split(",")
        last_name = parts[0].strip()
        given_name = parts[1].strip() if len(parts) > 1 else ""
        initials = "".join([n[0] for n in given_name.split() if n])  # Handles multiple given names
        return f"{last_name}, {initials}"

    formatted = [format_name(author) for author in authors]

    if not formatted:
        return ""
    elif len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} & {formatted[1]}"
    else:
        return f"{', '.join(formatted[:-1])}, & {formatted[-1]}"


for index, row in df.iterrows():

    relation = {"identifier":row["DOI"],
                "scheme":"doi",
                "relation_type": {"id":"haspart"}, "resource_type": {"id": "publication-section"}
                }
    record["metadata"]["related_identifiers"].append(relation)

    creators = []
    creatorsAffil = []
    for col in initColumns:
            #print(col)
            value = getattr(row, col)  # Get the value of the column in the current row
            if pd.notna(value):  # Only add the value if it's not NA
                if col.startswith("Creator_Author_Affiliation"):
                    creatorsAffil.append(value)                     
                elif col.startswith("Creator_Author_"):
                    creators.append(value)

    citationString = f"<li>{format_citation(creators)}: {row['Title']}. <a href='https://doi.org/{row['DOI']}'>{row['DOI']}</a></li>"
    print(citationString)
    description = description+citationString
    
description = description+"</ul>"
record["metadata"]["description"]  = description   
#Update existing Draft
newRecord = zenodo.updateRecord(recordId,record)

# #Publish the Zenodo Record
zenodo.publishDraft(recordId)
    
        
#Add Communities
zenodo.addRectoCommunity(recordId, {'communities': [{'id': 'lory'},{'id': 'lory_hslu'},{'id': 'lory_phlu'}]})
