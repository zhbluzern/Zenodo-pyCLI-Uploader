import requests
from dotenv import load_dotenv
import os

# ZenodoSearch Class 
#    combines several methods for GET-Request which don't need API-KEY authentification
#    classical "query"-Requests (records, communities, requests)
class ZenodoSearch:
    def __init__(self):
        load_dotenv()
        self.ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
        self.API_URL = os.getenv("API_URL")

    def searchCommunityBySlug(self, slug):
        url = f"{self.API_URL}communities"
        r = requests.get(url=url, params={'q' : f"slug:{slug}"})
        return r
    
    def getCommunityIdBySlug(self, slug):
        results = self.searchCommunityBySlug(slug).json()
        if (len(results["hits"]["hits"])) == 1 and results["hits"]["hits"][0]["slug"] == slug: #1 Result means probably an exact match for the community slug
            for hit in results["hits"]["hits"]:
                print(f"searched for community {slug} and matched slug {hit['slug']} with id {hit['id']}")
                return hit["id"]

if __name__ == "__main__":
    zenSearch = ZenodoSearch()
    communityId = zenSearch.getCommunityIdBySlug("lory_hslu_dfk_bnl")
    print(communityId)