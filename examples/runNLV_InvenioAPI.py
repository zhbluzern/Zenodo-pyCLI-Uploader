## ******************************************************************
## Dieses Skript erzeugt Datensätze in Zenodo mit Zugriff
## über die "neue" InvenioRDM-REST-API (https://inveniordm.docs.cern.ch/reference/rest_api_index/)
##
## 2024-02: Die InvenioRDM-REST-API erlaubt noch _keine_ Ergänzung von 
## Records zu Communities.
##

import src.handleAlma as handleAlma
import src.handleFiles as handleFiles
import src.invenioRest as zenodo
import src.ZenodoSearch as ZenodoSearch
import re
from datetime import datetime
import json 

zenodo = zenodo.Invenio()
alma = handleAlma.readAlma()
recs = alma.getRecordsViaSRU(query="alma.all_for_ui=\"*edoc.zhbluzern.ch/*\"")
for rec in recs:
    zenodo.resetRecord()
    zenodo.recordSchema["metadata"]["resource_type"] = {"id":"publication-other"}
    zenodo.recordSchema["metadata"]["publication_date"] = datetime.today().strftime('%Y-%m-%d')
    zenodo.recordSchema["metadata"]["publisher"] = "Zentral- und Hochschulbibliothek Luzern"
    zenodo.recordSchema["metadata"]["languages"] = [{"id":"deu"}]
    creator = zenodo.setPersonOrOrg("Zentral- und Hochschulbibliothek Luzern",type="organizational", persId="4647881-4", persIdScheme="gnd")
    zenodo.recordSchema["metadata"]["creators"].append(creator)
    zenodo.recordSchema["metadata"]["rights"] = [{"id": "cc-by-4.0","icon": "cc-by-icon", "title": {"en": "Creative Commons Attribution 4.0 International"}, "description": {"en": "The Creative Commons Attribution license allows re-distribution and re-use of a licensed work on the condition that the creator is appropriately credited."}, "link": "https://creativecommons.org/licenses/by/4.0/"}]

    mmsId_IZ = alma.getMetadataByXpath(rec, ".//slim:controlfield[@tag='001']")
    print(mmsId_IZ[0].text)
    zenodo.recordSchema["metadata"]["related_identifiers"] = [{"identifier" : f"https://rzs.swisscovery.slsp.ch/permalink/41SLSP_RZS/lim8q1/alma{mmsId_IZ[0].text}", "relation_type": {"id": "hasmetadata", "title": {"de": "Hat Metadaten in","en": "Has metadata"}}, "scheme": "url"}]

    mmsId_NZ = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='035']/slim:subfield[@code='a'][starts-with(text(),'(EXLNZ-41SLSP_NETWORK)')]")
    nzID = (re.sub("\(EXLNZ-41SLSP_NETWORK\)","",mmsId_NZ[0].text))
    print(nzID)
    zenodo.recordSchema["metadata"]["related_identifiers"].append({"identifier" : f"https://swisscollections.ch/Record/{nzID}", "relation_type": {"id": "hasmetadata", "title": {"de": "Hat Metadaten in","en": "Has metadata"}}, "scheme": "url"})

    title = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='245']/slim:subfield[@code='a']")
    print(title[0].text)
    zenodo.recordSchema["metadata"]["title"] = title[0].text
    description = f"<p>Findbuch zum {title[0].text}</p>"

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
        description = f"{description}<p>{desc[0].text}</p>"
    
    zenodo.recordSchema["metadata"]["description"]  = description

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
    zenodo.recordSchema["metadata"]["contributors"] = []
    contrib = zenodo.setPersonOrOrg(name=subjectName[0].text, splitChar=", ", persId=subjectId, persIdScheme="GND", role="other")
    zenodo.recordSchema["metadata"]["contributors"].append(contrib)
    zenodo.recordSchema["metadata"]["subjects"] = [{"subject": "Nachlass"}, {"subject":subjectName[0].text}]

    #AVA-Information building the invenio-Notes Field:
    ava = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='AVA']")
    standort = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='q']")
    standortDet = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='c']")
    signatur = alma.getMetadataByXpath(ava[0], "slim:subfield[@code='d']")
    print(f"Standort: {standort[0].text} ({standortDet[0].text}), Signatur: {signatur[0].text}")

    zenodo.recordSchema["metadata"]["additional_descriptions"] = [{"description": f"Standort: {standort[0].text} ({standortDet[0].text}), Signatur: {signatur[0].text}", "type": { "id": "notes", "title": { "de": "Anmerkungen", "en": "Notes"}}}]

    zenSearch = ZenodoSearch.ZenodoSearch()
    zenodo.recordSchema["metadata"]["communities"] = []
    communityId = zenSearch.getCommunityIdBySlug(slug="lara_sosa_nlv")
    zenodo.recordSchema["metadata"]["communities"].append({"identifier":communityId})   
    #zenodo.recordSchema["metadata"]["communities"].append({"identifier":"lara_sosa_nlv"})   
    print(json.dumps(zenodo.recordSchema,indent=1))

    newRecord = zenodo.createDraft(zenodo.recordSchema)
    print(newRecord)
    print(f"ID: {newRecord['id']}")

    listOfFiles = []
    for file in files:
        fileUrl = alma.getMetadataByXpath(file,"slim:subfield[@code='u']")
        print(handleFiles.getFileName(fileUrl[0].text))
        listOfFiles.append({"key":handleFiles.getFileName(fileUrl[0].text)})
        #handleFiles.downloadFile(fileUrl[0].text, localPath="nlv/Files")
        fileDesc = alma.getMetadataByXpath(file,"slim:subfield[@code='z']")
        print(fileDesc[0].text)

    fileDraft = zenodo.startDraftFiles(newRecord["id"], data=listOfFiles)
    print(fileDraft)
    for filename in listOfFiles:
        with open(f"nlv/Files/{filename['key']}", 'rb') as f:
            data = f.read()
        fileUpload = zenodo.uploadFileContent(newRecord["id"], fileName=filename["key"], fileContent=data)
        #print(fileUpload)
        print(zenodo.commitFileUpload(newRecord["id"], fileName=filename["key"]))
    print(zenodo.publishDraft(newRecord["id"]))

    #Search for alle Requests by the new Record-ID
    zenRequ = zenodo.searchRequests(f"topic.record:{newRecord['id']}")
    results = (zenRequ.json())
    
    for hit in results["hits"]["hits"]:
        print(hit["id"])
        print(hit["type"])
        #print(hit["links"]["actions"]["accept"])
        print(zenodo.acceptRequest(hit["id"]).text)
    break