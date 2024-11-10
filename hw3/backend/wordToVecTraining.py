from gensim.models import Word2Vec
from utils import db_connection
from pymongo.collection import Collection
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# 初始化NLTK的停用詞
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))

# 設定每批提取的文檔數量
batch_size = 1000

class MongoCorpus:
    def __init__(self, collection:Collection, batch_size:int):
        self.collection = collection
        self.batch_size = batch_size
        self.total_documents = collection.count_documents({})
    
    def __iter__(self):
        skip = 0
        while skip < self.total_documents:
            documents = self.collection.find({},{'abstract':1}).skip(skip).limit(self.batch_size)
            for doc in documents:
                content:str = doc['abstract']
                # 分詞並處理文本
                tokens = word_tokenize(content.lower())  # 轉換為小寫並分詞
                filtered_tokens = [
                    word for word in tokens 
                    if word not in stop_words and word not in string.punctuation
                ]  # 過濾停用詞和標點符號
                yield filtered_tokens  # 生成處理後的分詞內容
            skip += self.batch_size


# 創建MongoCorpus實例
corpus = MongoCorpus(db_connection.collection, batch_size=1000)

# 使用MongoCorpus訓練Word2Vec模型
model = Word2Vec(sentences=corpus, vector_size=100, window=5, min_count=1, workers=4)

# 保存模型
model.save("./model/pubmed_word2vec.model")
