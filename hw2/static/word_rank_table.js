class WordRankTableManager {
    constructor(data, table_no){
        this.data = this.constructData(data);
        this.table_no = table_no;
        const container = document.getElementById(`keyword-${table_no}-WordsRank`);
        container.style.display = 'block'
        this.tbody = container.querySelector('tbody');
        this.select = container.querySelector('select'); 

        this.handleSelectChange = this.handleSelectChange.bind(this);
        
        this.select.addEventListener('change', this.handleSelectChange);

        this.drawWordRankTable(this.select.value);
    }

    handleSelectChange(event) {
        this.drawWordRankTable(event.target.value);
    }

    removeSelectChangeListener() {
        this.select.removeEventListener('change', this.handleSelectChange);
    }

    generateTableRow(rank, word, freq, percentage){
        let _class = ''
        if((rank >= 1) && (rank <= 3)){
            _class = ` class="rank-${rank}"`;
            let rankIcon;
            if(rank === 1){
                rankIcon = '🥇'
            } else if(rank === 2){
                rankIcon = '🥈'
            } else {
                rankIcon = '🥉'
            }
            rank = `<span class="rank-icon">${rankIcon}</span>`
        }
    
        return `
        <tr${_class}>
            <td>${rank}</td>
            <td>${word}</td>
            <td>${freq}</td>
            <td class="percentage">${percentage}%</td>
        </tr>
        `
    }

    getTableRows(top){
        let length = top > this.data.length ? this.data.length : top;
        const rows = this.data.slice(0, length).map((item, index) =>{
            return this.generateTableRow(index+1, item.word, item.freq, item.percentage)
        });
        return rows.join('\n');
    }

    constructData(data){
        const {words, frequencies} = data
        const total = frequencies.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
        const percentages = frequencies.map(freq => (freq / total * 100).toFixed(2))
        const length = words.length > 30 ? 30 : words.length;
        data = []
        for(let i=0; i<length; i++){
            data.push({
                "word": words[i],
                "freq": frequencies[i],
                "percentage": percentages[i]
            })
        }
        return data;
    }

    drawWordRankTable(top=5){        
        const tableRows = this.getTableRows(top)
        this.tbody.innerHTML = `
            ${tableRows}
        `
    }
}