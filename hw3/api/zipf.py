from fastapi import APIRouter
from datetime import datetime, date
from utils.model import QueryOperator
from utils import db_connection
from utils.query_utils import (
    invIdxToWordsAndFrequencies,
    search_documents
)

zipf_router = APIRouter()

@zipf_router.get("/api/search/zipf")
async def search_zipf(
    query:str, 
    usePorterStem:bool=True,
    startDate: date | None = None,
    endDate: date | None = None,
    operator: QueryOperator = QueryOperator.OR,
):
    if not query: return
    startDatetime = datetime.combine(startDate, datetime.min.time()) if startDate else None
    endDatetime = datetime.combine(endDate, datetime.min.time()) if endDate else None
    docs, _, _ = search_documents(query, usePorterStem, startDatetime, endDatetime, operator,True)
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

@zipf_router.get("/api/document/zipf")
async def document_zipf(pmid:str):
    doc:dict | None = db_connection.collection.find_one(
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