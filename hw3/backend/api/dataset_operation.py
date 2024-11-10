from fastapi import APIRouter, UploadFile, File, Query
from typing import List
import pymongo
from math import ceil

import utils.file_process as file_process
import utils.db_connection as db_connection
from utils.query_utils import (
    invIdxToWordsAndFrequencies,
    articleDateToString,
)
from utils.model import PaginatedResponse

dataset_operation_router = APIRouter()

# 接收上傳的檔案 (支援多檔案上傳)
@dataset_operation_router.post("/api/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    docs = []
    # 處理檔案，限制檔案類型為 json 或 xml
    for file in files:
        file_content = await file.read()  # 讀取檔案內容        
        if file.content_type == "text/xml":
            # 解析 XML 檔案
            try:
                doc = await file_process.analysis(file_content)
                docs.append(doc)
            except Exception:
                return {"error": f"Failed to parse XML file: {file.filename}"}
        else:
            return {"error": f"Unsupported file type: {file.filename}"}
        
    batch_ops = []    
    for doc in docs:
        if(doc == None): continue
        # 生成 upsert 操作（如果匹配则更新，不匹配则插入）
        operation = pymongo.UpdateOne(
            {'pmid': doc['pmid']},  # 假设文档的 `_id` 字段为唯一键
            {'$set': doc},        # 如果匹配到已有的文档，则更新整个文档
            upsert=True           # 如果没有匹配到，则插入文档
        )
        batch_ops.append(operation)

    if batch_ops:
        result = db_connection.collection.bulk_write(batch_ops)
        return {
            "inserted_count": result.inserted_count, 
            "modified_count": result.modified_count,
            "upserted_count": result.upserted_count
        }

    else:
        return {"inserted_count": 0, "modified_count": 0,"upserted_count": 0}

        

# 接收上傳的檔案 (支援多檔案上傳)
@dataset_operation_router.post("/api/upload2/")
async def upload_files2(files: List[UploadFile] = File(...)):
    docs = []
    # 處理檔案，限制檔案類型為xml
    for file in files:
        docs.append(await file_process.analysis(file))
    
    return docs
    
@dataset_operation_router.delete("/api/delete")
async def delete_document(pmid:str):
    reseult = db_connection.collection.delete_one({"pmid": pmid})
    return {"deleted_count": reseult.deleted_count}

@dataset_operation_router.get("/api/document_set/")
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
            "articleDate":1,
            "pStemInvIdx.abstract":1,
            "nonStemInvIdx.abstract":1,
    }

    # 計算總數量
    totalDocs = db_connection.collection.count_documents(query_filter)
    
    # 計算總頁數
    totalPages = ceil(totalDocs / pageSize)
    
    # 計算跳過的數量
    skip = (page - 1) * pageSize
    
    # 查詢數據
    docs = list(db_connection.collection
        .find(query_filter,projection)
        .sort('updated_at', pymongo.DESCENDING)
        .skip(skip)
        .limit(pageSize))

    # invIdxToWordsAndFrequencies(docs[0]['pStemInvIdx']['abstract'])

    for doc in docs:
        doc['pStemZipf'] = invIdxToWordsAndFrequencies(doc['pStemInvIdx']['abstract'])
        doc['nonStemZipf'] = invIdxToWordsAndFrequencies(doc['nonStemInvIdx']['abstract'])
    
    #docs濾除invIdx
    docs = [{k: v for k, v in d.items() if k not in ["pStemInvIdx","nonStemInvIdx"]} for d in docs]


    # 將articleDate轉為"yyyy-mm-dd""
    docs = articleDateToString(docs)

    return PaginatedResponse(
        items=docs,
        total=totalDocs,
        totalPages=totalPages,
        currentPage=page,
        pageSize=pageSize
    )