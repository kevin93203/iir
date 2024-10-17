from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import se
import file_process
import model
import common.db_connetion as db_connetion

app = FastAPI()

# 配置静态文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")


# 回傳 HTML 頁面
@app.get("/", response_class=HTMLResponse)
async def read_html():
    file_path = os.path.join("static", "index.html")
    return HTMLResponse(open(file_path, encoding='utf-8').read())

# 接收上傳的檔案 (支援多檔案上傳)
@app.post("/api/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_file_names = []
    documents = []
    titles = []

    # 處理檔案，限制檔案類型為 json 或 xml
    for file in files:
        file_content = await file.read()  # 讀取檔案內容
        if file.content_type == "application/json":
            # 解析 JSON 檔案
            try:
                json_data:dict = json.loads(file_content)
                text = json_data.get("text")
                if(text):
                    documents.append(text)
            except json.JSONDecodeError:
                return {"error": f"Failed to parse JSON file: {file.filename}"}
        
        elif file.content_type == "text/xml":
            # 解析 XML 檔案
            try:
                # 讀取 XML 檔案
                root = ET.fromstring(file_content)
                # 使用 XPath 查找所有 AbstractText 標籤
                abstract_texts = root.find(".//AbstractText")
                if abstract_texts!=None:
                    documents.append(abstract_texts.text)

                article_title = root.find(".//ArticleTitle")
                if article_title!=None:
                    titles.append(article_title.text)
            except ET.ParseError:
                return {"error": f"Failed to parse XML file: {file.filename}"}
        else:
            return {"error": f"Unsupported file type: {file.filename}"}

        uploaded_file_names.append(file.filename)
    
    #對每個文件倒排索引
    inverted_index = se.build_inverted_indexes(documents)
    inverted_index_titles = se.build_inverted_indexes(titles)
    #統計每個文件的統計量
    stats = se.documents_statistics(documents)
    
    #回傳所有檔案名稱、文件內容、倒排索引, 統計量， 空的搜尋紀錄
    return {
        "filenames": uploaded_file_names, 
        "documents": documents,
        "titles": titles, 
        "inverted_index": inverted_index,
        "inverted_index_titles":  inverted_index_titles,
        "statistics":stats,
        "search_history":[],
    }

# 接收上傳的檔案 (支援多檔案上傳)
@app.post("/api/upload2/")
async def upload_files2(files: List[UploadFile] = File(...)):
    docs = []
    # 處理檔案，限制檔案類型為xml
    for file in files:
        docs.append(await file_process.analysis(file))
    
    return docs
    
    

@app.post("/api/search/")
async def search_documents(query:str, data:model.Data):
    keywords, highlighted_documents, highlighted_titles, rank = se.highlight_query(query, data)
    return {
        "query": query,
        "query_keywords": keywords,
        "highlighted_documents": highlighted_documents,
        "highlighted_titles": highlighted_titles,
        "rank": rank
    }

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import re
import string

def custom_tokenize(text):
    return re.findall(r'\b\w+\b|[^\w\s]',text)

def get_query_keywords(query:str, stemmer:PorterStemmer | None = None):
    stop_words = set(stopwords.words('english'))

    # 切詞
    query_words = custom_tokenize(query.lower())
    
    # use stemmer
    if(stemmer!=None):
        query_words = [stemmer.stem(word) for word in query_words]
    
    # 去除stopwords和標點符號
    query_keywords = [word for word in query_words if word not in stop_words and word not in string.punctuation]

    return query_keywords

def getQueryFilter(query_keywords: list[str]):
    or_list = []
    for word in query_keywords:
        or_list.append({ f"pStemInvIdx.title.{word}": { "$exists": True } })
        or_list.append({ f"pStemInvIdx.abstract.{word}": { "$exists": True } })
    
    return {"$or": or_list}

def getProjection(query_keywords: list[str]):
    projection = {
        "_id":0, 
        "pmid":1, 
        "title": 1, 
        "abstract":1, 
        "dateCompleted":1
    }
    for word in query_keywords:
        projection[f"pStemInvIdx.title.{word}"] = 1
        projection[f"pStemInvIdx.abstract.{word}"] = 1
    
    return projection


def getHighlightedDoc(
    content:str, 
    query_keywords:list[str],
    invIdx:dict[str,dict],
    stemmer:PorterStemmer | None = None
):
    # highlighted_position = []
    # for word in invIdx:
    #     highlighted_position.extend(invIdx[word]['position'])
    words = custom_tokenize(content)
    # for i in highlighted_position:
    #     words[i] = f"<mark>{words[i]}</mark>"
    
    highlighted_content = content
    match_count = 0
    for word in words:
        word_clean = word.lower().strip(string.punctuation)
        if(stemmer!=None):
            word_clean = stemmer.stem(word_clean)
        if word_clean in query_keywords:
            # 使用正则表达式来替换匹配的单词，保持原有的大小写和标点
            # 确保没有已经标记的词
            highlighted_content = re.sub(r'(?<!<mark>)\b' + re.escape(word) + r'\b(?!<\/mark>)', 
                                     f"<mark>{word}</mark>", 
                                     highlighted_content)
            match_count += 1
    return highlighted_content, match_count

def highlight_query_in_documents(
    query_keywords: list[str], 
    docs: list[dict], 
    stemmer: PorterStemmer | None = None,
):
    invIdxKey = "pStemInvIdx" if stemmer else "nonStemInvIdx"
    for doc in docs:
        # 使用正则表达式来分割文档，保留标点符号
        doc['title'], title_match_count = getHighlightedDoc(doc['title'], query_keywords, doc[invIdxKey]['title'], stemmer)
        doc['abstract'], abstract_match_count = getHighlightedDoc(doc['abstract'], query_keywords, doc[invIdxKey]['abstract'], stemmer)
        doc['match_count'] = title_match_count + abstract_match_count

    #docs依照match_count排列
    docs = sorted(docs, key=lambda x: x['match_count'], reverse=True)
    #docs濾除invIdx
    docs = [{k: v for k, v in d.items() if k != invIdxKey} for d in docs]
    
    return docs

def dateCompleteToString(docs:list[dict]):
    for doc in docs:
        if(isinstance(doc['dateCompleted'], datetime)):
            doc['dateCompleted'] = doc['dateCompleted'].strftime("%Y-%m-%d")
    return docs

@app.get("/api/search/v2")
async def search_documents_v2(query:str, usePorterStem:bool=True):
    stemmer = PorterStemmer() if usePorterStem else None
    query_keywords = get_query_keywords(query, stemmer)
    query_filter = getQueryFilter(query_keywords)
    projection = getProjection(query_keywords)
    result = db_connetion.collection.find(
        query_filter,
        projection
    )
    docs = list(result)
    docs = highlight_query_in_documents(query_keywords, docs, stemmer)
    # 將dateCompleted轉為"yyyy-mm-dd""
    docs = dateCompleteToString(docs)
    
    return {
        "query": query,
        "query_keywords": query_keywords,
        "docs": docs,
    }

@app.get("/api/document_set/")
async def document_set():
    result = db_connetion.collection.find(
        {},
        {
            "_id":0, 
            "pmid":1, 
            "title": 1, 
            "abstract":1, 
            "statistics":1, 
            "dateCompleted":1
        }
    )
    docs = list(result)

    # 將dateCompleted轉為"yyyy-mm-dd""
    docs = dateCompleteToString(docs)
    return docs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
