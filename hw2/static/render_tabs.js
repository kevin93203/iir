let usePorterStem = true

function changeUseStem(evt) {
    usePorterStem = evt.target.checked;
}

function createElementFromHTML(htmlString) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');
    return doc.body.firstChild; // 返回解析後的第一個子元素
}

// 資料集分頁manager
const dataSetPaginationManager = new PaginationManager({
    initialPage: 1,
    totalPages: 300,
    elements: {
        container: '#upload-documents',
        list: '#upload-documents-contents',
        prevButton: '#prevButton',
        nextButton: '#nextButton',
        pageInput: '#pageInput',
        totalPages: '#totalPages',
        resultMesssage: '#upload-documents-msg'
    },

    // 自定義獲取數據的函數
    fetchData: async (page) => {
        // 示例：從實際 API 獲取數據
        const response = await fetch(`/api/document_set/?page=${page}&page_size=12`);
        const data = await response.json();
        return {
            items: data.items,
            total: data.total,
            totalPages: data.totalPages
        };
    },

    // 自定義項目渲染
    renderItem: (item) => {
        const {pmid, title, abstract, articleDate, statistics} = item
        const {
            characters_excluding_spaces,
            characters_including_spaces,
            non_ascii_characters,
            non_ascii_words,
            sentences,
            words,
        } = statistics
        const htmlString = `
            <div class='document-wrapper'>
                <div class='document-header'>
                    <div class='pmid'>
                        PMID: ${pmid}
                    </div>
                </div>
                <div class='document-content-container'> 
                    <div class='document-content'>
                        <div class='date-zipf-container'>
                            <p class='articleDate'>${articleDate ? articleDate : ''}</p>
                            <div class='document-zipf' onclick="open_document_zipf('${pmid}')">
                                <img src="/static/chart.svg" alt="chart icon">
                            </div>
                        </div> 
                        <div class='document-stats'>
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
        const element = createElementFromHTML(htmlString);
        return element
    },

    // 事件回調
    onPageChange: (page) => {
        console.log(`Page changed to ${page}`);
    },

    onError: (error) => {
        console.error('Data loading failed:', error);
    },

    onDataLoaded: (data) => {
        console.log('Data loaded successfully:', data);
    }
});

function createNewSearchPaginationManager(query){
    // 搜尋結果分頁manager
    const searchPaginationManager = new PaginationManager({
        elements: {
            container: '#search-result',
            list: '#search-result-contents',
            prevButton: '#search-prevButton',
            nextButton: '#search-nextButton',
            pageInput: '#search-pageInput',
            totalPages: '#search-totalPages',
            resultMesssage: '#search-result-msg',
        },

        noDataErrorMessage: "搜尋不到任何結果！",
        // 自定義獲取數據的函數
        fetchData: async (page) => {
            // 示例：從實際 API 獲取數據
            const response = await fetch(`/api/search?query=${query}&usePorterStem=${usePorterStem}&page=${page}&pageSize=12`);
            const data = await response.json();
            return {
                items: data.items,
                total: data.total,
                totalPages: data.totalPages
            };
        },

        // 自定義項目渲染
        renderItem: (item) => {
            const {pmid, title, abstract, articleDate, match_count} = item
            const htmlString = `
            <div class='document-wrapper search-result-wrapper'>
                <div class='document-header'>
                    <div class='pmid'>
                        PMID: ${pmid}
                    </div>
                    <div class='match-count'>
                        匹配數: ${match_count}
                    </div>
                </div>
                <div class='document-content-container'>
                    <div class='document-content'>
                        <div class='date-zipf-container'>
                            <p class='articleDate'>${articleDate ? articleDate : ''}</p>
                            <div class='document-zipf' onclick="open_document_zipf('${pmid}')">
                                <img src="/static/chart.svg" alt="chart icon">
                            </div>
                        </div> 
                        <h2 class='document-title'>${title}</h2>
                        <p>${abstract}</p>
                    </div>
                </div>
            </div>
            `
            const element = createElementFromHTML(htmlString);
            return element
        },

        // 事件回調
        onPageChange: (page) => {
            console.log(`Page changed to ${page}`);
        },

        onError: (error) => {
            console.error('Data loading failed:', error);
        },

        onDataLoaded: (data) => {
            console.log('Data loaded successfully:', data);
        }
    });

    return searchPaginationManager
}




function drawZipfChart(data, chart_id, content_id = null, title, color='#5470C6'){
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

    // 監聽窗口大小變化，並調整圖表大小
    window.addEventListener('resize', function() {
        myChart.resize();
    });


    // 當targetElement的style(style.display)發生變化時，也會重新resize myChart
    if (content_id !== null){
        // 要監聽的元素
        const targetElement = document.getElementById(content_id);
        // 建立 MutationObserver
        const observer = new MutationObserver((mutationsList) => {
            mutationsList.forEach((mutation) => {
                if (mutation.attributeName === 'style') {
                    myChart.resize();
                }
            });
        });

        // 設置 observer 來監聽屬性變化
        observer.observe(targetElement, { attributes: true, attributeFilter: ['style'] });
    }
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
        drawZipfChart(data['nonStemZipf'], "nonStemZipfChart", "documet-zipf-modal", "Zipf 分布圖")
        drawZipfChart(data['pStemZipf'], "pStemZipfChart", "documet-zipf-modal", "Zipf 分布圖(By Porter Stem)","#FF0000")
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

function drawKeywordZipf(event, keyword_id){
    const query = event.target.value

    // 使用 fetch 查詢 API
    fetch(`/api/search/zipf?query=${query}&usePorterStem=${usePorterStem}`)  // 替換成你自己的 API URL
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();  // 將回傳的資料轉為 JSON 格式
      })
      .then(data => {
        drawZipfChart(
            data, 
            `keyword-${keyword_id}-ZipfChart`, 
            tabcontent_id='tab-zipf-compare',
            `${query} Zipf分布圖`,
        )
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}