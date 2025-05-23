import bnl.bnlParser as bnlParser
import pandas as pd
from datetime import datetime

resultSet = []
baseUrl = "https://brand-new-life.org"
rootHtml = bnlParser.getHTML("https://brand-new-life.org/b-n-l/search")


resultSet = bnlParser.parseArticleList(rootHtml, resultSet, baseUrl)
nextPage = rootHtml.find("p", {"class":"pagination"}).find("a", {"class":"next"})

while nextPage != None:
    print(nextPage["href"])
    rootHtml = bnlParser.getHTML(f"{baseUrl}/{nextPage['href']}")
    resultSet = bnlParser.parseArticleList(rootHtml, resultSet, baseUrl)
    nextPage = rootHtml.find("p", {"class":"pagination"}).find("a", {"class":"next"})

df = pd.DataFrame(resultSet) 
currentDateStr = datetime.now().strftime("%Y%m%d")
df.to_excel(f'bnl/BNL_Liste_{currentDateStr}.xlsx', index=False) 