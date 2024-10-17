from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import json
import xml.etree.ElementTree as ET
import se
import file_process
import model
from dotenv import load_dotenv


app = FastAPI()

# 配置静态文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")

#load env
load_dotenv(override=True)

MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_PORT = os.getenv('MONGODB_PORT')

#mongo uri
mongo_uri = f'mongodb://{MONGODB_HOST}:{MONGODB_PORT}'

# 回傳 HTML 頁面
@app.get("/", response_class=HTMLResponse)
async def read_html():
    file_path = os.path.join("static", "index.html")
    return HTMLResponse(open(file_path, encoding='utf-8').read())

# 接收上傳的檔案 (支援多檔案上傳)
@app.post("/upload/")
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
@app.post("/upload2/")
async def upload_files2(files: List[UploadFile] = File(...)):
    docs = []
    # 處理檔案，限制檔案類型為xml
    for file in files:
        docs.append(await file_process.analysis(file))
    
    return docs
    
    

@app.post("/search/")
async def search_documents(query:str, data:model.Data):
    keywords, highlighted_documents, highlighted_titles, rank = se.highlight_query(query, data)
    return {
        "query": query,
        "query_keywords": keywords,
        "highlighted_documents": highlighted_documents,
        "highlighted_titles": highlighted_titles,
        "rank": rank
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
