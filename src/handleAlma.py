import requests
from lxml import etree
import re

class readAlma():

    def __init__(self):
        self.ns = {'xmlns' : 'http://www.loc.gov/zing/srw/', 'slim' : 'http://www.loc.gov/MARC21/slim'} 
        self.headers = {"Accept": "application/xml"}    
        self.sruUrl = "https://slsp-rzs.alma.exlibrisgroup.com/view/sru/41SLSP_RZS/"


    def getRecordsViaSRU(self, query):
        params = { "version" : "1.2", "operation" : "searchRetrieve", "recordSchema" : "marcxml", "maximumRecords" : 20, "query": query}
        response = requests.get(url=self.sruUrl, params=params, headers=self.headers)
        root = etree.fromstring(response.content)
        records = root.findall(".//xmlns:record",namespaces=self.ns)
        return records

    def getMetadataByXpath(self, rec, xpath):
        metadata = rec.xpath(xpath,namespaces=self.ns)
        return metadata
    
if __name__ == "__main__":
    alma = readAlma()
    recs = alma.getRecordsViaSRU(query="alma.all_for_ui=\"*edoc.zhbluzern.ch/*\"")
    for rec in recs:
        mmsId_IZ = alma.getMetadataByXpath(rec, ".//slim:controlfield[@tag='001']")
        print(mmsId_IZ[0].text)
        
        mmsId_NZ = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='035']/slim:subfield[@code='a'][starts-with(text(),'(EXLNZ-41SLSP_NETWORK)')]")
        print(re.sub("\(EXLNZ-41SLSP_NETWORK\)","",mmsId_NZ[0].text))

        title = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='245']/slim:subfield[@code='a']")
        print(title[0].text)

        desc = alma.getMetadataByXpath(rec, ".//slim:datafield[@tag='520']/slim:subfield[@code='a']")
        print(desc[0].text)