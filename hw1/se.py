import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
import string
from collections import defaultdict

nltk.download('punkt')
nltk.download('stopwords')

# 構建倒排索引的函數
def build_inverted_index(documents):
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    inverted_index = defaultdict(list)  # {stemmed_word: [(doc_id, position), ...]}

    for doc_id, document in enumerate(documents):
        words_in_doc = word_tokenize(document)
        for position, word in enumerate(words_in_doc):
            word_clean = word.lower().strip(string.punctuation)
            stemmed_word = stemmer.stem(word_clean)
            if stemmed_word not in stop_words and stemmed_word:
                inverted_index[stemmed_word].append((doc_id, position))

    return inverted_index

# 使用倒排索引進行查詢並高亮顯示
def highlight_query_in_documents(query:str, documents:list[str], inverted_index:dict[str, list[tuple[int,int]]]):
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))

    # 預處理查詢詞
    query_words = word_tokenize(query.lower())
    filtered_query = [stemmer.stem(word) for word in query_words if word not in stop_words and word not in string.punctuation]

    # 找到包含查詢詞的文件ID
    doc_ids_to_highlight = set()
    for term in filtered_query:
        if term in inverted_index:
            doc_ids_to_highlight.update([doc_id for doc_id, _ in inverted_index[term]])

    highlighted_documents = []
    
    # 僅處理包含查詢詞的文件
    for doc_id, document in enumerate(documents):
        if doc_id in doc_ids_to_highlight:
            words_in_doc = word_tokenize(document)
            highlighted_doc = []

            for position, word in enumerate(words_in_doc):
                word_clean = word.lower().strip(string.punctuation)
                stemmed_word = stemmer.stem(word_clean)
                if stemmed_word in filtered_query:
                    highlighted_doc.append(f"<mark>{word}</mark>")  # 高亮顯示匹配的單詞
                else:
                    highlighted_doc.append(word)

            highlighted_documents.append(' '.join(highlighted_doc))
        else:
            highlighted_documents.append(None)  # 未命中查詢的文件不變

    return highlighted_documents

# 計算每個document的字元數、單詞數和句子數 (去除標點符號)
def document_statistics(documents):
    stats = []
    for document in documents:
        # 字符數 (including spaces)
        num_characters_including_spaces = len(document)
        
        # 字符數 (excluding spaces)
        num_characters_excluding_spaces = len(document.replace(" ", ""))
        
        # 單詞數 (去除標點符號)
        words = word_tokenize(document)
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

        stats.append({
            'characters_including_spaces': num_characters_including_spaces,
            'characters_excluding_spaces': num_characters_excluding_spaces,
            'words': num_words,
            'sentences': num_sentences,
            'non_ascii_characters': num_non_ascii_characters,
            'non_ascii_words': num_non_ascii_words
        })
    
    return stats

def query_keywords(query:str):
    words = word_tokenize(query)
    words = [word for word in words if word not in string.punctuation]  # 去除標點符號
    return words

if __name__ == '__main__':
    # 測試數據
    documents = [
        "The core technology of a full-text search engine is the inverted index.",
        "Search engines use various algorithms to index and rank pages.",
        "The inverted index is critical to efficient search functionality.",
        "测试非ASCII字符和单词。"
    ]

    query = "search engine"

    # 構建倒排索引
    inverted_index = build_inverted_index(documents)

    print(inverted_index)

    # 使用倒排索引進行查詢並高亮顯示
    highlighted_documents = highlight_query_in_documents(query, documents, inverted_index)

    # 輸出高亮結果
    for i, doc in enumerate(highlighted_documents):
        print(f"Document {i+1}:\n{doc}\n")

    # 計算每個document的字符數、單詞數和句子數
    stats = document_statistics(documents)

    for i, stat in enumerate(stats):
        print(f"Document {i+1} stats:")
        print(f"Characters (including spaces): {stat['characters_including_spaces']}")
        print(f"Characters (excluding spaces): {stat['characters_excluding_spaces']}")
        print(f"Words (excluding punctuation): {stat['words']}")
        print(f"Sentences: {stat['sentences']}")
        print(f"Non-ASCII characters: {stat['non_ascii_characters']}")
        print(f"Non-ASCII words: {stat['non_ascii_words']}\n")
