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
book = zenodo.exportRecord("15065419")
# print(book["metadata"]["creators"])
# print(book["metadata"]["title"])
# print(book["metadata"]["resource_type"])
# print(book["metadata"]["rights"])


for index, row in df.iloc[3:4].iterrows():

    #Initialize Zenodo-Classes
    zenodo = InvenioRest.Invenio()
    zenSearch = ZenodoSearch.ZenodoSearch()

    # create Zenodo-Record
    # record = zenodo.recordSchema
    # get existing Draft Recod for Editing
    record = zenodo.editRecord(row["ZenodoId"])
    # record = zenodo.exportRecord(row["ZenodoId"])
    # print(record)
    
    print(f"Record {row['ZenodoId']} upload {row['File']}")
    
    #UploadFiles
    handleFiles.uploadFile(zenodo,[row.File],row["ZenodoId"],"Files/ZLLF/")
    

    #Publish the Zenodo Record
    print(zenodo.publishDraft(row["ZenodoId"]))
    
    #break