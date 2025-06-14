import re
import requests

# Script imports Metadata from crossref using a DOI
# Code is mainly based on Scholia's DOI-Importer: https://github.com/WDscholia/scholia/blob/main/scholia/doi.py

DATACITE_URL = "https://api.datacite.org/dois/"

def get_doi_metadata(doi):
    def get_date(date_list):
        if (len(date_list) == 1 and date_list[0] != "None" and  date_list[0] is not None):
            date = f"{date_list[0]}"
            return date, f"+{date}-00-00T00:00:00Z/9"
        if len(date_list) == 2:
            date = f"{date_list[0]}-{date_list[1]:02d}"
            return date, f"+{date}-00T00:00:00Z/10"
        if len(date_list) == 3:
            date = f"{date_list[0]}-{date_list[1]:02d}-{date_list[2]:02d}"
            return date, f"+{date}T00:00:00Z/11"

    def get_author_name(author_dict):
        author = {
            "name": author_dict.get('name', ''),
            "given_name" : author_dict.get('givenName', ''),
            "family_name" : author_dict.get('familyName', ''),
            "affiliation" : author_dict.get("affiliation")[0],
            # formatted_name = f"{name} {given_name} {family_name}".strip(),
            "orcid" : get_orcid(author_dict.get("nameIdentifiers"))
            }
        return author        

    def get_orcid(nameIds):
        for nameId in nameIds:
            if nameId.get("nameIdentifierScheme","") == "ORCID":
                return nameId.get("nameIdentifier")


    doi = doi.strip()
    url = DATACITE_URL + doi
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            entry = response.json()["data"]
            #plain_date, date = get_date(entry["attributes"]["dates"][0].get("date"))

            paper = {
                "doi": entry.get("id"),
                "authors": [
                    get_author_name(author)
                    for author in entry["attributes"].get("creators", [])
                ],
                # not full text URL if the paper is closed source
                # "full_text_url":
                #      entry.get("resource", {}).get("primary", {}).get("URL"),
                "date": entry["attributes"]["dates"][0].get("date"),
                # Some titles may have a newline in them. This should be
                # converted to an ordinary space character
                "title": entry["attributes"]["titles"][0].get("title")
            }     
            # issns = entry.get('ISSN')
            # paper["issn"] = issns[0]
            # issue = entry.get('issue')
            # if issue:
            #     paper['issue'] = issue

            # pages = entry.get('page')
            # if pages:
            #     paper['pages'] = pages

            #     # Compute number of pages from pages
            #     # number_of_pages = pages_to_number_of_pages(pages)
            #     # if number_of_pages:
            #     #     paper['number_of_pages'] = number_of_pages

            # volume = entry.get('volume')
            # if volume:
            #     paper['volume'] = volume

            return paper
        else:
            if response.text == "Resource not found.":
                return {'error': "Not found"}
            # Handle non-200 status codes (e.g., 404, 500) appropriately
            status_code = response.status_code
            return {"error": f"Request failed with status code {status_code}"}
    except requests.exceptions.RequestException as e:
        # connection timeout, DNS resolution error, etc
        current_app.logger.debug(f'Request failed due to a network error: {e}')
        return {'error': 'Request failed due to a network error'}

if __name__ == "__main__":
    paper = get_doi_metadata("10.1016/j.dendro.2023.126065")
    print(paper)
    paper = get_doi_metadata("10.5281/zenodo.12697661")
    print(paper)
    paper = get_doi_metadata("10.1186/s40494-022-00686-6")
    print(paper)
