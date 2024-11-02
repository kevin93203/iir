## PubMed 文件搜尋引擎
### 功能簡介
1. 搜尋框
    - 可以輸入關鍵字或句子做搜尋，比對內容包含標題、摘要、PMID
    - 可以勾選是否要提取詞幹 
    - 可以篩選日期

2. 搜尋結果
    - 分頁顯示搜尋結果，包含PMID、日期、標題、摘要、齊夫分布圖
    - 結果依照出現關鍵字次數由多到少排列
    - 關鍵字以高量顯示
    - 保留搜尋紀錄

3. 資料集
    - 分頁顯示所有資料集，包含PMID、日期、標題、摘要、各統計值、齊夫分布圖
    - 可上傳及刪除文件(僅支援PubMed XML格式)

4. 齊夫分布圖
    - 可以輸入兩組關鍵字來比對兩組的齊夫分布圖
    - 關鍵字比對內容包含標題、摘要、PMID

### 實作細節
1. 使用web網頁開發
2. 前後端分離，後端API使用python fastapi，前端使用原生javascript、css
3. 使用正則表達式提取詞，再使用nltk內的PorterStemmer提取詞幹，並且去除stop words和punctuation
4. 對所有文件建立Inverted Index，（詞、詞出現在第幾個字、出現次數）
5. 資料存放於MongoDB
6. 使用ECharts繪製圖表

### 執行方式
1. 啟用MongoDB
2. 創建.env檔並且輸入MongoDB的host和port
3. ```shell
    pip install -r requirements.txt
    ```
4. ```shell
    python main.py
    ```
5. 開啟網址: http://localhost:8000