# PubMed, Twitter 文件搜尋引擎
## 功能簡介
1. 可以上傳檔案，檔案類型支援Pubmed的xml格式和twitter的json格式
2. 對所有上傳文件做統計包含characters (including spaces)、characters (excluding spaces)、words、sentences、non-ASCII characters、non-ASCII words，並且顯示文件原文
3. 提供搜尋框讓用者可以輸入關鍵字或句子做搜尋，搜尋後會顯示文章內有包含關鍵字的文件，並且關鍵字出現的位置會以高亮提示
4. 保存搜尋紀錄，使用者可一鍵查看過去的搜尋結果
5. 顯示搜尋的關鍵字原文、詞幹、詞幹數（關鍵字字數）

## 操作流程
1. 點選迴紋針圖示上傳檔案（可多檔案同時上傳）
2. 查看上傳的文件內文和各統計量
3. 到搜尋框輸入關鍵字查詢
4. 查看搜尋結果
5. 點選搜尋紀錄可查看過去搜尋的結果

## 實作細節
1. 使用web網頁開發
2. 前後端分離，後端API使用python fastapi，前端使用原生javascript、css
3. 使用正則表達式提取詞，再使用nltk內的PorterStemmer提取詞幹，並且去除stop words和punctuation
4. 對所有文件建立Inverted Index，（詞、文件編號、詞出現在第幾個字），用以快速查找所有文件
4. 尚未使用DB做任何資料存取，資料全部存取在網頁的memory（JS變數）

## 執行方式
1. 
```shell
cd hw1
```

2. 
```shell
pip install -r requirements.txt
```

3.
```shell
python main.py
```

4. 開啟網址: http://localhost:8000