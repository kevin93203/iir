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
                            <div>characters (including spaces): <strong>${characters_including_spaces}</strong></div>
                            <div>characters (excluding spaces): <strong>${characters_excluding_spaces}</strong></div>
                            <div>words: <strong>${words}</strong></div>
                            <div>sentences: <strong>${sentences}</strong></div>
                            <div>non-ASCII characters: <strong>${non_ascii_characters}</strong></div>
                            <div>non-ASCII words: <strong>${non_ascii_words}</strong></div>
                        </div>
                        <h2 class='document-title'>${title}</h2>
                        <p>${abstract}</p>
                    </div>
                </div>
            </div>
            `
        );
    });
    toggleAllElements()
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