from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.stem import PorterStemmer
import string
from collections import defaultdict
import re
import utils.model as model

# nltk.download('punkt')
# nltk.download('stopwords')

def custom_tokenize(text):
    return re.findall(r'\b\w+\b|[^\w\s]',text)

def init_word_index_obj():
    return {
        "position": [],
        "freq": 0
    }

def build_inverted_index(document ,stemmer:PorterStemmer | None  = None):
    stop_words = set(stopwords.words('english'))
    inverted_index = defaultdict(dict)  # {stemmed_word: [(doc_id, position), ...]}

    words_in_doc = custom_tokenize(document)
    for position, word in enumerate(words_in_doc):
        word_clean = word.lower().strip(string.punctuation)
        # 檢查是否為特殊術語（如"COVID-19"）
        if re.match(r'^[A-Za-z]+(?:-\d+)+$', word):
            stemmed_word = word.lower()  # 對特殊術語，我們只轉換為小寫，不進行詞幹提取
            # 同時為術語的第一部分建立索引
            first_part = word.split('-')[0].lower()
            if(stemmed_word not in inverted_index):
                inverted_index[stemmed_word] = init_word_index_obj()
            if(first_part not in inverted_index):
                inverted_index[first_part] = init_word_index_obj()
            
            inverted_index[stemmed_word]["position"].append(position)
            inverted_index[stemmed_word]["freq"] = inverted_index[stemmed_word]["freq"] + 1
            
            inverted_index[first_part]["position"].append(position)
            inverted_index[first_part]["freq"] = inverted_index[first_part]["freq"] + 1
        else:
            stemmed_word = stemmer.stem(word_clean) if stemmer else word_clean
            if stemmed_word not in stop_words and stemmed_word:
                if(stemmed_word not in inverted_index):
                    inverted_index[stemmed_word] = init_word_index_obj()
                inverted_index[stemmed_word]["position"].append(position)
                inverted_index[stemmed_word]["freq"] = inverted_index[stemmed_word]["freq"] + 1
    
    return inverted_index

def build_inverted_indexes(documents: list[str]):
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    inverted_index = defaultdict(list)  # {stemmed_word: [(doc_id, position), ...]}

    for doc_id, document in enumerate(documents):
        words_in_doc = custom_tokenize(document)
        for position, word in enumerate(words_in_doc):
            word_clean = word.lower().strip(string.punctuation)
            # 檢查是否為特殊術語（如"COVID-19"）
            if re.match(r'^[A-Za-z]+(?:-\d+)+$', word):
                stemmed_word = word.lower()  # 對特殊術語，我們只轉換為小寫，不進行詞幹提取
                inverted_index[stemmed_word].append((doc_id, position))
                # 同時為術語的第一部分建立索引
                first_part = word.split('-')[0].lower()
                inverted_index[first_part].append((doc_id, position))
            else:
                stemmed_word = stemmer.stem(word_clean)
                if stemmed_word not in stop_words and stemmed_word:
                    inverted_index[stemmed_word].append((doc_id, position))

    return inverted_index

def query_keywords(query:str, stemmer:PorterStemmer):
    stop_words = set(stopwords.words('english'))

    # 預處理查詢詞
    query_words = custom_tokenize(query.lower())
    filtered_query = [stemmer.stem(word) for word in query_words if word not in stop_words and word not in string.punctuation]

    return filtered_query

def get_ranking_by_index(documents_match_count: list[int], titles_match_count:list[int] ):
    total_count = [x + y for x, y in zip(documents_match_count, titles_match_count)]

    # 由大到小排序並保留原索引
    rank = sorted(enumerate(total_count), key=lambda x: x[1], reverse=True)

    return rank 

def highlight_query(query: str, data: model.Data):
    stemmer = PorterStemmer()
    filtered_query = query_keywords(query, stemmer)
    highlighted_documents, documents_match_count =  \
        highlight_query_in_documents(
            filtered_query, 
            data.documents, 
            data.inverted_index,
            stemmer
        )
    
    highlighted_titles, titles_match_count =  \
        highlight_query_in_documents(
            filtered_query, 
            data.titles, 
            data.inverted_index_titles,
            stemmer
        )
    rank = get_ranking_by_index(documents_match_count, titles_match_count)

    return filtered_query, highlighted_documents, highlighted_titles, rank

def highlight_query_in_documents(
        filtered_query: list[str], 
        documents: list[str], 
        inverted_index: dict[str, list[tuple[int, int]]],
        stemmer: PorterStemmer
):
    # 找到包含查询词的文档ID
    doc_ids_to_highlight = set()
    for term in filtered_query:
        if term in inverted_index:
            doc_ids_to_highlight.update([doc_id for doc_id, _ in inverted_index[term]])

    highlighted_documents = []
    match_count = [0] * len(documents)

    # 仅处理包含查询词的文档
    for doc_id, document in enumerate(documents):
        if doc_id in doc_ids_to_highlight:
            # 使用正则表达式来分割文档，保留标点符号
            words_in_doc = custom_tokenize(document)

            highlighted_doc = document
            for word in words_in_doc:
                word_clean = word.lower().strip(string.punctuation)
                stemmed_word = stemmer.stem(word_clean)
                if stemmed_word in filtered_query:
                    # 使用正则表达式来替换匹配的单词，保持原有的大小写和标点
                    # 确保没有已经标记的词
                    highlighted_doc = re.sub(r'(?<!<mark>)\b' + re.escape(word) + r'\b(?!<\/mark>)', 
                                             f"<mark>{word}</mark>", 
                                             highlighted_doc)
                    match_count[doc_id] = match_count[doc_id] + 1
            
            highlighted_documents.append(highlighted_doc)
        else:
            highlighted_documents.append(None)  # 未命中查询的文档保持不变

    return highlighted_documents, match_count

def document_statistics(document):
    # 字符數 (including spaces)
    num_characters_including_spaces = len(document)
    
    # 字符數 (excluding spaces)
    num_characters_excluding_spaces = len(document.replace(" ", ""))
    
    # 單詞數 (去除標點符號)
    words = custom_tokenize(document)
    words = [word for word in words if word not in string.punctuation]  # 去除標點符號
    num_words = len(words)
    
    # 句子數
    num_sentences = len(sent_tokenize(document))
    
    # 非ASCII字符數
    non_ascii_characters = [char for char in document if ord(char) > 127]
    num_non_ascii_characters = len(non_ascii_characters)
    
    # 非ASCII單詞數 (去除標點符號)
    non_ascii_words = [word for word in words if any(ord(char) > 127 for char in word)]
    num_non_ascii_words = len(non_ascii_words)

    return {
        'characters_including_spaces': num_characters_including_spaces,
        'characters_excluding_spaces': num_characters_excluding_spaces,
        'words': num_words,
        'sentences': num_sentences,
        'non_ascii_characters': num_non_ascii_characters,
        'non_ascii_words': num_non_ascii_words
    }

# 計算每個document的字元數、單詞數和句子數 (去除標點符號)
def documents_statistics(documents):
    stats = []
    for document in documents:
        stats.append(document_statistics(document))

    return stats