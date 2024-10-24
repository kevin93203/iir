let usePorterStem = true
let startDate = ''
let endDate = ''

function changeUseStem(evt) {
    usePorterStem = evt.target.checked;
}

function changeStartDate(evt){
    startDate = evt.target.value;
}

function changeEndDate(evt){
    endDate = evt.target.value;
}

function createElementFromHTML(htmlString) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');
    return doc.body.firstChild; // 返回解析後的第一個子元素
}

function close_delete_confirm(){
    const modal = document.querySelector('#delete-confirm-modal');
    modal.style.display = 'none';
}

function openDetelConfirmModal(pmid){
    const modal = document.getElementById("delete-confirm-modal")
    const modal_content = document.getElementById("delete-modal-content")
    modal_content.innerHTML = ""
    modal_content.insertAdjacentHTML(
        'beforeend',
        `
        <span class="close" onclick="close_delete_confirm()">&times;</span>
        <p id="delete-confirm-text">你確定要刪除PMID為<span style="color:#4285F4;font-weight: 500;">${pmid}</span>的文件嗎?</p>
        <div class="delete-confirm-btn-container">
            <button class="confirm-btn" onclick="deleteDocument(${pmid})">確定</button>
            <button class="cancel-btn" onclick="close_delete_confirm()">取消</button>
        </div>
        `
    )
    modal.style.display = "flex";
}

async function deleteDocument(pmid) {
    const response = await fetch(
        `/api/delete?pmid=${pmid}`,
        {method: 'DELETE'}
    );
    const data = await response.json();
    console.log(data)
    dataSetPaginationManager.restore(true);
    close_delete_confirm()
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
                    <div class='delete' onclick='openDetelConfirmModal(${pmid})'>
                        <img src="/static/delete.svg" alt="delete icon">
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
            let url = ''
            if(startDate && endDate) {
                url = `/api/search?startDate=${startDate}&endDate=${endDate}&query=${query}&usePorterStem=${usePorterStem}&page=${page}&pageSize=12&operator=${operator}`
            } else if (startDate) {
                url = `/api/search?startDate=${startDate}&query=${query}&usePorterStem=${usePorterStem}&page=${page}&pageSize=12&operator=${operator}`
            } else if (endDate) {
                url = `/api/search?endDate=${endDate}&query=${query}&usePorterStem=${usePorterStem}&page=${page}&pageSize=12&operator=${operator}`
            } else {
                url = `/api/search?query=${query}&usePorterStem=${usePorterStem}&page=${page}&pageSize=12&operator=${operator}`
            }    
            const response = await fetch(url);
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




function drawZipfChart(data, chart_id, content_id = null, title, color='#5470C6', log=false){
    // 基于准备好的 dom，初始化 echarts 实例
    const myChart = echarts.init(document.getElementById(chart_id));
    let {words, frequencies} = data
    if(log){
        frequencies = frequencies.map(freq => Math.log10(freq))
    }
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


let tableManagers = [null, null]
let cloudManagers = [null, null]

function drawKeywordZipf(event, keyword_id){
    const query = event.target.value

    let url = ''
    if(startDate && endDate) {
        url = `/api/search/zipf?startDate=${startDate}&endDate=${endDate}&query=${query}&usePorterStem=${usePorterStem}&operator=${operator}`
    } else if (startDate) {
        url = `/api/search/zipf?startDate=${startDate}&query=${query}&usePorterStem=${usePorterStem}&operator=${operator}`
    } else if (endDate) {
        url = `/api/search/zipf?endDate=${endDate}&query=${query}&usePorterStem=${usePorterStem}&operator=${operator}`
    } else {
        url = `/api/search/zipf?query=${query}&usePorterStem=${usePorterStem}&operator=${operator}`
    }    

    // 使用 fetch 查詢 API
    fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();  // 將回傳的資料轉為 JSON 格式
      })
      .then(data => {
        if(tableManagers[keyword_id-1]){
            tableManagers[keyword_id-1].removeSelectChangeListener();
        }
        tableManagers[keyword_id-1] = new WordRankTableManager(data, keyword_id)

        // $(`#keyword-${keyword_id}-WordCloud`).JQCloud(processData(data),{
        //     autoResize: true
        // });
        $(`#keyword-${keyword_id}-WordCloud`).jQCloud('destroy')

        $(`#keyword-${keyword_id}-WordCloud`).jQCloud(processData(data), {
            autoResize: true,  // jQCloud 會自動處理 resize
            classPattern: null,
            colors: [
                "#362F9E",  // 更深的起始色
                "#4338CA",
                "#4F46E5",
                "#5651E8",
                "#625FE9",
                "#6366F1",
                "#7673F3",
                "#8885F5",
                "#9A97F7",
                "#A7A6F2"   // 適中的結束色
            ],
            fontSize: {
                from: 0.15,
                to: 0.02
            },
        })

        drawZipfChart(
            data, 
            `keyword-${keyword_id}-ZipfChart`, 
            tabcontent_id='tab-zipf-compare',
            `${query} Zipf分布圖`,
        )
        drawZipfChart(
            data, 
            `keyword-${keyword_id}-ZipfChart-log`, 
            tabcontent_id='tab-zipf-compare',
            `${query} Zipf Log分布圖`,
            '#FF0000',
            true
        )
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}