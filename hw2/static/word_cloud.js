// 轉換成JQCloud的資料格式
function processData(data) {
    const {words, frequencies} = data;
    return words.map((text, i) => ({
        text: String(text),
        weight: Number(frequencies[i]),
        html: {
            class: 'word-cloud-item'
        }
    })).filter(item => item.text && item.weight > 0);
}
