# Zenodo pyCLI Uploader

Dieses Python-Skript stellt unter Verwendung der Zenodo-Rest-API ein einfaches CLI-Tool zur Verfügung um auf Basis von xls-Files die Bearbeitung und Erstellung von Datensätzen in Zenodo in Stapelverarbeitung (inkl. Fileupload bis 100 MB) zu ermöglichen.

# Beispiele

* [searchZenodo_isbnInArticles.py](examples/searchZenodo_isbnInArticles.py) ändert Metadaten in Zenodo auf Basis einer vorangehenden REST-API-Abfrage. Gesucht werden Datensätze die eine ISBN-Nummer im Format einer ISSN eingetragen haben und gleichzeitig den resource subtype article besitzen.
* [xls2Zenodo.py](examples/searchZenodo_isbnInArticles.py) auf Basis einer XLS-Datei mit bestehenden Zenodo-Record-IDs werden die Datensätze in Zenodo geöffnet und mit gegebenen Metadaten aus der xls-Datei ergänzt.

## Update von Records mit InvenioRDM-REST-API

Seit der Softwaremigration von Zenodo auf InvenioRDM im Oktober 2023 ist es möglich mit der InvenioRDM-Rest-API parallel zur legacy REST-API von Zenodo Datensätze zu erstellen und zu bearbeiten. Mit der InvenioRDM-API hat man aber den Vorteil auf das erweiterte Datenmodell der Invenio-Records zugreifen zu können. Für das aktualisieren publizierten Records in Zenodo müssen aber anders als in der Invenio-Doku vermerkt folgende Arbeitsschritte stattfinden:

```python
import src.invenioRest as invenioRest

recordId = "{YOUR_REC_ID}"

# ===================== Edit already published Records with Invenio-RDM-API =========
zenodo = invenioRest.Invenio()
## Make a draft of the already published record
zenodo.editRecord(recordId)
## Export the published record and use that response for further metadata adjustments
record = zenodo.exportRecord(recordId)
## Make your metadata adjustments
record["metadata"]["title"] = record["metadata"]["title"]+" [new Update]"
## update the record with new data
zenodo.updateRecord(recordId, record)
## publish the record once again
response = zenodo.publishDraft(recordId)
```