import src.handleAlma as handleAlma
import src.handleFiles as handleFiles
import src.invenioRest as InvenioRest
import pandas as pd
from datetime import datetime
import re

data = pd.read_excel(r'nlv/Findbuecher_202410_Zenodo.xlsx')
df = pd.DataFrame(data)
df = df.astype('string')

alma = handleAlma.readAlma()
#df = df.iloc[[6],:]

for index, row in df.iterrows():
    if pd.notna(row.ZenodoId):
        print(f"{row.mmsID} already uploaded as row.ZenodoId")
    else:
        print(f"upload {row.mmsID} to Zenodo")
        rec = alma.getRecordsViaSRU(query=f"rec.id={row.mmsID}")
        zenodo = InvenioRest.Invenio()
        zenodo.resetRecord()
        record = zenodo.recordSchema
        record["metadata"]["resource_type"] = {"id":"publication-other"}
        record["metadata"]["publication_date"] = datetime.today().strftime('%Y-%m-%d')
        record["metadata"]["publisher"] = "Zentral- und Hochschulbibliothek Luzern"
        record["metadata"]["languages"] = [{"id":"deu"}]
        creator = zenodo.setPersonOrOrg("Zentral- und Hochschulbibliothek Luzern",type="organizational", persId="4647881-4", persIdScheme="gnd")
        record["metadata"]["creators"].append(creator)
        record["metadata"]["rights"] = [{"id": "cc-by-4.0"}]
        record["metadata"]["title"] = row.title
        description = f"<p>{row.title}</p>"

        record["metadata"]["related_identifiers"] = []
        record["metadata"]["related_identifiers"].append({"identifier" : f"https://rzs.swisscovery.slsp.ch/permalink/41SLSP_RZS/lim8q1/alma{row.mmsID}", "relation_type": {"id": "hasmetadata"}, "scheme": "url"})
        mmsId_NZ = alma.getMetadataByXpath(rec[0], ".//slim:datafield[@tag='035']/slim:subfield[@code='a'][starts-with(text(),'(EXLNZ-41SLSP_NETWORK)')]")
        nzID = (re.sub("\(EXLNZ-41SLSP_NETWORK\)","",mmsId_NZ[0].text))
        record["metadata"]["related_identifiers"].append({"identifier" : f"https://swisscollections.ch/Record/{nzID}", "relation_type": {"id": "hasmetadata"}, "scheme": "url"})

        desc = alma.getMetadataByXpath(rec[0], ".//slim:datafield[@tag='520']/slim:subfield[@code='a']")
        if desc != []:
            print(desc[0].text)
            description = f"{description}<p>Der Nachlass umfasst {desc[0].text}</p>"
        
        desc = alma.getMetadataByXpath(rec[0], ".//slim:datafield[@tag='541']/slim:subfield[@code='a']")
        if desc != []:
            print(desc[0].text)
            description = f"{description}<p>{desc[0].text}</p>"

        desc = alma.getMetadataByXpath(rec[0], ".//slim:datafield[@tag='555']/slim:subfield[@code='a']")
        if desc != []:
            print(desc[0].text)
            description = f"{description}<p>{desc[0].text}</p>"

        umfang = alma.getMetadataByXpath(rec[0], ".//slim:datafield[@tag='300']/slim:subfield[@code='a']")
        if umfang != []:
            print(f"Umfang: {umfang[0].text}")
            description = f"{description}<p>Umfang: {umfang[0].text}</p>"
        
        record["metadata"]["description"]  = description   

        subjectCreatorNode = alma.getMetadataByXpath(rec[0], ".//slim:datafield[@tag='100']/slim:subfield[@code='4' and text()='cre']/..")
        subjectName = alma.getMetadataByXpath(subjectCreatorNode[0],"slim:subfield[@code='a']")
        print(f"Nachlassbildner: {subjectName[0].text}")
        subjectGND = alma.getMetadataByXpath(subjectCreatorNode[0],"slim:subfield[@code='0']")
        subjectId = ""
        if subjectGND != []:
            print(subjectGND[0].text)
            subjectId = re.sub("\(DE-588\)","",subjectGND[0].text)
        record["metadata"]["contributors"] = []
        contrib = zenodo.setPersonOrOrg(name=subjectName[0].text, splitChar=", ", persId=subjectId, persIdScheme="gnd", role="other")
        record["metadata"]["contributors"].append(contrib)
        #print(contrib)
        record["metadata"]["subjects"] = [{"subject": "Nachlass"}, {"subject":subjectName[0].text}]

        #AVA-Information building the invenio-Notes Field:
        ava = alma.getMetadataByXpath(rec[0], ".//slim:datafield[@tag='AVA']")
        standort = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='q']")
        standortDet = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='c']")
        signatur = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='d']")
        print(f"Standort: {standort[0].text} ({standortDet[0].text}), Signatur: {signatur[0].text}")
        addDescription = f"Standort: {standort[0].text} ({standortDet[0].text}), Signatur: {signatur[0].text}"
        record["metadata"]["additional_descriptions"] = [{"description": addDescription, "type": { "id": "notes"}, "lang":{"id":"deu"}}]
        
        print(record)
        
        #Create the Draft
        newRecord = zenodo.createDraft(record)
        print(newRecord)
        #break
        #Handle the files
        listOfFiles = []
        listOfFiles.append(row.fileName)
        print(listOfFiles)
        handleFiles.uploadFile(zenodo,listOfFiles,newRecord,"nlv/Files")
        
        ### Publish the Zenodo Record
        print(zenodo.publishDraft(newRecord["id"]))
        zenodo.addRectoCommunity(newRecord["id"],{"communities":[{"id":"lara_sosa_nlv"}]})

        df.at[index, "ZenodoId"] = str(newRecord["id"])
        #break
df.to_excel("nlv/Findbuecher_202410_Zenodo_Update.xlsx", index=False, engine="openpyxl")