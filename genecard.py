import requests
from lxml import etree
import time
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os

os.environ['GH_TOKEN'] = "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"

#from selenium.webdriver.edge.service import Service
#from webdriver_manager.microsoft import EdgeChromiumDriverManager

#from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager


base_url = 'https://www.genecards.org'

#driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))


#driver = webdriver.Chrome(executable_path = r"C:\Users\Hsuan\nctu\web_crawler\chromedriver.exe")

driver.get(base_url)






headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'cookie': 'ASP.NET_SessionId=fbn1f52ppnbotksqpszu4lhe; rvcn=0Kpw76RjQWVPghHk_eHFMzdye5bqaMDGx5BUmO0BCiQv5NL9fBg_F6DHp2D7zcU955B-K0moDdWWLEgyLvPPU8H7vRY1; ARRAffinity=bbda99ae9f2cbea3a7894c6d34604e73c55fed16cf5f41fadce3a25415ea24f4; visid_incap_146342=JJg8EvqnRL21kFlyDqoJtVp4jF4AAAAAQUIPAAAAAADoDyfKhHCxYjc4Esv7sFIl; nlbi_146342=3Z3Bda14by/DQ4RJmewSQgAAAABIDL4M3uKW9Nn5B+a0Tx19; _ga=GA1.2.1127478822.1586264159; _gid=GA1.2.772327545.1586264159; __gads=ID=00050bb968e74cd0:T=1586264160:S=ALNI_MZrmbqyOxyLDo2Z5_k5rcoA7tMkLg; incap_ses_433_146342=JsQwcq4j9GPUtFdrVVQCBrF/jF4AAAAA4L1izrsxqq8bGasGou8j5g=='
}

def get_cookies(base_url):
    try:
        requests.session()
        sessions = requests.get(base_url, headers=headers)
        cookie = sessions.cookies
    except:
        cookie = ''
    return cookie

def get_search_response(base_url, cookies):
    try:
        response = requests.get(base_url, headers=headers, cookies=cookies)
        content = response.content.decode()
        data = etree.HTML(content)
        match_gene = data.xpath('//tbody/tr[1]/td[3]/a/text()')[0]
    except:
        match_gene = 'NA'
    print(match_gene)
    return match_gene


genes = pd.read_csv(r"C:\Users\Hsuan\nctu\實驗室學長姐資料\于鈴學姊\BMN\FPKM_protein_coding_gene.csv")
f = open(r"C:\Users\Hsuan\nctu\實驗室學長姐資料\于鈴學姊\BMN\20230210_glucocorticoid_genecards.txt","w", encoding='UTF-8')
f.write("gene_name\tname\tgenecards_summary\tEntrez_summary\tclassification\n")
count=0
for item in list(genes["SYMBOL"]):
    _list=[]
    count=count+1
    print(count)
    new_url = 'https://www.genecards.org/Search/Keyword?queryString=' + item
    cookies = get_cookies(new_url)
    driver.get(new_url)
    time.sleep(2)
    name = get_search_response(new_url, cookies)
    _list.append(item)
    _list.append(name)
    
    geneurl = driver.current_url  #取得當前網址: 獲取當前瀏覽頁面的網址連結
    psps = driver.page_source
    spsp = bs(psps, "lxml")
    for a in spsp.select("td a"):
        if (a.text) == name:
            urll = "https://www.genecards.org" + (a.get("href"))
    driver.get(urll)
    time.sleep(2)

    geneurl_2 = driver.current_url  #取得當前網址: 獲取當前瀏覽頁面的網址連結
    psps_2 = driver.page_source
    spsp_2 = bs(psps_2, "lxml")
    summaries = spsp_2.select('#summaries .gc-subsection')
    genecards_summary_text = entrezgene_summary_text = '.'

    for summary in summaries:
        title = summary.select('h3')[0].text.strip()
        if title.startswith('GeneCards Summary'):
            genecards_summary = summary.select('p')[0]
            _list.append(' '.join(re.split(r'\n|\t|\s+', genecards_summary.text.strip())))
    for summary in summaries:
        title = summary.select('h3')[0].text.strip()
        if title.startswith('Entrez Gene Summary'):
            Entrez_summary = summary.select('p')[0]
            _list.append(Entrez_summary.text)
    
    for summary in summaries:
        title = summary.select('h3')[0].text.strip()
        if title.startswith('GeneCards Summary'):
            genecards_summary = summary.select('p')[0]
            if "glucocorticoid" in (genecards_summary.text) or "Glucocorticoid" in (genecards_summary.text) :
                _list.append("glucocorticoid")
            
            
    for summary in summaries:
        title = summary.select('h3')[0].text.strip()
        if title.startswith('Entrez Gene Summary'):
            Entrez_summary = summary.select('p')[0]
            if "glucocorticoid" in (Entrez_summary.text) or "Glucocorticoid" in (Entrez_summary.text):
                _list.append("glucocorticoid")

            
    f.write('\t'.join(_list)+'\n')

f.close()