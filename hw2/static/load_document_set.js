// 當頁面載入完成時
window.addEventListener('load', function() {
    // 使用 fetch 查詢 API
    fetch('/api/document_set/')  // 替換成你自己的 API URL
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();  // 將回傳的資料轉為 JSON 格式
      })
      .then(data => {
        console.log(data);  // 處理 API 回傳的資料
        render_document_set(data['docs'])
        // // 這裡可以將資料動態顯示在頁面上
        // document.getElementById('api-data').textContent = JSON.stringify(data);
      })
      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });
  });