<script lang="ts">
	import Echart from './Echart.svelte';
	import { modalState, zipfData } from './shared.svelte.ts';

	function onclick() {
		modalState.isOpen = !modalState.isOpen;
	}

	function getZipfOptions(title:string, item:any, color:string) {
        const {words, frequencies} = item;

		const options = {
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
					type: 'line', // 使用折線圖顯示
					data: frequencies,
					smooth: true, // 讓線條平滑
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

        return options
	}

	const options = $derived.by(() => {
		if (!zipfData.data) return null;
		return {
            "nonStemZipf": getZipfOptions("Zipf 分布圖", zipfData.data.nonStemZipf, '#5470C6'),
            "pStemZipf": getZipfOptions("Zipf 分布圖 (波特)", zipfData.data.pStemZipf, '#FF0000')
        };
	});

</script>

<!-- 資料集齊夫分布圖modal -->
<div class="modal" style="display: {modalState.isOpen ? 'flex' : 'none'};">
	<div class="modal-content">
		<button class="close" {onclick}>&times;</button>
		{#if modalState.isOpen && options}
			<Echart options={options.nonStemZipf} />
			<Echart options={options.pStemZipf} />
		{/if}
	</div>
</div>

<style>
	/* Modal 的背景（半透明黑色遮罩） */
	.modal {
		display: none;
		/* 預設隱藏 */
		position: fixed;
		/* 固定定位 */
		z-index: 1;
		/* 優先顯示 */
		left: 0;
		top: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		justify-content: center;
		align-items: center;
		/* 黑色遮罩 */
	}

	/* Modal 內容的樣式 */
	.modal-content {
		position: relative;
		display: flex;
		justify-content: center;
		align-items: center;
		flex-direction: column;
		background-color: white;
		margin: 15% auto;
		/* 置中 */
		padding: 20px;
		border: 1px solid #888;
		width: 80%;
		max-width: 800px;
		max-height: 80%;
		/* 限制最大寬度 */
		text-align: center;
		border-radius: 8px;
		overflow: auto;
	}

	/* 關閉按鈕樣式 */
	.close {
		z-index: 99;
		position: absolute;
		top: 5px;
		right: 15px;
		color: #aaa;
		float: right;
		font-size: 28px;
		font-weight: bold;
		padding: 0px;
		background-color: transparent;
		border: none;
	}

	.close:hover,
	.close:focus {
		color: black;
		text-decoration: none;
		cursor: pointer;
	}
</style>
