import os
from fastapi import UploadFile
import xml.etree.ElementTree as ET
from nltk.stem import PorterStemmer
import se
import asyncio
from datetime import datetime

def list_xml_files(directory):
    return [file for file in os.listdir(directory) if file.endswith('.xml')]

# 提取PMID、title、Abstract, 建立inverted index, 計算統計值
async def analysis(file: UploadFile | str):
    root = None
    if(isinstance(file, UploadFile)):
        file_content = await file.read()  # 讀取檔案內容
        # 讀取 XML 檔案
        root = ET.fromstring(file_content)
    else:
        tree = ET.parse(file)
        # 獲取根節點
        root = tree.getroot()
    
    # 使用 XPath 查找所有標籤
    pmid = root.find(".//PMID")
    title = root.find(".//ArticleTitle")
    abstract = root.find(".//AbstractText")
    articleDateElement = root.find(".//ArticleDate")

    if (pmid != None) and (title!=None) and (abstract!=None) :
        articleDate = None
        if(articleDateElement!=None):
            articleDateYearEle = articleDateElement.find(".//Year")
            articleDateMonthEle = articleDateElement.find(".//Month")
            articleDateDayEle = articleDateElement.find(".//Day")
            if(articleDateYearEle!=None and articleDateMonthEle!=None and articleDateDayEle!=None):
                if(articleDateYearEle.text and articleDateMonthEle.text and articleDateDayEle.text):
                    articleDateDate = articleDateYearEle.text + articleDateMonthEle.text + articleDateDayEle.text
                    articleDate = datetime.strptime(articleDateDate,"%Y%m%d")
        

        title_text = ''.join(title.itertext())
        abstract_text = ''.join(abstract.itertext())
        nonStemInvIdx = {"title":{}, "abstract":{}} 
        pStemInvIdx = {"title":{}, "abstract":{}}
        stats = {}
        
        # 對title分別建立inverted_index和使用porter stem後建立的inverted_index
        if(title_text):
            nonStemInvIdx["title"] = se.build_inverted_index(title_text)
            pStemInvIdx["title"] = se.build_inverted_index(title_text, stemmer=PorterStemmer())
        
        # 對abstract分別建立inverted_index和使用porter stem後建立的inverted_index
        if(abstract_text):
            nonStemInvIdx["abstract"] = se.build_inverted_index(abstract_text)
            pStemInvIdx["abstract"] = se.build_inverted_index(abstract_text, stemmer=PorterStemmer())
        
        # 對abstract計算各統計值
        if(abstract_text):
            stats = se.document_statistics(abstract_text)

        doc = {
            "pmid": pmid.text,
            "articleDate": articleDate,
            "title": title_text,
            "abstract": abstract_text,
            "pStemInvIdx": pStemInvIdx,
            "nonStemInvIdx": nonStemInvIdx,
            "statistics": stats,
            "updated_at": datetime.now()
        }

        return doc

    else:
        if(isinstance(file, UploadFile)):
            print(file.filename)
        else:
            print(file)
        return None

    
if __name__ == "__main__":
    import common.db_connetion as db_connection
    import pymongo


    file_dir = './data'

    xml_files = list_xml_files(file_dir)
    batch_size = 200
    batch_ops = []

    for xml_file_name in xml_files:
        xml_path = os.path.join(file_dir, xml_file_name)
        doc = asyncio.run(analysis(xml_path))
        if(doc == None): continue

        # 生成 upsert 操作（如果匹配则更新，不匹配则插入）
        operation = pymongo.UpdateOne(
            {'pmid': doc['pmid']},  # 假设文档的 `_id` 字段为唯一键
            {'$set': doc},        # 如果匹配到已有的文档，则更新整个文档
            upsert=True           # 如果没有匹配到，则插入文档
        )
        batch_ops.append(operation)

        # 当批次达到10个时，执行批量操作
        if len(batch_ops) == batch_size:
            db_connection.collection.bulk_write(batch_ops)
            batch_ops = []  # 清空批次

    # 如果最后一批不足10个，依然需要处理
    if batch_ops:
        db_connection.collection.bulk_write(batch_ops)
        
            