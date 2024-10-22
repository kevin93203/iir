
function triggerFileInput() {
    document.getElementById('file-input').click();  // 觸發檔案上傳
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
        const response = await fetch('/api/upload/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const jsonData = await response.json(); // 取得 JSON 資料
            console.log(jsonData)
            dataSetPaginationManager.elements.pageInput.value = 1;
            // 手動觸發 change 事件
            let event = new Event('change');
            dataSetPaginationManager.elements.pageInput.dispatchEvent(event);
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


// 監聽 keydown 事件
document.getElementById("search").addEventListener('keydown', function(event) {
    // 檢查是否按下 Enter 鍵
    if (event.key === 'Enter') {
        this.blur();
        search();
    }
});

// 監聽 keydown 事件
document.getElementById("keyword-1-input").addEventListener('keydown', function(event) {
    // 檢查是否按下 Enter 鍵
    if (event.key === 'Enter') {
        this.blur();
    }
});

// 監聽 keydown 事件
document.getElementById("keyword-2-input").addEventListener('keydown', function(event) {
    // 檢查是否按下 Enter 鍵
    if (event.key === 'Enter') {
        this.blur();
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