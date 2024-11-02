let search_history = []
const history_pagination_managers = []
let current_history_idx = null;

async function search(query=null) {
    if(query === null){
        query = document.getElementById('search').value;
    }
    // 停止監聽先前的歷史查詢
    if(current_history_idx!==null){
        history_pagination_managers[current_history_idx].unbindEvents();
    }
    if (!query) {
        console.log("searchPaginationManager")
        alert("搜尋文字不能為空白！");
        return;
    }
    try {
        searchPaginationManager = createNewSearchPaginationManager(query)
        history_pagination_managers.push(searchPaginationManager)
        current_history_idx = history_pagination_managers.length - 1
        add_history(current_history_idx, query)
        switch_current_history(current_history_idx)
        document.querySelector("#tab-search-result-btn").click()
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while searching.');
    }
}

function switchSearchReuslt(history_no){
    switch_current_history(history_no)

    // 停止監聽先前的歷史查詢
    if(current_history_idx!==null){
        history_pagination_managers[current_history_idx].unbindEvents();
    }

    // 更新目前的histroy index
    current_history_idx = history_no;

    const data = history_pagination_managers[current_history_idx].responseData
    renderRelatedKeyword(data)
    
    // 重新綁定並恢復資料
    history_pagination_managers[current_history_idx].restore();

}

function switch_current_history(history_no){
    // Declare all variables
    let i, history

    // Get all elements with class="tablinks" and remove the class "active"
    history = document.getElementsByClassName("history");
    for (i = 0; i < history.length; i++) {
        history[i].className = history[i].className.replace(" current", "");
    }

    document.getElementById(`history-${history_no}`).className += " current";
}

function add_history(history_no, query){
    document.getElementById("search-history-keywords").insertAdjacentHTML(
        'beforeend',
        `
            <p 
                id="history-${history_no}"
                class="history"
                onclick="
                    switchSearchReuslt(${history_no});
                "
            >
                ${query}
            </p>
        `
    )
}