# Zenodo pyCLI Uploader

Dieses Python-Skript stellt unter Verwendung der Zenodo-Rest-API ein einfaches CLI-Tool zur Verfügung um auf Basis von xls-Files die Bearbeitung und Erstellung von Datensätzen in Zenodo in Stapelverarbeitung (inkl. Fileupload bis 100 MB) zu ermöglichen.

# Beispiele

* [examples/searchZenodo_isbnInArticles.py](searchZenodo_isbnInArticles.py) ändert Metadaten in Zenodo auf Basis einer vorangehenden REST-API-Abfrage. Gesucht werden Datensätze die eine ISBN-Nummer im Format einer ISSN eingetragen haben und gleichzeitig den resource subtype article besitzen.
* [examples/xls2Zenodo.py](searchZenodo_isbnInArticles.py) auf Basis einer XLS-Datei mit bestehenden Zenodo-Record-IDs werden die Datensätze in Zenodo geöffnet und mit gegebenen Metadaten aus der xls-Datei ergänzt.
