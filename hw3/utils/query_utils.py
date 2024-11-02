import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
from typing import Literal
from .model import QueryOperator
from . import db_connection
from datetime import datetime
from math import ceil


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
    invIdxKey: Literal['pStemInvIdx','nonStemInvIdx'],
    operator: QueryOperator = QueryOperator.OR,
):
    and_or_or_list = []
    word_or_list = []
    for word in query_keywords:
        word_or_list = []
        word_or_list.append({ "pmid": word })
        word_or_list.append({ f"{invIdxKey}.title.{word}": { "$exists": True } })
        word_or_list.append({ f"{invIdxKey}.abstract.{word}": { "$exists": True } })
        and_or_or_list.append({"$or": word_or_list})
    
    return {f"${operator.value}": and_or_or_list}

# 動態生成日期篩選條件
def getDateFilter(startDatetime: datetime | None, endDatetime: datetime | None):
    date_filter = {}
    if startDatetime and endDatetime:
        date_filter = {'articleDate': {'$gte': startDatetime, '$lte': endDatetime}}
    elif startDatetime:
        date_filter = {'articleDate': {'$gte': startDatetime}}
    elif endDatetime:
        date_filter = {'articleDate': {'$lte': endDatetime}}
    
    return date_filter

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
        "articleDate":1
    }

    if(full_abstract_InvIdx):
        projection[f"{invIdxKey}.abstract"] = 1
        return projection
    
    for word in query_keywords:
        projection[f"{invIdxKey}.title.{word}.freq"] = 1
        projection[f"{invIdxKey}.abstract.{word}.freq"] = 1
    
    return projection

def search_documents(
    query:str, 
    usePorterStem:bool, 
    startDatetime: datetime | None,
    endDatetime: datetime | None,
    operator: QueryOperator,
    full_abstract_InvIdx:bool = False
):
    stemmer = PorterStemmer() if usePorterStem else None
    query_keywords = get_query_keywords(query, stemmer)
    
    invIdxKey = "pStemInvIdx" if stemmer else "nonStemInvIdx"
    query_filter = getQueryFilter(query_keywords, invIdxKey, operator)
    date_filter = getDateFilter(startDatetime, endDatetime)

    if(date_filter):
        query_filter = {
            "$and": [date_filter, query_filter]
        }
    print(query_filter)

    projection = getProjection(query_keywords, invIdxKey, full_abstract_InvIdx)
    result = db_connection.collection.find(
        query_filter,
        projection
    )
    docs = list(result)
    return docs, query_keywords, stemmer

def search_documents_page(
    query:str, 
    usePorterStem:bool, 
    startDatetime: datetime | None,
    endDatetime: datetime | None,
    operator: QueryOperator,
    page: int,
    pageSize: int,
    full_abstract_InvIdx:bool = False
):
    stemmer = PorterStemmer() if usePorterStem else None
    query_keywords = get_query_keywords(query, stemmer)
    
    invIdxKey = "pStemInvIdx" if stemmer else "nonStemInvIdx"
    query_filter = getQueryFilter(query_keywords, invIdxKey, operator)

    all_word_freq_field = getAllWordFreqField(query_keywords, invIdxKey)
    
    

    projection = getProjection(query_keywords, invIdxKey, full_abstract_InvIdx)
    projection["match_count"] = 1

    date_filter = getDateFilter(startDatetime, endDatetime)

    #計算總數pipline
    count_pipeline = []
    if(date_filter):
        count_pipeline.append({"$match": date_filter})
    count_pipeline.extend([{"$match": query_filter},{"$count": "total"}])

    # 獲取總數
    count_result = list(db_connection.collection.aggregate(count_pipeline))
    totalDocs:int = count_result[0]["total"] if count_result else 0
    
    # 計算總頁數
    totalPages = ceil(totalDocs / pageSize)

    #搜尋pipeline
    pipeline = []
    if(date_filter):
        pipeline.append({"$match": date_filter})
    pipeline.extend([
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
    ])
    
    docs = list(db_connection.collection.aggregate(pipeline))

    return docs, query_keywords, stemmer, totalDocs, totalPages

def invIdxToWordsAndFrequencies(invIdx:dict[str,dict]):
    words = list(invIdx.keys())
    words = sorted(words, key= lambda x: invIdx[x]['freq'],reverse=True)
    frequencies = []
    for word in words:
        frequencies.append(invIdx[word]["freq"])
    return {"words": words, "frequencies": frequencies}

def articleDateToString(docs:list[dict]):
    for doc in docs:
        if(isinstance(doc['articleDate'], datetime)):
            doc['articleDate'] = doc['articleDate'].strftime("%Y-%m-%d")
    return docs