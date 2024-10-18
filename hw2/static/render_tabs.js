function render_document_set(data) {
    const documents_results = document.getElementById("upload-documents-contents");
    documents_results.innerHTML = '';
    
    data.forEach(item => {
        const {pmid, title, abstract, dateCompleted, statistics} = item
        const {
            characters_excluding_spaces,
            characters_including_spaces,
            non_ascii_characters,
            non_ascii_words,
            sentences,
            words,
        } = statistics
        documents_results.insertAdjacentHTML(
            'beforeend',
            `
            <div class='document-wrapper'>
                <div class='document-content-container'> 
                    <div class='document-filename'>${pmid}</div>
                    <div class='document-content'>
                        <div class='document-stats'>
                            <div class='document-zipf' onclick="open_document_zipf('${pmid}')">
                                <img src="/static/chart.svg" alt="chart icon">
                            </div>
                            <div>characters (including spaces): <strong>${characters_including_spaces}</strong></div>
                            <div>characters (excluding spaces): <strong>${characters_excluding_spaces}</strong></div>
                            <div>words: <strong>${words}</strong></div>
                            <div>sentences: <strong>${sentences}</strong></div>
                            <div>non-ASCII characters: <strong>${non_ascii_characters}</strong></div>
                            <div>non-ASCII words: <strong>${non_ascii_words}</strong></div>
                        </div>
                        <h3 class='document-title'>${title}</h3>
                        <p>${abstract}</p>
                    </div>
                </div>
            </div>
            `
        );
    });
    toggleAllElements()
}



function drawZipfChart(data, chart_id, title, color='#5470C6'){
    // 基于准备好的 dom，初始化 echarts 实例
    const myChart = echarts.init(document.getElementById(chart_id));
    const {words, frequencies} = data

    // 指定圖表的配置項和數據
    const option = {
        title: {
            text: title
        },
        tooltip: {
            trigger: 'axis'
        },
        xAxis: {
            type: 'category',
            name: '詞',
            data: words
        },
        yAxis: {
            // 確保 Y 軸刻度為整數
            minInterval: 1,
            type: 'value',
            name: '頻率'
        },
        series: [
            {
                name: '詞頻',
                type: 'line',  // 使用折線圖顯示
                data: frequencies,
                smooth: true,  // 讓線條平滑
                // 設置線條顏色
                lineStyle: {
                    color: color, // 線條顏色，紅色
                },
                // 設置每個點的顏色
                itemStyle: {
                    color: color, // 點的顏色，藍色
                }
            }
        ]
    };

    // 使用指定的配置和數據來顯示圖表
    myChart.setOption(option);
}

function open_document_zipf(pmid){
    const modal = document.querySelector("#documet-zipf-modal")
    // 使用 fetch 查詢 API
    fetch(`/api/document/zipf?pmid=${pmid}`)  // 替換成你自己的 API URL
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();  // 將回傳的資料轉為 JSON 格式
      })
      .then(data => {
        drawZipfChart(data['nonStemZipf'], "nonStemZipfChart", "Zipf 分布圖")
        drawZipfChart(data['pStemZipf'], "pStemZipfChart", "Zipf 分布圖(By Porter Stem)","#FF0000")
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
    modal.style.display = "flex";
}

function close_document_zipf(){
    const modal = document.querySelector('#documet-zipf-modal');
    modal.style.display = 'none';
}

function render_search_result(data) {
    const {query, query_keywords, docs} = data
    const documents_results = document.getElementById("search-result-contents");
    documents_results.innerHTML = '';
    const search_content = document.getElementById("search-content")
    search_content.innerHTML = '';
    search_content.insertAdjacentHTML(
        'beforeend',
        `
            <div>搜尋內容: ${query}</div>
            <div>關鍵字: ${query_keywords.join(", ")}</div>
            <div>關鍵字字數: ${query_keywords.length}</div>
        `
    )
    if(docs.length === 0){
        documents_results.innerHTML = "<p>搜尋不到任何結果！<p>";
        toggleAllElements();
    } 
    else {
        let i = 1
        docs.forEach(item => {
            const {pmid, title, abstract, dateCompleted, match_count} = item
            documents_results.insertAdjacentHTML(
                'beforeend',
                `
                <div class='document-wrapper'>
                    <div class='document-ranking'>
                        <div class='rank'> 
                            ${i}
                        </div>
                        <div class='filename'>
                            ${pmid}
                        </div>
                        <div class='match-count'>
                            匹配數: ${match_count}
                        </div>
                    </div>
                    <div class='document-content-container'>
                        <div class='document-content'>
                            <h2 class='document-title'>${title}</h2>
                            <p>${abstract}</p>
                        </div>
                    </div>
                </div>
                `
            );
            i++;
        })
        toggleAllElements();
    }
}

function drawKeywordZipf(event, keyword_id){
    console.log(event.target.value)
    console.log(keyword_id)
    const query = event.target.value

    // 使用 fetch 查詢 API
    fetch(`/api/search/zipf?query=${query}&usePorterStem=true`)  // 替換成你自己的 API URL
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();  // 將回傳的資料轉為 JSON 格式
      })
      .then(data => {
        drawZipfChart(data, `keyword-${keyword_id}-ZipfChart`, `${query} Zipf分布圖`)
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}