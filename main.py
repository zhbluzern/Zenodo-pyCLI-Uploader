import pandas as pd
import ZenodoRest
import json

#Read a Metadata-Excel-File
#data = pd.read_excel(r'C:\Temp\Nummer11\Nummer 11 - DOIs_ML_bw.xlsx')
data = [{"item":"Q116960807","zenodoId":7418080},{"item":"Q116960808","zenodoId":7418116},{"item":"Q116960809","zenodoId":7418127},{"item":"Q116960810","zenodoId":7418145},{"item":"Q116960811","zenodoId":7418153},{"item":"Q116960812","zenodoId":7418161},{"item":"Q116960813","zenodoId":7418173},{"item":"Q116960814","zenodoId":7418179},{"item":"Q116960815","zenodoId":7418191},{"item":"Q116960816","zenodoId":7418195},{"item":"Q116960817","zenodoId":7418207},{"item":"Q116960818","zenodoId":7418222},{"item":"Q116960819","zenodoId":7418230},{"item":"Q116960820","zenodoId":7418232},{"item":"Q116960821","zenodoId":7418517},{"item":"Q116960822","zenodoId":7418531},{"item":"Q116960823","zenodoId":7418533},{"item":"Q116960824","zenodoId":7418537},{"item":"Q116960825","zenodoId":7418547},{"item":"Q116960826","zenodoId":7418551},{"item":"Q116961010","zenodoId":7417971}]
df = pd.DataFrame(data)

print(df)

#Iterate through xls-File
for row in df.itertuples(index=True, name='Pandas'):
    print(row.zenodoId, row.item)

    #Initialisiere Zenodo-Klasse aufBasis vorhandener Zenodo-ID
    zenodo = ZenodoRest.Zenodo(row.zenodoId)
    
    # Editiere Datensatz
    zenodo.setEdit()

    #Hole Metadaten
    recordData = zenodo.getRecordData()
    
    ## Formatierte Ausgabe des JSON-Recods zur Kontrolle wenn nötig
    #json_formatted_str = json.dumps(recordData, indent=2)
    #print(json_formatted_str)
    
    ## Bearbeite Metadaten

    print(recordData["metadata"]["related_identifiers"])
    newRelId = {}
    newRelId["scheme"] = "url"
    newRelId["identifier"] = f"https://www.wikidata.org/entity/{row.item}"
    newRelId["relation"] = "isDocumentedBy"
    recordData["metadata"]["related_identifiers"].append(newRelId)
    print(recordData["metadata"]["related_identifiers"])

    ## Lade neue Metadaten hoch
    uploadData = zenodo.putRecordData(recordData)
    print(uploadData)


    ## Publish Record
    publishData = zenodo.publishRecord()
    print(publishData)
