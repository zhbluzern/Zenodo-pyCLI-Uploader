import requests
import ZenodoRest
import json

# ###########################################################################
# Dieses Beispiel ändert Communities in Zenodo auf Basis einer
# vorangehenden REST-API-Abfrage
#
# Gesucht werden Datensätze die eine ISBN-Nummer im Format einer ISSN.
# ###########################################################################

#Zu beabeitende Datensätze über Rest-API holen
#Grösse des Ergebnisset beachten (SIZE Parameter anpassen oder Iteration über next-Key)
query = "imprint.isbn:/[0-9]{4}-[0-9]{3}[0-9X]{1}/ AND communities:lory* resource_type.subtype:article"
response = requests.get('https://zenodo.org/api/records',
                        params={'q': query, 'size':200})
records = response.json()

#Iteration durch das Ergebnisset 
#Metadaten-Bearbeitung durchführen
for record in records["hits"]["hits"]:
    recordId = record["id"]
    #recordId = "61717"
    print(recordId)

    #Initialisiere Zenodo-Klasse aufBasis vorhandener Zenodo-ID
    zenodo = ZenodoRest.Zenodo(recordId)
    recordData = zenodo.getRecordData()
    print(recordData)
    json_formatted_str = json.dumps(recordData["metadata"], indent=2)
    print(json_formatted_str)

    #ISSN aus dem Imprint-ISBN holen
    #print(recordData["metadata"])
    issn = recordData["metadata"]["imprint_isbn"]
    print(issn)
    #ISBN-Feld löschen
    recordData["metadata"].pop("imprint_isbn")

    #Related Identifiers Feld holen, wenn nicht vorhanden, leere Liste erzeugen
    try:
        relatedIdentifiers = recordData["metadata"]["related_identifiers"]
    except KeyError:
        relatedIdentifiers = []

    #Neue Realted ID "ISSN" erzeugen:
    #{"scheme": "issn", "identifier": "{Hier die ISSN}",  "relation": "isPublishedIn" }
      
    newRelatedID = {}
    newRelatedID["scheme"] = "issn"
    newRelatedID["identifier"] = issn
    newRelatedID["relation"] = "isPublishedIn"
    relatedIdentifiers.append(newRelatedID)
    print(relatedIdentifiers)
    recordData["metadata"]["related_identifiers"] = relatedIdentifiers


    #Datensatz editieren
    zenodo.setEdit()

    #Metadatensatz aktualisieren
    zenodo.putRecordData(recordData)

    #Datensatz publizieren
    publish = zenodo.publishRecord()
    print(publish)
    #break