import pandas as pd
import ZenodoRest
import src.readDocx as docx
import json

#Read a Metadata-Excel-File
data = pd.read_excel(r'hslu_sa/ImportData.xlsx', skiprows=[1])
df = pd.DataFrame(data)

print(df.head())

#Initialize ZenodoSearch
zenSearch = ZenodoRest.ZenodoSearch()

df["zenodoId"] = None
#Iterate through xls-File
#Iterate through xls-File
for row in df.itertuples(index=True, name='Pandas'):
    #Build the empty deposition metadata dict
    metadata = {"metadata" : {}}

    #Fetch the metdata
    #List of Creators
    creators = row.creators.replace('\n\n', '\n').split("\n")
    metadata["metadata"].update({"creators": []})
    for creator in creators:
        creatorDict = {}
        creatorDict["name"] = creator
        creatorDict["affiliation"] = "Hochschule Luzern – Soziale Arbeit"
        #nameParts = creator.split(", ")
        #creatorDict["family_name"] = nameParts[0]
        #creatorDict["given_name"] = nameParts[1]
        metadata["metadata"]["creators"].append(creatorDict)
    
    #Abstract - Description
    if row.description.endswith(".docx") == True:
        descriptionTxt = docx.get_docx_text(f"hslu_sa/Files/{row.description}")
    elif row.description.endswith(".txt") == True:
        txtF = open(f"hslu_sa/Files/{row.description}", encoding="utf8")
        descriptionTxt = txtF.read()
    else:
        descriptionTxt = row.description
    #print(descriptionTxt)
    metadata["metadata"].update({"description": descriptionTxt})
    
    #Title
    metadata["metadata"]["title"] = row.title

    #additional_descriptions
    addDesc = {"description": row.additional_descriptions, "type": {"id":"notes", "title": {"de":"Anmerkungen", "en":"Notes"}}}
    metadata["metadata"].update({"additional_descriptions": []})
    metadata["metadata"]["additional_descriptions"].append(addDesc)
    
    #publicationDate, publisher
    metadata["metadata"]["publication_date"] = row.publication_date.strftime("%Y-%m-%d")
    metadata["metadata"]["imprint_publisher"] = row.publisher

    #metadata["metadata"]["resource_type"] = ({"id": row.resource_type, "title": {"de":"Bericht","en":"Report"}})
    if row.resource_type == "publication-report":
        metadata["metadata"]["upload_type"] = "publication"
        metadata["metadata"]["publication_type"] = "report"
    elif row.resource_type == "publication-thesis":
        metadata["metadata"]["upload_type"] = "publication"
        metadata["metadata"]["publication_type"] = "thesis"  
        metadata["metadata"]["thesis_university"] = "Hochschule Luzern – Soziale Arbeit"   
    
    metadata["metadata"]["access_right"] = "open"
    metadata["metadata"]["license"] = "cc-by-nc-nd-4.0"

    communities = row.communities.split("\n")
    metadata["metadata"]["communities"] = []
    communityRequestCounter = 0
    for communitiy in communities:
        communityId = zenSearch.getCommunityIdBySlug(slug=communitiy)
        #metadata["metadata"]["communities"].append({"identifier":communityId})   
        metadata["metadata"]["communities"].append({"identifier":communitiy})   
        communityRequestCounter += 1
    #print( metadata["metadata"]["communities"])
    #print(json.dumps(metadata, sort_keys=True, indent=4))
    
    #Create a new Draft Record
    zenodo = ZenodoRest.Zenodo()
    print(zenodo.ZenodoId)
    df.at[row.Index, 'zenodoId'] = zenodo.ZenodoId
    #Upload the Metadata to the Draft
    print(zenodo.putRecordData(metadata).text)
    #Upload the File to the Draft
    print(zenodo.uploadFile(row.files,"hslu_sa/Files/").text)
    #Publish the File
    print(zenodo.publishRecord())


    #Accept the Communitie-Requests
    #Search for alle Requests by the new Record-ID
    zenRequ = zenodo.searchRequests(f"topic.record:{zenodo.ZenodoId}")
    results = (zenRequ.json())
    
    #Es dürfen nur soviele Requests wie Communities vorliegen, sonst ist was faul.
    if (len(results["hits"]["hits"])) == communityRequestCounter:
        for hit in results["hits"]["hits"]:
            print(hit["id"])
            print(hit["type"])
            #print(hit["links"]["actions"]["accept"])
            print(zenodo.acceptRequest(hit["id"]).text)
    
    #OutPut Dataframe enriched with DOI
    df.to_excel("hslu_sa/ExportData.xlsx", index=False, engine="openpyxl")
    #break