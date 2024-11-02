from fastapi import APIRouter, Query
from datetime import datetime, date
import re
import string
from utils.model import QueryOperator, PaginatedResponse
from nltk.stem import PorterStemmer
from utils.query_utils import (
    search_documents_page,
    articleDateToString,
    custom_tokenize
)

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

def getHighlightedDoc(
    content:str, 
    query_keywords:list[str],
    invIdx:dict[str,dict],
    stemmer:PorterStemmer | None = None
):
    words = custom_tokenize(content)
    
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

search_router = APIRouter()

@search_router.get("/api/search")
async def search_documents_content(
    query:str, 
    usePorterStem:bool=True,
    startDate: date | None = None,
    endDate: date | None = None,
    operator: QueryOperator = QueryOperator.OR,
    page: int = Query(1, ge=1, description="當前頁碼"),
    pageSize: int = Query(12, ge=1, le=100, description="每頁數量"),
):
    startDatetime = datetime.combine(startDate, datetime.min.time()) if startDate else None
    endDatetime = datetime.combine(endDate, datetime.min.time()) if endDate else None
    docs, query_keywords, stemmer, totalDocs, totalPages = \
        search_documents_page(query, usePorterStem, startDatetime, endDatetime, operator, page, pageSize)
    docs = highlight_query_in_documents(query_keywords, docs, stemmer)
    # 將articleDate轉為"yyyy-mm-dd""
    docs = articleDateToString(docs)

    return PaginatedResponse(
        items=docs,
        total=totalDocs,
        totalPages=totalPages,
        current_page=page,
        pageSize=pageSize,
        query=query,
        query_keywords=query_keywords
    )