import pandas as pd
import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio
from datetime import datetime


import json
import re
from datetime import datetime

#Read a Metadata-Excel-File
data = pd.read_excel(r'RoRa/draft.xlsx',  header=0)
df = pd.DataFrame(data)
initColumns = df.columns

#print(df.head())

for index, row in df.iterrows():
    
    #create Zenodo-Record
    zenodo = InvenioRest.Invenio()
    record = zenodo.recordSchema
    zenSearch = ZenodoSearch.ZenodoSearch()

#    https://inveniordm.docs.cern.ch/reference/metadata/#description-0-1


    # TITLE, DESCRIPTION, LANGUAGE
    record["metadata"]["title"] = "TESTING: "+row["Title"]
    record["metadata"]["description"] = row["Description / Abstract"]
    record["metadata"]["languages"] = [{"id":row["Languages"].strip()}]
    
    #  ADDITIONAL NOTES / DESCRIPTIONS
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
    
       
        
    # LICENSE, PUBLISHER, VERSION
    #record["metadata"]["rights"] = [{"id": row["License"]}]
    record["metadata"]["rights"] = [ {"id":"cc-by-4.0"}]
    record["metadata"]["publisher"] = row["Publisher"]
  #  record["metadata"]["version"] = row["Version"]

    # RESOURCE TYPE
    #  record["metadata"]["resource_type"] = {"id":row["Resource Type"]}
     # record["metadata"]["publication_type"] = {"id":"publication-article"}
    record["metadata"]["resource_type"] = {"id":"publication-conferencepaper"}
    
    creators = []
    creatorNames = []
    creatorFamilyNames = []
    creatorAffiliations = []    
    
    contributors = []
    contributorNames = []
    contributorFamilyNames = []
    contributorAffiliations = []
    contributorRoles = []
    
    relations = []
    relationNames = []
    relationProperties = []
    
   # languages = []
    tags = []
    subjects = []
    relatedUrl = []
    for col in initColumns:
            value = getattr(row, col)  # Get the value of the column in the current row
            if pd.notna(value):  # Only add the value if it's not NA
                value = str(value).strip()
                if col.startswith('tag_'):
                    tags.append(value)
              
                # SUBJECTS
                elif col.startswith("Keywords_"):
                    subjects.append({"subject":value})
                    
                # RELATIONS
                elif col.startswith("Relation_"):
                    relationNames.append(value.strip())                
                elif col.startswith("RelationProperty_"):
                    relationProperties.append(value.strip().lower())
                
                # CREATORS
                elif col.startswith("Creator_Author_FirstName_"):
                   creatorNames.append(value.strip())
                elif col.startswith("Creator_Author_LastName_"):
                    creatorFamilyNames.append(value.strip())
                elif col.startswith("Creator_Author_Affiliation_"):
                    creatorAffiliations.append(value.strip())
                
                # CONTRIBUTORS
                elif col.startswith("Contributor_Name_"):
                   contributorNames.append(value.strip())
                elif col.startswith("Contributor_FamilyName_"):
                    contributorFamilyNames.append(value.strip())
                elif col.startswith("Contributor_Affiliation_"):
                    contributorAffiliations.append(value.strip())
                elif col.startswith("Contributor_Role_"):
                    contributorRoles.append(value.strip().lower())

    # CREATORS
    for cn_i, cn in enumerate(creatorNames):
        creators.append(
            {
                "name": cn, 
                "family_name": creatorFamilyNames[cn_i],
                "affiliation": creatorAffiliations[cn_i]
            }
        )
    
    for creator in creators:
        creatorName = creator["name"] + ";" + creator["family_name"]
        record["metadata"]["creators"].append(zenodo.setPersonOrOrg(
            name=creatorName,
            splitChar=";",
            familyNameFirst=False,
            affiliation=creator["affiliation"]
    ))
        
    # creatorName = row['Creator_Author_Name_01'] +";"+ row['Creator_Author_FamilyName_01']
    # record["metadata"]["creators"].append(zenodo.setPersonOrOrg(
    #     name=creatorName,
    #     splitChar=";",
    #     familyNameFirst=False,
    #     affiliation=row['Creator_Author_Affiliation_01'].strip()
    # ))
        
    # CONTRIBUTORS
    record["metadata"]["contributors"] = []
    
    for con_i, con in enumerate(contributorNames):
        contributors.append(
            {
                "name": con, 
                "family_name": contributorFamilyNames[con_i],
                "affiliation": contributorAffiliations[con_i],
                "role": contributorRoles[con_i]
            }
        )
    
    
    for contributor in contributors:
        contributorName = contributor["name"] + ";" + contributor["family_name"]
        record["metadata"]["contributors"].append(zenodo.setPersonOrOrg(
            name=contributorName,
            splitChar=";",
            familyNameFirst=False,
            affiliation=contributor["affiliation"],
            role=contributor["role"]        
    ))
    
    # contributorName = row['Contributor_Name_01'] +";"+ row['Contributor_FamilyName_01']
    # record["metadata"]["contributors"].append(zenodo.setPersonOrOrg(
    #     name=creatorName,
    #     splitChar=";",
    #     familyNameFirst=False,
    #     affiliation=row['Contributor_Affiliation_01'].strip(),
    #     role={"id":row['Contributor_Role_01'].strip().lower()}
    # ))

    
    # RELATIONS
    record["metadata"]["related_identifiers"] = []
    for rel_i, rel in enumerate(relationNames):
        relations.append(
            {
                "identifier": rel,
                "relation_type": {"id": relationProperties[rel_i]},
                "resource_type": {"id": "publication-conferenceproceeding"},
                "scheme": "doi"
            }
        )
    
    for relation in relations:
        record["metadata"]["related_identifiers"].append(relation)    
    
    # SUBJECTS
    record["metadata"]["subjects"] = subjects
    
    # CONFERENCE
    meeting = {}
    meeting["title"] = row['Conference Title'].strip()
    meeting["acronym"] = row['Conference Acronym'].strip()
    meeting["dates"] = row['Conference Dates'].strip()
    meeting["place"] = row['Conference Place'].strip()
    meeting["url"] = row['Conference Website'].strip()

    # Ensure meeting["url"] starts with http:// or https://
    if not re.match(r'^https?://', meeting["url"]):
        meeting["url"] = "https://" + meeting["url"].lstrip('/')

    meeting["session"] = row['Conference Session'].strip()
    meeting["session_part"] = row['Conference Part'].strip()

    record.update({"custom_fields":{"meeting:meeting": meeting}})
    
    #record.update({"prereserve_doi" : True})

    # PUBLICATION DATE
    record["metadata"]["publication_date"] = str(row["Publication date"])[:10]

   # print(record["metadata"])
    
    record["metadata"]["communities"] = [{"identifier": "lara"}]
    

    newRecord = zenodo.createDraft(record)
   # print(zenodo.addRectoCommunity(newRecord["id"], {"communities": [{"id": "lory"}]}))

    # listOfFiles = []
    # print(row["File"])
    # listOfFiles.append(row["File"])
    # handleFiles.uploadFile(zenodo,listOfFiles,newRecord,"EFCF/files/")

    print(newRecord)
    
    prefixSandbox = "10.5072/zenodo."
    prefixProd = "10.5281/zenodo."

    df.at[index, "ZenodoId"] = str(newRecord["id"])
    df.at[index, "ZenodoConceptId"] = str(newRecord["conceptrecid"])
    df.at[index, "ConceptDOI (Sandbox)"] = prefixSandbox+str(newRecord["conceptrecid"])
    df.at[index, "ConceptDOI (Prod)"] = prefixProd+str(newRecord["conceptrecid"])   
     
    df.at[index, "DOI (Sandbox)"] = prefixSandbox+str(newRecord["id"])
    df.at[index, "DOI (Prod)"] = prefixProd+str(newRecord["id"])


timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
df.to_excel(f"RoRa/drafted_{timestamp}.xlsx", index=False, engine="openpyxl")
df.to_excel("RoRa/drafted.xlsx", index=False, engine="openpyxl")