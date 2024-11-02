from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from api.search import search_router
from api.zipf import zipf_router
from api.dataset_operation import dataset_operation_router

app = FastAPI()
app.include_router(search_router)
app.include_router(zipf_router)
app.include_router(dataset_operation_router)

# 配置静态文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")

# 回傳 HTML 頁面
@app.get("/", response_class=HTMLResponse)
async def read_html():
    file_path = os.path.join("static", "index.html")
    return HTMLResponse(open(file_path, encoding='utf-8').read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
