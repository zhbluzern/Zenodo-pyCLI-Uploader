import src.queryWikidata as WDQS
import src.invenioRest as zenodo

query = """SELECT * WHERE {
  ?item wdt:P1433 wd:Q15757483;
    wdt:P4901 ?zenodoId;
        wdt:P953 ?fullWorkUrl.
}"""
results = WDQS.get_results(query)

zenodo = zenodo.Invenio()

for result in results["results"]["bindings"]:
    print(result["zenodoId"]["value"]+": "+result["fullWorkUrl"]["value"])
    recordId = result["zenodoId"]["value"]

    zenodo.editRecord(recordId)
    record = zenodo.exportRecord(recordId)

    relIdList = []
    for relId in record["metadata"]["related_identifiers"]:
        #print(relId)
        if relId["relation_type"]["id"] == "isidenticalto":
            # print(relId)
            relId["identifier"] = result["fullWorkUrl"]["value"]
            # print(relId)
        relIdList.append(relId)
    # print(relIdList)
    record["metadata"]["related_identifiers"] = relIdList

    zenodo.updateRecord(recordId, record)
    print(zenodo.publishDraft(recordId))    
    #break
