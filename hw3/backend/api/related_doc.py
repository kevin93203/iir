from fastapi import APIRouter
from gensim.models.doc2vec import Doc2Vec
from utils import db_connection

# 載入模型
model = Doc2Vec.load("./model/doc2vec_model.d2v")


related_doc_router = APIRouter()

# 查找與指定文檔最相似的文檔
@related_doc_router.get("/api/related_doc")
def find_similar_documents(pmid:str, top_n:int=4):
    # 獲取指定文檔的向
    doc_vector = model.dv[pmid]
    
    # 找到最相似的文檔
    similar_docs = model.dv.most_similar([doc_vector], topn=top_n)

    pmids = [tag  for tag, _ in similar_docs[1:]]

    docs = list(db_connection.collection.find({"pmid":{"$in": pmids}},{"_id":0, "pmid":1, "title":1}))
    
    # 返回相似文檔的
    return docs