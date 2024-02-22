import src.handleAlma as handleAlma
import src.handleFiles as handleFiles
import src.ZenodoRest as ZenodoRest
import src.ZenodoSearch as ZenodoSearch
import re
from datetime import datetime
import json 
import pandas as pd

alma = handleAlma.readAlma()
recs = alma.getRecordsViaSRU(query="alma.all_for_ui=\"*edoc.zhbluzern.ch/*\"")
resultSet = []
for rec in recs:
    resultDet = {}
    #Build the empty deposition metadata dict
    metadata = {"metadata" : {}}
    metadata["metadata"]["upload_type"] = "publication"
    metadata["metadata"]["publication_type"] = "other"
    metadata["metadata"]["publication_date"] = datetime.today().strftime('%Y-%m-%d')
    metadata["metadata"]["imprint_publisher"] = "Zentral- und Hochschulbibliothek Luzern"
    metadata["metadata"]["language"] = "deu"
    metadata["metadata"].update({"creators": [ { "name": "Zentral- und Hochschulbibliothek Luzern", "gnd": "4647881-4"}]})
    metadata["metadata"]["access_right"] = "open"
    metadata["metadata"]["license"] = "cc-by-nc-nd-4.0"

    mmsId_IZ = alma.getMetadataByXpath(rec, ".//slim:controlfield[@tag='001']")
    print(mmsId_IZ[0].text)
    metadata["metadata"]["related_identifiers"] = [{"identifier" : f"https://rzs.swisscovery.slsp.ch/permalink/41SLSP_RZS/lim8q1/alma{mmsId_IZ[0].text}", "relation": "hasMetadata"}]
    resultDet["mmsId_IZ"] = mmsId_IZ[0].text

    mmsId_NZ = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='035']/slim:subfield[@code='a'][starts-with(text(),'(EXLNZ-41SLSP_NETWORK)')]")
    nzID = (re.sub("\(EXLNZ-41SLSP_NETWORK\)","",mmsId_NZ[0].text))
    print(nzID)
    metadata["metadata"]["related_identifiers"].append({"identifier" : f"https://swisscollections.ch/Record/{nzID}", "relation": "hasMetadata"})
    resultDet["mmsId_NZ"] = nzID

    title = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='245']/slim:subfield[@code='a']")
    print(title[0].text)
    metadata["metadata"]["title"] = title[0].text
    description = f"<p>Findbuch zum {title[0].text}</p>"
    resultDet["title"] = title[0].text

    desc = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='520']/slim:subfield[@code='a']")
    print(desc[0].text)
    description = f"{description}<p>Der Nachlass umfasst {desc[0].text}</p>"

    desc = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='541']/slim:subfield[@code='a']")
    if desc != []:
        print(desc[0].text)
        description = f"{description}<p>{desc[0].text}</p>"

    desc = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='555']/slim:subfield[@code='a']")
    if desc != []:
        print(desc[0].text)
        description = f"{description}<p>{desc[0].text}</p>"

    umfang = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='300']/slim:subfield[@code='a']")
    if umfang != []:
        print(f"Umfang: {umfang[0].text}")
        description = f"{description}<p>Umfang: {umfang[0].text}</p>"
    
    metadata["metadata"]["description"]  = description

    #fileUrls = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='856']/slim:subfield[@code='u']")
    files = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='856']")
    for file in files:
        fileUrl = alma.getMetadataByXpath(file,"slim:subfield[@code='u']")
        print(handleFiles.getFileName(fileUrl[0].text))
        #handleFiles.downloadFile(fileUrl[0].text, localPath="nlv/Files")
        fileDesc = alma.getMetadataByXpath(file,"slim:subfield[@code='z']")
        print(fileDesc[0].text)
    
    subjectCreatorNode = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='100']/slim:subfield[@code='4' and text()='cre']/..")
    subjectName = alma.getMetadataByXpath(subjectCreatorNode[0],"slim:subfield[@code='a']")
    print(f"Nachlassbildner: {subjectName[0].text}")
    subjectGND = alma.getMetadataByXpath(subjectCreatorNode[0],"slim:subfield[@code='0']")
    subjectId = ""
    if subjectGND != []:
        print(subjectGND[0].text)
        subjectId = subjectGND[0].text
    metadata["metadata"]["subjects"] = [{"term": subjectName[0].text, "identifier": subjectId}]
    metadata["metadata"]["keywords"] = ["Nachlass", subjectName[0].text]

    #AVA-Information building the invenio-Notes Field:
    ava = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='AVA']")
    standort = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='q']")
    standortDet = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='c']")
    signatur = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='d']")
    print(f"Standort: {standort[0].text} ({standortDet[0].text}), Signatur: {signatur[0].text}")

    metadata["metadata"]["additional_descriptions"] = [{"description": f"Standort: {standort[0].text} ({standortDet[0].text}), Signatur: {signatur[0].text}", "type": { "id": "notes", "title": { "de": "Anmerkungen", "en": "Notes"}}}]

    zenSearch = ZenodoSearch.ZenodoSearch()
    metadata["metadata"]["communities"] = []
    #communityId = zenSearch.getCommunityIdBySlug(slug=communitiy)
    #metadata["metadata"]["communities"].append({"identifier":communityId})   
    metadata["metadata"]["communities"].append({"identifier":"lara_sosa_nlv"})   

    print(json.dumps(metadata,indent=1))

    #Create a new Deposit/Draft
    zenodo = ZenodoRest.Zenodo()
    print(zenodo.ZenodoId)
    resultDet["zenodoId"] = zenodo.ZenodoId
    resultSet.append(resultDet)

    print(zenodo.putRecordData(metadata).text)

    listOfFiles = []
    for file in files:
        fileUrl = alma.getMetadataByXpath(file,"slim:subfield[@code='u']")
        print(handleFiles.getFileName(fileUrl[0].text))
        listOfFiles.append({"key":handleFiles.getFileName(fileUrl[0].text)})
        #handleFiles.downloadFile(fileUrl[0].text, localPath="nlv/Files")
        fileDesc = alma.getMetadataByXpath(file,"slim:subfield[@code='z']")
        print(fileDesc[0].text)

    for filename in listOfFiles:
        print(filename)
        #Upload the File to the Draft
        print(zenodo.uploadFile(filename["key"],"nlv/Files/").text)
    
    #Publish the File
    print(zenodo.publishRecord())


    #Search for alle Requests by the new Record-ID
    zenRequ = zenodo.searchRequests(f"topic.record:{zenodo.ZenodoId}")
    results = (zenRequ.json())
    
    for hit in results["hits"]["hits"]:
        print(hit["id"])
        print(hit["type"])
        #print(hit["links"]["actions"]["accept"])
        print(zenodo.acceptRequest(hit["id"]).text)
    #break

df = pd.DataFrame.from_dict(resultSet)
df.to_excel("nlv/Output.xlsx", index=False, engine="openpyxl")