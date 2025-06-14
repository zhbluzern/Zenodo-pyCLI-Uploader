import re
import requests

# Script imports Metadata from crossref using a DOI
# Code is mainly based on Scholia's DOI-Importer: https://github.com/WDscholia/scholia/blob/main/scholia/doi.py

CROSSREF_URL = "https://api.crossref.org/v1/works/"

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
            "given_name" : author_dict.get('given', ''),
            "family_name" : author_dict.get('family', ''),
            "affiliation" : author_dict.get("affiliation",""),
            # formatted_name = f"{name} {given_name} {family_name}".strip(),
            "orcid" : re.sub("https://orcid.org/","",author_dict.get("ORCID",""))
            }
        return author        


    doi = doi.strip()
    url = CROSSREF_URL + doi
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            entry = response.json()["message"]

            plain_date, date = get_date(entry["issued"]["date-parts"][0])

            paper = {
                "doi": entry.get("DOI"),
                "authors": [
                    get_author_name(author)
                    for author in entry.get("author", [])
                ],
                # not full text URL if the paper is closed source
                # "full_text_url":
                #      entry.get("resource", {}).get("primary", {}).get("URL"),
                "date_P577": date,
                "date": plain_date,
                # Some titles may have a newline in them. This should be
                # converted to an ordinary space character
                "title": re.sub(r"\s+", " ", entry["title"][0]),
            }     
            issns = entry.get('ISSN')
            paper["issn"] = issns[0]
            issue = entry.get('issue')
            if issue:
                paper['issue'] = issue

            pages = entry.get('page')
            if pages:
                paper['pages'] = pages

                # Compute number of pages from pages
                # number_of_pages = pages_to_number_of_pages(pages)
                # if number_of_pages:
                #     paper['number_of_pages'] = number_of_pages

            volume = entry.get('volume')
            if volume:
                paper['volume'] = volume

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
