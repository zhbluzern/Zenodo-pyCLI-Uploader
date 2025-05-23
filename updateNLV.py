import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as zenodo
import pandas as pd
import re

zenodo = zenodo.Invenio()
search = ZenodoSearch.ZenodoSearch()

#Read a Metadata-Excel-File
data = pd.read_excel(r'nlv/Findmittel_202410_Zenodo_Update_20241104.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns

df = df[df['TitleNew'].notna()] #filter to _new_ records (which aren't uploaded to Zenodo yoet)
#print(df.head())

for index, row in df.iterrows():
    #Get the latest Zenodo-Record-ID based on a given DOI
    recordId = zenodo.getLatestRecordIdByDOI(row["DOI"])
    print(recordId)
    print(row["TitleNew"])
    #recordId = "13935021"

    zenodo.editRecord(recordId)
    record = zenodo.exportRecord(recordId)
    record["metadata"]["title"] = row["TitleNew"]
    print(record["metadata"]["description"])
    newDesc = re.sub(row["TitleAlt"],row["TitleNew"],record["metadata"]["description"])
    print(newDesc)
    record["metadata"]["description"] = newDesc
    zenodo.updateRecord(recordId, record)
    print(zenodo.publishDraft(recordId))   
    #break

#df.to_excel("nlv/Findbuecher_202410_LatestId.xlsx", index=False, engine="openpyxl")   