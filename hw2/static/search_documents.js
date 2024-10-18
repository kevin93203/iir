let search_history = []

function go_to_search_result(){
    // 取得你要滾動到的元素
    const element = document.getElementById('search-result');

    // 使用 scrollIntoView 滾動到該元素
    element.scrollIntoView({
        behavior: 'smooth', // 平滑滾動 (也可以設為 'auto')
        block: 'start',     // 滾動到元素的頂部 ('end' 會滾動到底部)
        inline: 'nearest'   // 水平滾動行為
    });
}

async function search() {
    const query = document.getElementById('search').value;
    if (!query) {
        alert("搜尋文字不能為空白！");
        return;
    }
    try {
        const response = await fetch(`/api/search/?query=${query}&usePorterStem=true`);
        if (response.ok) {
            const data = await response.json(); // 取得 JSON 資料
            console.log(data)
            add_history(data)
            render_search_result(data)
            document.querySelector("#tab-search-result-btn").click()
            go_to_search_result()

        } else {
            const errorData = await response.json(); // 取得錯誤的 JSON 資料（如果有的話）
            alert(`Failed to search documents`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while searching.');
    }
}

function add_history(data){
    search_history.push(data)
    const history_no = search_history.length - 1
    document.getElementById("search-history-keywords").insertAdjacentHTML(
        'beforeend',
        `
            <p 
                id="history-${history_no}"
                class="history"
                onclick="
                    render_search_result(search_history[${history_no}]);
                    go_to_search_result();
                "
            >
                ${data['query']}
            </p>
        `
    )
}