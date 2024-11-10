from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.search import search_router
from api.zipf import zipf_router
from api.dataset_operation import dataset_operation_router
from api.related_doc import related_doc_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(zipf_router)
app.include_router(dataset_operation_router)
app.include_router(related_doc_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
