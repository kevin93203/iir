from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Literal, Optional
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from math import ceil
from pydantic import BaseModel

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

def getQueryFilter(
    query_keywords: list[str], 
    invIdxKey: Literal['pStemInvIdx','nonStemInvIdx']
):
    or_list = []
    for word in query_keywords:
        or_list.append({ f"{invIdxKey}.title.{word}": { "$exists": True } })
        or_list.append({ f"{invIdxKey}.abstract.{word}": { "$exists": True } })
    
    return {"$or": or_list}

def getAllWordFreqField(
    query_keywords: list[str], 
    invIdxKey: Literal['pStemInvIdx','nonStemInvIdx']     
):
    all_word_field = []
    for word in query_keywords:
        all_word_field.append(f"${invIdxKey}.title.{word}.freq")
        all_word_field.append(f"${invIdxKey}.abstract.{word}.freq")
    return all_word_field

def getProjection(
    query_keywords: list[str],
    invIdxKey: Literal['pStemInvIdx','nonStemInvIdx'],
    full_abstract_InvIdx: bool,
):
    projection = {
        "_id":0, 
        "pmid":1, 
        "title": 1, 
        "abstract":1, 
        "dateCompleted":1
    }

    if(full_abstract_InvIdx):
        projection[f"{invIdxKey}.abstract"] = 1
        return projection
    
    for word in query_keywords:
        projection[f"{invIdxKey}.title.{word}"] = 1
        projection[f"{invIdxKey}.abstract.{word}"] = 1
    
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

def search_documents(query:str, usePorterStem:bool, full_abstract_InvIdx:bool = False):
    stemmer = PorterStemmer() if usePorterStem else None
    query_keywords = get_query_keywords(query, stemmer)
    
    invIdxKey = "pStemInvIdx" if stemmer else "nonStemInvIdx"
    query_filter = getQueryFilter(query_keywords, invIdxKey)
    projection = getProjection(query_keywords, invIdxKey, full_abstract_InvIdx)
    result = db_connetion.collection.find(
        query_filter,
        projection
    )
    docs = list(result)
    return docs, query_keywords, stemmer

def search_documents_page(
    query:str, 
    usePorterStem:bool, 
    page: int,
    pageSize: int,
    full_abstract_InvIdx:bool = False
):
    stemmer = PorterStemmer() if usePorterStem else None
    query_keywords = get_query_keywords(query, stemmer)
    
    invIdxKey = "pStemInvIdx" if stemmer else "nonStemInvIdx"
    query_filter = getQueryFilter(query_keywords, invIdxKey)
    all_word_freq_field = getAllWordFreqField(query_keywords, invIdxKey)
    print("all_word_freq_field: ", all_word_freq_field)
    projection = getProjection(query_keywords, invIdxKey, full_abstract_InvIdx)
    projection["match_count"] = 1
    count_pipeline = [{"$match": query_filter},{"$count": "total"}]
    # 獲取總數
    count_result = list(db_connetion.collection.aggregate(count_pipeline))
    totalDocs:int = count_result[0]["total"] if count_result else 0
    print("totalDocs: ",totalDocs)
    
    # 計算總頁數
    totalPages = ceil(totalDocs / pageSize)

    pipeline = [
        {"$match": query_filter},
        {
            "$addFields": {
                "match_count": { 
                    "$add": all_word_freq_field
                }
            }
        },
        {"$sort": {"match_count": -1}},
        {"$skip": (page - 1) * pageSize},
        {"$limit": pageSize},
        {"$project": projection}
    ]
    
    docs = list(db_connetion.collection.aggregate(pipeline))

    return docs, query_keywords, stemmer, totalDocs, totalPages

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    totalPages: int
    current_page: int
    pageSize: int
    query: str | None = None
    query_keywords: list[str] | None = None

