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
# Am 29.03.2025 wurden für das Journal Draft-Records angelegt
# Es fehlen folgende Metadaten:
# * PublicationDate (aus XLS oder fix implementieren)
# * Communities
# * ggf. Page-Range im imprimt:imprint
# 


#Read a Metadata-Excel-File
data = pd.read_excel(r'Files/Sammelband-ZLLF-Raster.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns
#Define new Columns with explicit dtype for correct export
# df['ZenodoId'] = pd.Series(dtype='str')
# df['DOI'] = pd.Series(dtype='str')
print(df.head())

#Fetch Containing Book Record
zenodo = InvenioRest.Invenio()
book = zenodo.getDraft("15065419")
print(book["metadata"]["creators"])
print(book["metadata"]["title"])
print(book["metadata"]["resource_type"])
print(book["metadata"]["license"])
print(book["doi"])

for index, row in df.iterrows():

    #create Zenodo-Record
    zenodo = InvenioRest.Invenio()
    record = zenodo.recordSchema
    zenSearch = ZenodoSearch.ZenodoSearch()

    creators = []
    creatorsAffil = []
    languages = []
    tags = []
    relatedUrl = []
    for col in initColumns:
            #print(col)
            value = getattr(row, col)  # Get the value of the column in the current row
            if pd.notna(value):  # Only add the value if it's not NA
                if col.startswith('Keywords_'):
                    tags.append(value)
                elif col.startswith("Creator_Author_Affiliation"):
                    creatorsAffil.append(value)                     
                elif col.startswith("Creator_Author_"):
                    creators.append(value)
                # elif col.startswith("Languages_"):
                #     languages.append(value)                
                # elif col.startswith("Relation_"):
                #     relatedUrl.append(value)
    print(tags)
    print(creators)
    print(creatorsAffil)

    for i, creator in enumerate([creator for creator in creators if pd.notna(creator)]):
        record["metadata"]["creators"].append(zenodo.setPersonOrOrg(name=creator,splitChar=",", affiliation=creatorsAffil[i], familyNameFirst=True))

    record["metadata"]["contributors"] = []
    for i, contributor in enumerate(book["metadata"]["creators"]):
        print(contributor["name"])
        if contributor.get("orcid"):
            record["metadata"]["contributors"].append(zenodo.setPersonOrOrg(contributor["name"], affiliation=contributor["affiliation"],
                                                                        splitChar=",", role="editor", familyNameFirst=True,
                                                                        persId=contributor["orcid"],persIdScheme="orcid"))
        else:
            record["metadata"]["contributors"].append(zenodo.setPersonOrOrg(contributor["name"], affiliation=contributor["affiliation"],
                                                                        splitChar=",", role="editor", familyNameFirst=True))

    record["metadata"]["title"]=row.Title
    
    #publicationtype book-chapter
    record["metadata"]["resource_type"] = {"id":"publication-section"}

    record.update({"custom_fields":{"imprint:imprint": {"title":book["metadata"]["title"], "place" : "Luzern", "pages":""}}})
    record["metadata"]["publisher"] = row.Publisher
    record["metadata"]["rights"] = [{"id":row.Licence}]
    record["metadata"]["languages"] = [{"id":row.Languages}]
    record["metadata"]["publication_date"] = "2025"
    subjects = []
    for tag in tags:
        subjects.append({"subject":tag})
    record["metadata"]["subjects"] = subjects

    relatedIdentifiers = []
    #for url in relatedUrl:
    relatedIdentifiers.append({"identifier":"10.5281/zenodo.15065418", "scheme":"doi", "relation_type": {"id":"ispartof"}})
    record["metadata"]["related_identifiers"] = relatedIdentifiers


    print(record)
    
    #Create the Draft
    # newRecord = zenodo.createDraft(record)
    # print(newRecord["id"])
    # df.loc[index, 'ZenodoId'] = str(newRecord["id"])
    # df.loc[index, 'DOI'] = f"10.5281/zenodo.{newRecord['id']}"
    
    #Update existing Draft
    newRecord = zenodo.updateRecord(row.ZenodoId,record)
    
    #Publish the Zenodo Record
    # print(zenodo.publishDraft(row.ZenodoId))
    
    #UploadFiles
    handleFiles.uploadFile(zenodo,[row.File],newRecord,"Files/ZLLF/")

    #Add Communities
    communities = row.Communities.replace('\n\n', '\n').split("\n")
    print(communities)
    #zenodo.addRectoCommunity(row.ZenodoId{"communities":[{"id":"lory_hslu_dfk_bnl"}...

    break

#print(df.head())
currentDateStr = datetime.now().strftime("%Y%m%d")
df.to_excel(f"Files/Sammelband_ZLLF_DOI_{currentDateStr}.xlsx", index=False, engine="openpyxl")