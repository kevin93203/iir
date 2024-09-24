let global_data = null; // 保留全域變數

function triggerFileInput() {
    document.getElementById('file-input').click();  // 觸發檔案上傳
}

function show_or_hide(ele) {
    if (ele.innerHTML === "隱藏上傳資料") {
        document.getElementById('upload-documents').style.display = 'none';
        ele.innerHTML = "顯示上傳資料"
    } else {
        document.getElementById('upload-documents').style.display = 'block';
        ele.innerHTML = "隱藏上傳資料"
    }
}

function render_documents(data, search_result = null, is_history = false) {
    const target_id = search_result ? "search-result-contents" : "upload-documents-contents"
    const documents_results = document.getElementById(target_id);
    documents_results.innerHTML = '';
    const document_size = data['filenames'].length;
    if (search_result) {
        const search_content = document.getElementById("search-content")
        search_content.innerHTML = '';
        search_content.insertAdjacentHTML(
            'beforeend',
            `
                <div>搜尋內容: ${search_result['query']}</div>
                <div>關鍵字: ${search_result['query_keywords'].join(", ")}</div>
                <div>關鍵字字數: ${search_result['query_keywords'].length}</div>
            `
        )

        if (!is_history) {
            const history_no = global_data["search_history"].length - 1
            document.getElementById("search-history-keywords").insertAdjacentHTML(
                'beforeend',
                `
                    <button 
                        id="history-${history_no}"
                        onclick="
                            render_documents(global_data, global_data['search_history'][${history_no}], true);
                            go_to_search_result();
                        "
                    >
                        ${search_result['query']}
                    </button>
                `
            )
        }

        if (search_result['highlighted_documents'].every(element => element === null)) {
            documents_results.innerHTML = "<p>搜尋不到任何結果！<p>";
            toggleAllElements();
            return
        }
    }
    for (let i = 0; i < document_size; i++) {
        const document_content = search_result ? search_result['highlighted_documents'][i] : data['documents'][i];
        if (document_content === null) continue;
        documents_results.insertAdjacentHTML(
            'beforeend',
            `
            <div class='document-content-container'>
                <div class='document-filename'>${data['filenames'][i]}</div>
                <div class='document-content'>
                    ${search_result === null ?
                    `
                        <div class='document-stats'>
                            <div>characters (including spaces): <strong>${data['statistics'][i]['characters_including_spaces']}</strong></div>
                            <div>characters (excluding spaces): <strong>${data['statistics'][i]['characters_excluding_spaces']}</strong></div>
                            <div>words: <strong>${data['statistics'][i]['words']}</strong></div>
                            <div>sentences: <strong>${data['statistics'][i]['sentences']}</strong></div>
                            <div>non-ASCII characters: <strong>${data['statistics'][i]['non_ascii_characters']}</strong></div>
                            <div>non-ASCII words: <strong>${data['statistics'][i]['non_ascii_words']}</strong></div>
                        </div>
                        `
                    : ""}
                    <p>${document_content}<p>
                </div>
            </div>
            `
        );
    }
    toggleAllElements()
}

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
    if (!global_data) {
        alert("請先上傳檔案");
        return;
    }
    if (!query) {
        alert("搜尋文字不能為空白！");
        return;
    }
    try {
        const response = await fetch(`/search/?query=${query}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(global_data)
        });

        if (response.ok) {
            const search_result = await response.json(); // 取得 JSON 資料
            global_data["search_history"].push(search_result)
            render_documents(global_data, search_result);
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

async function handleFileUpload(event) {
    const files = event.target.files;
    if (!files.length) {
        alert('Please select at least one file.');
        return;
    }
    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }

    try {
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const jsonData = await response.json(); // 取得 JSON 資料
            global_data = jsonData;
            render_documents(global_data); // 使用 render_documents 顯示未加亮的文檔
            clean_history_and_search_result() // 清空搜尋歷史和搜尋結果的html
            toggleAllElements()
            alert('Files uploaded successfully!');
        } else {
            const errorData = await response.json(); // 取得錯誤的 JSON 資料（如果有的話）
            alert(`Failed to upload files: ${errorData.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while uploading files.');
    }
}

function toggleAllElements(){
    toggleElements('upload-documents', 'upload-documents-contents')
    toggleElements('search-history', 'search-history-keywords')
    toggleElements('search-result', 'search-result-contents')
}

function toggleElements(parent_id, child_id) {
    const parentElement = document.getElementById(parent_id);
    const childElement = document.getElementById(child_id);

    if (childElement.children.length === 0) {
        parentElement.style.display = 'none';
    } else {
        parentElement.style.display = 'flex';
    }
}

// 初次頁面載入時執行
document.addEventListener("DOMContentLoaded", toggleAllElements);

// 監聽 keydown 事件
document.getElementById("search").addEventListener('keydown', function(event) {
    // 檢查是否按下 Enter 鍵
    if (event.key === 'Enter') {
        this.blur();
        search();
    }
});

function clean_history_and_search_result(){
    const target_id_list = ["search-history-keywords", "search-content","search-result-contents"]
    target_id_list.forEach(id => {
        document.getElementById(id).innerHTML = ""
    })
}

function observe_popup_search(){
    const target = document.getElementById('search-bar');
    const popup_search = document.getElementById('popup-search');

    // 建立 IntersectionObserver
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) {
                // 當 target 離開視窗畫面時，顯示並觸發動畫
                popup_search.classList.remove('hide');
                popup_search.classList.add('show');
            } else {
                // 當 target 進入視窗畫面時，隱藏並觸發動畫
                popup_search.classList.remove('show');
                popup_search.classList.add('hide');
            }
        });
    });

    // 觀察 target 元素
    observer.observe(target);
}

observe_popup_search()

function goto_search_bar(){
    // 取得你要滾動到的元素
    const element = document.getElementById('search');

    // 使用 scrollIntoView 滾動到該元素
    element.scrollIntoView({
        behavior: 'smooth', // 平滑滾動 (也可以設為 'auto')
        block: 'end',     // 滾動到元素的頂部 ('end' 會滾動到底部)
        inline: 'nearest'   // 水平滾動行為
    });

    element.focus();
}