@app.get("/api/search")
async def search_documents_content(
    query:str, 
    usePorterStem:bool=True,
    page: int = Query(1, ge=1, description="當前頁碼"),
    pageSize: int = Query(12, ge=1, le=100, description="每頁數量"),
):
    docs, query_keywords, stemmer, totalDocs, totalPages = \
         search_documents_page(query, usePorterStem, page, pageSize)
    docs = highlight_query_in_documents(query_keywords, docs, stemmer)
    # 將dateCompleted轉為"yyyy-mm-dd""
    docs = dateCompleteToString(docs)

    return PaginatedResponse(
        items=docs,
        total=totalDocs,
        totalPages=totalPages,
        current_page=page,
        pageSize=pageSize,
        query=query,
        query_keywords=query_keywords
    )

def invIdxToWordsAndFrequencies(invIdx:dict[str,dict]):
    words = list(invIdx.keys())
    words = sorted(words, key= lambda x: invIdx[x]['freq'],reverse=True)
    frequencies = []
    for word in words:
        frequencies.append(invIdx[word]["freq"])
    return {"words": words, "frequencies": frequencies}

@app.get("/api/document_set/")
async def document_set(
    page: int = Query(1, ge=1, description="當前頁碼"),
    pageSize: int = Query(12, ge=1, le=100, description="每頁數量"),
):
    query_filter = {}
    projection = {
            "_id":0, 
            "pmid":1, 
            "title": 1, 
            "abstract":1, 
            "statistics":1, 
            "dateCompleted":1,
            "pStemInvIdx.abstract":1,
            "nonStemInvIdx.abstract":1,
    }

    # 計算總數量
    totalDocs = db_connetion.collection.count_documents(query_filter)
    
    # 計算總頁數
    totalPages = ceil(totalDocs / pageSize)
    
    # 計算跳過的數量
    skip = (page - 1) * pageSize
    
    # 查詢數據
    docs = list(db_connetion.collection
        .find(query_filter,projection)
        .skip(skip)
        .limit(pageSize))

    # invIdxToWordsAndFrequencies(docs[0]['pStemInvIdx']['abstract'])

    for doc in docs:
        doc['pStemZipf'] = invIdxToWordsAndFrequencies(doc['pStemInvIdx']['abstract'])
        doc['nonStemZipf'] = invIdxToWordsAndFrequencies(doc['nonStemInvIdx']['abstract'])
    
    #docs濾除invIdx
    docs = [{k: v for k, v in d.items() if k not in ["pStemInvIdx","nonStemInvIdx"]} for d in docs]


    # 將dateCompleted轉為"yyyy-mm-dd""
    docs = dateCompleteToString(docs)

    return PaginatedResponse(
        items=docs,
        total=totalDocs,
        totalPages=totalPages,
        current_page=page,
        pageSize=pageSize
    )

@app.get("/api/document/zipf")
async def document_zipf(pmid:str):
    doc:dict | None = db_connetion.collection.find_one(
        {"pmid":pmid},
        {
            "pStemInvIdx.abstract":1,
            "nonStemInvIdx.abstract":1,
        }
    )
    if doc == None:
        return
    
    pStemZipf = invIdxToWordsAndFrequencies(doc['pStemInvIdx']['abstract'])
    nonStemZipf = invIdxToWordsAndFrequencies(doc['nonStemInvIdx']['abstract'])

    return {
        "pStemZipf": pStemZipf,
        "nonStemZipf": nonStemZipf
    }

@app.get("/api/search/zipf")
async def search_zipf(query:str, usePorterStem:bool=True):
    if not query: return
    docs, _, _ = search_documents(query, usePorterStem, True)
    invIdxKey = "pStemInvIdx" if usePorterStem else "nonStemInvIdx"
    
    words_frequencies ={}
    for doc in docs:
        abstract_invIdx =  doc[invIdxKey]['abstract']
        for word in abstract_invIdx:
            if(word in words_frequencies):
                words_frequencies[word] += abstract_invIdx[word]['freq']
            else:
                words_frequencies[word] = abstract_invIdx[word]['freq']
    
    words_freq_list = [{"word": word, "freq": words_frequencies[word]} for word in  words_frequencies]
    words_freq_list.sort(key=lambda x: x['freq'], reverse=True)
    words = [ item['word'] for item in words_freq_list]
    frequencies = [ item['freq'] for item in words_freq_list]
    
    return {
        "words": words,
        "frequencies": frequencies
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
