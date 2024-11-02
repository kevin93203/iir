from gensim.models import Word2Vec

# 加载普通格式的Word2Vec模型
model = Word2Vec.load('./model/pubmed_word2vec.model')

def generate(user_input, model=model, topn=5):
    try:
        related_keywords = model.wv.most_similar(user_input, topn=topn)
        return [keyword for keyword, _ in related_keywords]
    except KeyError:
        # 如果用戶輸入的關鍵字不在模型的詞彙中
        return []

if __name__ == '__main__':
    # 用戶輸入的查詢關鍵字
    user_input = 'korea'
    related_keywords = generate(user_input)

    print("與 '{}' 相關的關鍵詞: {}".format(user_input, related_keywords))