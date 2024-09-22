from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import json
import xml.etree.ElementTree as ET
import se
from pydantic import BaseModel

class Data (BaseModel):
    filenames: list[str]
    documents: list[str]
    inverted_index:dict[str, list[tuple[int,int]]]

app = FastAPI()

# 配置静态文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")

# 回傳 HTML 頁面
@app.get("/", response_class=HTMLResponse)
async def read_html():
    file_path = os.path.join("static", "index.html")
    return HTMLResponse(open(file_path).read())

# 接收上傳的檔案 (支援多檔案上傳)
@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_file_names = []
    processed_data = {}
    documents = []

    # 處理檔案，限制檔案類型為 json 或 xml
    for file in files:
        file_content = await file.read()  # 讀取檔案內容
        print(file.content_type)
        if file.content_type == "application/json":
            # 解析 JSON 檔案
            try:
                json_data:dict = json.loads(file_content)
                print(json_data)
                text = json_data.get("text")
                print(text)
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
            except ET.ParseError:
                return {"error": f"Failed to parse XML file: {file.filename}"}
        else:
            return {"error": f"Unsupported file type: {file.filename}"}

        uploaded_file_names.append(file.filename)
    inverted_index = se.build_inverted_index(documents)
    stats = se.document_statistics(documents)
    return {
        "filenames": uploaded_file_names, 
        "documents": documents, 
        "inverted_index": inverted_index, 
        "statistics":stats,
        "search_history":[],
    }

@app.post("/search/")
async def search_documents(query:str, data:Data):
    highlighted_documents = se.highlight_query_in_documents(query, data.documents, data.inverted_index)
    query_keywords = se.query_keywords(query)
    return {
        "query": query,
        "query_keywords": query_keywords,
        "highlighted_documents": highlighted_documents
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
