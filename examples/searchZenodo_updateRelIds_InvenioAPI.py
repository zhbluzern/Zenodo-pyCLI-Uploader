import src.ZenodoSearch as ZenodoSearch
import src.invenioRest as zenodo

zenodo = zenodo.Invenio()
search = ZenodoSearch.ZenodoSearch()
records = search.searchRecords("communities:lory_unilu_ksf_jgb AND related.relation:isreferencedby")
recCount = 1

while records != []:
    #print(records["links"]["next"])
    for record in records["hits"]["hits"]:
        recordId = record["id"]
        print(f"#{str(recCount)}: {record['id']}")

        zenodo.editRecord(recordId)
        record = zenodo.exportRecord(recordId)
        #print(json.dumps(record["metadata"], indent=1))
        relIdList = []
        for relId in record["metadata"]["related_identifiers"]:
            print(relId)
            if relId["relation_type"]["id"] == "isreferencedby":
                relId["relation_type"]["id"] = "hasmetadata"
                relId["relation_type"].pop("title")
            #print(relId)
            relIdList.append(relId)
        print(relIdList)
        record["metadata"]["related_identifiers"] = relIdList

        print(zenodo.updateRecord(recordId, record))
        print(zenodo.publishDraft(recordId))

        recCount +=1

    if records["links"].get("next"):
        records = search.getRecordsByLinks(records["links"]["next"])
    else:
        records = []

