import requests
import time
import os
import xml.etree.ElementTree as ET


with open("./data/pmid-enteroviru-set.txt") as f:
    text = f.read()
    pmid_list = text.split("\n")

file_dir = "./data"

pmid_len = len(pmid_list)
chunk_size = 10

for i in range(1170, pmid_len, chunk_size):
    chunk_pmid_list = pmid_list[i:i + chunk_size]
    pmids = ','.join(chunk_pmid_list)

    print(f"downloading {i} ~ {i + chunk_size - 1} file...")
    
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmids}&retmode=xml"

    response = None
    while response is None or response.status_code != 200:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to download {pmids}, status code {response.status_code}. Retrying...")
                time.sleep(2)  # 等待2秒後重試
        except Exception as e:
            print(e)
    
    success_pmid_list = []
    root = ET.fromstring(response.text)
    articles = root.findall(".//PubmedArticle")
    # 遍歷每個 <PubmedArticle> 並輸出到單獨的 XML 文件
    for i, article in enumerate(articles, start=1):
        # 提取 PMID 作為文件名的一部分
        pmid = article.find(".//PMID").text if article.find(".//PMID") is not None else f"article_{i}"

        # 建立 ElementTree 對象
        article_tree = ET.ElementTree(article)

        # 輸出到 XML 文件
        filename = os.path.join(file_dir, f"{pmid}.xml")
        article_tree.write(filename, encoding="utf-8", xml_declaration=True)

        print(f"Saved: {filename}")
    
    time.sleep(1)
