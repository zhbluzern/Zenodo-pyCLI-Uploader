import pandas as pd
import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio
import src.handleCrossRef as CrossRef
import src.handleDataCite as DataCite
import json
import re
from datetime import datetime

#Read a Metadata-Excel-File
data = pd.read_excel(r'hslu_datasets/Zenodo_CutAWAY_KURsamples_00.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns

#df = df[df['zenodoId'].isna()] #filter to _new_ records (which aren't uploaded to Zenodo yoet)
#df = df.iloc[10:11,:] #Montaging
#df = df.iloc[31:32,:] #To all arts
#df = df.iloc[[10, 13, 31], :] #three selected articles as test sample
#df = df.iloc[[9], :]
#df = df.iloc[[2]]
print(df.head())

for index, row in df.iterrows():
    
    # create Zenodo-Record
    zenodo = InvenioRest.Invenio()
    record = zenodo.recordSchema
    zenSearch = ZenodoSearch.ZenodoSearch()

    creators = []
    languages = []
    tags = []
    relatedUrl = []
#     for col in initColumns:
#             #print(col)
#             value = getattr(row, col)  # Get the value of the column in the current row
#             if pd.notna(value):  # Only add the value if it's not NA
#                 if col.startswith('tag_'):
#                     tags.append(value)
#                 elif col.startswith("author_"):
#                     creators.append(value)
#                 elif col.startswith("language_"):
#                     languages.append(value)
#                 elif col.startswith("related_"):
#                     relatedUrl.append(value)
#     #print(tags)

    # Get Metadata form realtedWork-DOI
    doi = re.sub("https://doi.org/","",row.DOI)
    crossref_MD = CrossRef.get_doi_metadata(doi)
    if crossref_MD.get("error"):
        crossref_MD = DataCite.get_doi_metadata(doi)
    
    for creator in crossref_MD["authors"]:
        # creatorDict = {}
        # creatorDict["name"] = creator
        # nameParts = creator.split(", ")
        # creatorDict["family_name"] = nameParts[0]
        # creatorDict["given_name"] = nameParts[1]
        # record["metadata"]["creators"].append(creatorDict)
        record["metadata"]["creators"].append(
            zenodo.setPersonOrOrg(
            name=creator["family_name"]+", "+creator["given_name"],
            splitChar=",",
            persId = creator["orcid"],
            persIdScheme= "orcid", 
            affiliation=creator["affiliation"],
            familyNameFirst=True))

#     if hasattr(row, 'organisation') and pd.notna(row.organisation):
#         record["metadata"]["creators"].append(zenodo.setPersonOrOrg(name=row.organisation, type="organizational"))

    record["metadata"]["title"]=f"{crossref_MD['title']} {row.Title}"
#     titleObject = []
#     titleObject = bnlParser.updateTitleObject(titleObject, row.title, languages[0], True)

#     print(record["metadata"])
    record["metadata"]["resource_type"] ={"id":"dataset"}
    record["metadata"]["publication_date"] = str(crossref_MD["date"])
    record["metadata"]["publisher"] = "Lucerne University of Applied Sciences and Arts, School of Engineering and Architecture"

   
    record["metadata"]["rights"] = [ {"id":"cc-by-4.0"}]
    record["metadata"]["description"] = f"This dataset contains high resolution images of x-ray computed tomography scans as supplementary dataset to the publication: <i>{crossref_MD['title']} ({crossref_MD['date']})</i> DOI:<a href='https://doi.org/{doi}'>{doi}</a>"

#     langDict = { "id" : row.language_01 }
#     record["metadata"]["languages"] = []
#     record["metadata"]["languages"].append(langDict)

    relatedIdentifiers = []
    relatedIdentifiers.append({"identifier":doi, "scheme":"doi", "relation_type": {"id":"issupplementto"}})
    record["metadata"]["related_identifiers"] = relatedIdentifiers

    print(record)
    newRecord = zenodo.createDraft(record)
#     #handleFiles.uploadFile(zenodo,listOfFiles,newRecord,"bnl/Files/")
#     #print(newRecord)

    
#     ### Publish the Zenodo Record
#     #print(zenodo.publishDraft(newRecord["id"]))
    df.at[index, 'ZenodoId'] = str(newRecord["id"])
    
#     ### Add Communities
#     zenodo.addRectoCommunity(newRecord["id"],{"communities":[ {"id":"lory_hslu_t_und_a"}, {"id":"lory"}, {"id":"lory_hslu"}]})
    
#     #break

currentDateStr = datetime.now().strftime("%Y%m%d")    
df.to_excel(f"hslu_datasets/ExportData_{currentDateStr}.xlsx", index=False, engine="openpyxl")
