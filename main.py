import pandas as pd
import ZenodoRest
import json

#Read a Metadata-Excel-File
data = pd.read_excel(r'C:\Temp\Nummer11\Nummer 11 - DOIs_ML_bw.xlsx')
df = pd.DataFrame(data)

#print(df)

#Iterate through xls-File
for row in df.itertuples(index=True, name='Pandas'):
    print(row.ZenodoID, row.AutorInnen, row.DateiPfad, row.Datei, row.Titel)

    #Initialisiere Zenodo-Klasse aufBasis vorhandener Zenodo-ID
    zenodo = ZenodoRest.Zenodo(row.ZenodoID)
    
    #FileUpload
    uploadData = zenodo.uploadFile(row.Datei, row.DateiPfad)
    print(uploadData)

    #Hole Metadaten
    recordData = zenodo.getRecordData()
    
    ## Formatierte Ausgabe des JSON-Recods zur Kontrolle wenn nötig
    #json_formatted_str = json.dumps(recordData, indent=2)
    #print(json_formatted_str)
    
    ## Bearbeite Metadaten
    recordDataNew = recordData
    recordDataNew["metadata"]["publication_date"] = "2023-03-01"
    recordDataNew["metadata"]["title"] = row.Titel
    recordDataNew["metadata"]["language"] = row.language

    relIdsNew = []
    for relIds in recordData["metadata"]["related_identifiers"]:
        if relIds["relation"] == "isPublishedIn":
            if relIds["identifier"] != row.isPublishedIn:
                relIds["identifier"]  = row.isPublishedIn
        relIdsNew.append(relIds)
    recordDataNew["metadata"]["related_identifiers"] = relIdsNew

    ## Lade neue Metadaten hoch
    uploadData = zenodo.putRecordData(recordDataNew)
    print(uploadData)


    ## Publish Record
    publishData = zenodo.publishRecord()
    print(publishData)
