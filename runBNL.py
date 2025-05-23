import pandas as pd
import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio
import bnl.bnlParser as bnlParser
import json
import re
from datetime import datetime

#Read a Metadata-Excel-File
data = pd.read_excel(r'bnl/BNL_Liste_20241017.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns

df = df[df['zenodoId'].isna()] #filter to _new_ records (which aren't uploaded to Zenodo yoet)
#df = df.iloc[10:11,:] #Montaging
#df = df.iloc[31:32,:] #To all arts
#df = df.iloc[[10, 13, 31], :] #three selected articles as test sample
#df = df.iloc[[9], :]
#print(df.head())

for index, row in df.iterrows():
    
    #create Zenodo-Record
    zenodo = InvenioRest.Invenio()
    record = zenodo.recordSchema
    zenSearch = ZenodoSearch.ZenodoSearch()

    creators = []
    languages = []
    tags = []
    relatedUrl = []
    for col in initColumns:
            #print(col)
            value = getattr(row, col)  # Get the value of the column in the current row
            if pd.notna(value):  # Only add the value if it's not NA
                if col.startswith('tag_'):
                    tags.append(value)
                elif col.startswith("author_"):
                    creators.append(value)
                elif col.startswith("language_"):
                    languages.append(value)
                elif col.startswith("related_"):
                    relatedUrl.append(value)
    #print(tags)

    #Fetch language dependend data (pdf, title)
    articleHtml = bnlParser.getHTML(row.articleUrl)
    listOfFiles =  []
    for lang in [lang for lang in languages]:
        #download pdfFiles for each given lang
        pdfUrl = bnlParser.getPDF(articleHtml,lang)
        print(f"https://brand-new-life.org{pdfUrl[0]}")
        handleFiles.downloadFile(f"https://brand-new-life.org{pdfUrl[0]}", "bnl/Files", pdfUrl[1])
        listOfFiles.append(f"bnl/Files/{pdfUrl[1]}")

    for creator in [creator for creator in creators if pd.notna(creator)]:
        # creatorDict = {}
        # creatorDict["name"] = creator
        # nameParts = creator.split(", ")
        # creatorDict["family_name"] = nameParts[0]
        # creatorDict["given_name"] = nameParts[1]
        # record["metadata"]["creators"].append(creatorDict)
        record["metadata"]["creators"].append(zenodo.setPersonOrOrg(name=creator,splitChar=",",familyNameFirst=True))
    
    if hasattr(row, 'organisation') and pd.notna(row.organisation):
        record["metadata"]["creators"].append(zenodo.setPersonOrOrg(name=row.organisation, type="organizational"))

    record["metadata"]["title"]=row.title
    titleObject = []
    titleObject = bnlParser.updateTitleObject(titleObject, row.title, languages[0], True)
    additional_titles = []
    if len(languages)>1:
        # Fetch alternative titles
        langUrl = bnlParser.getLangLinks(articleHtml, lang)
        articleHtml = bnlParser.getHTML(langUrl["href"])
        title = bnlParser.getTitle(articleHtml)
        titleObject = bnlParser.updateTitleObject(titleObject, title.strip(), lang)
        
    subtitle = bnlParser.getSubTitle(articleHtml)
    if subtitle != None:
        additional_titles.append({"title": subtitle, "type": {"id": "subtitle"}})
    
    for altTitle in [altTitle for altTitle in titleObject if altTitle["mainTitle"] == False]:
        additional_titles.append({"title": altTitle["title"], "type": {"id": "alternative-title"}, "lang": bnlParser.langIsoHelper(altTitle["lang"])})
    if additional_titles != []:
        record["metadata"]["additional_titles"] = additional_titles
    print(record["metadata"])
    record["metadata"]["resource_type"] ={"id":"publication-article"}
    record["metadata"]["publication_date"] = row.publicationDate[:10]
    record["metadata"]["languages"] = []
    record["metadata"]["publisher"] = "Brand New Life"
    record.update({"custom_fields":{"journal:journal": {"title":"Brand New Life", "issn" : "2297-9220"}}})
    record["metadata"]["rights"] = [ {"id":"cc-by-nc-nd-4.0"},{"title":{"en": "Other for images"},"description": {"en": "Free for private use; right holder retains other rights, including distribution"}}]
    for lang in [lang for lang in languages if pd.notna(lang)]:
        langDict = bnlParser.langIsoHelper(lang)
        record["metadata"]["languages"].append(langDict)
    
    relatedIdentifiers = []
    getAllLangUrls = bnlParser.getAllLangLinks(articleHtml)
    for url in getAllLangUrls:
        relatedIdentifiers.append({"identifier":url, "scheme":"url", "relation_type": {"id":"isidenticalto"}})
    for url in relatedUrl:
        relatedIdentifiers.append({"identifier":url, "scheme":"url", "relation_type": {"id":"issupplementedby"}})
    record["metadata"]["related_identifiers"] = relatedIdentifiers

    subjects = []
    for tag in tags:
        subjects.append({"subject":tag})
    record["metadata"]["subjects"] = subjects

    record["metadata"]["description"] = bnlParser.getSummary(articleHtml)

    print(record)
    
    newRecord = zenodo.createDraft(record)
    handleFiles.uploadFile(zenodo,listOfFiles,newRecord,"bnl/Files/")
    print(newRecord)
    #break
    
    ### Publish the Zenodo Record
    print(zenodo.publishDraft(newRecord["id"]))
    df.at[index, 'ZenodoId'] = str(newRecord["id"])
    
    ### Add Communities
    zenodo.addRectoCommunity(newRecord["id"],{"communities":[{"id":"lory_hslu_dfk_bnl"}, {"id":"lory"}, {"id":"lory_hslu"}, {"id":"lory_hslu_d_und_k"}]})
    
    #break

currentDateStr = datetime.now().strftime("%Y%m%d")    
df.to_excel(f"bnl/ExportData_{currentDateStr}.xlsx", index=False, engine="openpyxl")
