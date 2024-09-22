let global_data = null; // 保留全域變數

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
        documents_results.insertAdjacentHTML(
            'beforeend',
            `
                <div>
                    <div>搜尋內容: ${search_result['query']}</div>
                    <div>關鍵字: ${search_result['query_keywords'].join(", ")}</div>
                    <div>關鍵字字數: ${search_result['query_keywords'].length}</div>
                </div>
            `
        )

        if (!is_history) {
            const history_no = global_data["search_history"].length - 1
            document.getElementById("search-history").insertAdjacentHTML(
                'beforeend',
                `
                    <button 
                        id="history-${history_no}"
                        onclick="render_documents(global_data, global_data['search_history'][${history_no}], true)"
                    >
                        ${search_result['query']}
                    </button>
                `
            )
        }

        if (search_result['highlighted_documents'].every(element => element === null)) {
            documents_results.append("搜尋不到任何結果！");
            return
        }
    }
    for (let i = 0; i < document_size; i++) {
        const document_content = search_result ? search_result['highlighted_documents'][i] : data['documents'][i];
        if (document_content === null) continue;
        documents_results.insertAdjacentHTML(
            'beforeend',
            `
            <div>
                <h3>${data['filenames'][i]}</h3>
                ${search_result === null ?
                `
                    <div>
                        <div>characters (including spaces): ${data['statistics'][i]['characters_including_spaces']}</div>
                        <div>characters (excluding spaces): ${data['statistics'][i]['characters_excluding_spaces']}</div>
                        <div>words: ${data['statistics'][i]['words']}</div>
                        <div>sentences: ${data['statistics'][i]['sentences']}</div>
                        <div>non-ASCII characters: ${data['statistics'][i]['non_ascii_characters']}</div>
                        <div>non-ASCII words: ${data['statistics'][i]['non_ascii_words']}</div>
                    </div>
                    `
                : ""
            }
                <p>${document_content}<p>
            </div>
            `
        );
    }
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
            console.log(search_result);
            global_data["search_history"].push(search_result)
            render_documents(global_data, search_result);
            alert('Search documents successfully!');
        } else {
            const errorData = await response.json(); // 取得錯誤的 JSON 資料（如果有的話）
            alert(`Failed to search documents`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while searching.');
    }
}



document.getElementById('upload-form').onsubmit = async function (event) {
    event.preventDefault(); // Prevent the default form submission

    const input = document.getElementById('file');
    if (!input.files.length) {
        alert('Please select at least one file.');
        return;
    }

    const formData = new FormData();
    for (const file of input.files) {
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
            console.log(global_data);
            render_documents(global_data); // 使用 render_documents 顯示未加亮的文檔
            alert('Files uploaded successfully!');
        } else {
            const errorData = await response.json(); // 取得錯誤的 JSON 資料（如果有的話）
            alert(`Failed to upload files: ${errorData.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while uploading files.');
    }
};
