
import src.invenioRest as InvenioRest
import src.handleFiles as handleFiles
import src.handleInvenio as handleInvenio
import json
import re
import pandas as pd
import time


# Read a Metadata-Excel-File into a DataFrame

input_file = 'lory_zhb_inventory.xlsx'
data = pd.read_excel(input_file)
df = pd.DataFrame(data)
initColumns = df.columns


for index, row in df.iterrows():

    #create dlza note

    dlza_line = f"Langzeitarchivierung durch: {row['organisation']} - {row['signature']} - {row['last_changed'][0:10]}"

    dlza_notes = [{
        "description": dlza_line,
        "type": {
            "id": "notes",
            "title": {
                "de": "Anmerkungen",
                "en": "Notes"
            }
        }
    }]
    #create dlza related identifiers
    dlza_identifier = row["signature"]

    dlza_related_identifiers = [{
        "identifier": dlza_identifier,
        "relation_type": {
            "id": "isidenticalto",
            "title": {
                "de": "Ist identisch mit",
                "en": "Is identical to"
            } 
        },
        "resource_type": {
            "id": "dataset",
            "title": {
                "de": "Datensatz",
                "en": "Dataset"
            }
        },
        "scheme": "other"
    }]

    # get the zenodo record ID from the identifiers column
    identifier_list =  row["identifiers"]

    # split the identifiers string into a list
    items = identifier_list.strip("[]").split(", ")

    # Search for entry starting with "zenodo:"
    for item in items:
        item = item.strip("'\"")  # Entfernt einfache oder doppelte Anführungszeichen
        if item.startswith("zenodo:"):
            recordId = item.split(":")[1]
            #print("Record ID:", recordId)
            break

    if not recordId:
        print(f"Row {index}: No Zenodo record ID found in identifiers column.")
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Row {index}: No Zenodo record ID found in identifiers column, update manually: {dlza_line} - {dlza_identifier}\n")
        continue

    print("\n------------------------------\n")
    print(f"Row {index} - Record id: {recordId}")

    # create Zenodo-Record
    zenodo = InvenioRest.Invenio()
   
    zenodo.editRecord(recordId)

    record = zenodo.exportRecord(recordId)
    
    # make sure the necessary fields exist:

    record["metadata"].setdefault("additional_descriptions", [])
    record["metadata"].setdefault("related_identifiers", [])

    # add note if it does not already exist
    for note in dlza_notes:
        if note not in record["metadata"]["additional_descriptions"]:
            record["metadata"]["additional_descriptions"].append(note)

    # add related identifier if it does not already exist
    for identifier in dlza_related_identifiers:
        if identifier not in record["metadata"]["related_identifiers"]:
            record["metadata"]["related_identifiers"].append(identifier)

    # debugging: print pretty JSON of the metadata
    #print(json.dumps(record["metadata"], indent=4, ensure_ascii=False))

    # check if the record is owned by the LORY user (18299)
    zenodo_user = record["parent"]["access"]["owned_by"]["user"]
    if zenodo_user != "18299":
        print("UPDATE RECORD not possible, not lory@zhbluzern.ch user : ", zenodo_user)
        # write row to error file
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Row {index} - Record id: {recordId}: Not lory@zhbluzern.ch user: {zenodo_user}, update manually: {dlza_line} - {dlza_identifier}\n")
        continue

    # update the record with the new metadata
    zenodo.updateRecord(recordId, record)
    time.sleep(1)  # wait for 1 second to avoid rate limiting

    zenodo.publishDraft(recordId)
    time.sleep(1)  # wait for 1 second to avoid rate limiting

    updated_record = zenodo.getRecord(recordId)
    if updated_record.get("status") == "published":
        print("Record updated and published: ", recordId)
    else:
        print("Record not published, check draft mode: ", recordId)
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Row {index} - Record id: {recordId}: Record not published, check draft mode or update manually: {dlza_line} - {dlza_identifier}\n")

print("All records processed.")            
