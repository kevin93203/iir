<script lang="ts">
	import { onMount } from 'svelte';
	import Echart from '../Echart.svelte';
	import MyWordCloud from './MyWordCloud.svelte';
	import { PUBLIC_API_URL } from '$env/static/public';

	let keyword = $state();
	let isSearch = $state(false);
	let selected = $state();
	let wordsData: any = $state([]);
	let element: HTMLElement | undefined = $state();
	let width = $state();

	onMount(() => {
		const observer = new ResizeObserver((entries) => {
			for (let entry of entries) {
				width = entry.contentRect.width; // 更新寬度
			}
		});

		if (element) {
			observer.observe(element); // 開始觀察
		}

		return () => {
			observer.disconnect(); // 清理觀察者
		};
	});

	function getZipfOptions(title: string, item: any, color: string, log: boolean) {
		let { words, frequencies }: { words: string[]; frequencies: number[] } = item;
		if (log) {
			frequencies = frequencies.map((freq) => Math.log10(freq));
		}

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
						color: color // 線條顏色，紅色
					},
					// 設置每個點的顏色
					itemStyle: {
						color: color // 點的顏色，藍色
					}
				}
			]
		};

		return options;
	}

	async function getZipfData() {
		console.log('getZipfData');
		const res = await fetch(
			`${PUBLIC_API_URL}/api/search/zipf?query=${keyword}&usePorterStem=true&operator=or`
		);
		const data = await res.json();
		return data;
	}

	let options: any = $state({ nonlog: null, log: null });

	function setWordsData(data: any) {
		const { words, frequencies }: { words: string[]; frequencies: number[] } = data;
		const total = frequencies.reduce((accumulator, currentValue) => accumulator + currentValue, 0);
		const percentages = frequencies.map((freq) => ((freq / total) * 100).toFixed(2));
		const length = words.length > 30 ? 30 : words.length;

		const newWordsData = [];

		for (let i = 0; i < length; i++) {
			newWordsData.push({
				word: words[i],
				freq: frequencies[i],
				percentage: percentages[i]
			});
		}

		wordsData = newWordsData;
	}

	let words: any[] = $derived(wordsData.map(({word, freq}) => ({text:word, count:freq})))

	$inspect(words)

	function drawKeywordZipf() {
		if (!keyword) return;
		isSearch = true;

		getZipfData().then((data) => {
			setWordsData(data);
			options = {
				nonlog: getZipfOptions(`${keyword} Zipf 分布圖`, data, '#5470C6', false),
				log: getZipfOptions(`${keyword} Zipf Log 分布圖`, data, '#FF0000', true)
			};
		});
	}

	function getRankIcon(rank: number) {
		if (rank === 1) {
			return '🥇';
		} else if (rank === 2) {
			return '🥈';
		} else {
			return '🥉';
		}
	}
</script>

<div class="comparison-keyword" bind:this={element}>
	<input
		bind:value={keyword}
		class="keyword-input"
		type="text"
		placeholder="關鍵字1"
		onblur={() => drawKeywordZipf()}
	/>
	{#if isSearch}
		{#if wordsData.length > 0}
				{#key width}
				{#key words}
					<MyWordCloud words={words} {width} />
				{/key}
				{/key}
			{#key wordsData}
				{#if options.nonlog}
					<Echart options={options.nonlog} />
				{/if}
				{#if options.log}
					<Echart options={options.log} />
				{/if}
			{/key}
		{/if}
		<div class="words-rank-container">
			<div class="controls">
				<span class="label">顯示排名：</span>
				<div class="select-container">
					<select bind:value={selected}>
						<option value="5">前 5 名</option>
						<option value="10">前 10 名</option>
						<option value="20">前 20 名</option>
						<option value="30">前 30 名</option>
					</select>
				</div>
			</div>
			<div class="table-container">
				<table>
					<thead>
						<tr>
							<th>排名</th>
							<th>詞</th>
							<th>頻率</th>
							<th>百分比</th>
						</tr>
					</thead>
					<tbody>
						{#if wordsData.length > 0}
							{#each [...Array(Number(selected)).keys()] as index}
								<tr class={index + 1 >= 1 && index + 1 <= 3 ? `rank_${index + 1}` : ''}>
									<td>
										{#if index + 1 >= 1 && index + 1 <= 3}
											<span class="rank-icon">{getRankIcon(index + 1)}</span>
										{:else}
											{index + 1}
										{/if}
									</td>
									<td>{wordsData[index].word}</td>
									<td>{wordsData[index].freq}</td>
									<td class="percentage">{wordsData[index].percentage}%</td>
								</tr>
							{/each}
						{/if}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div>

{#snippet tableRow(rank: number, word: string, freq: number, percentage: number)}
	<script>
		let _class = '';
		let _rank;
		if (rank >= 1 && rank <= 3) {
			_class = ` class="rank-${rank}"`;
			let rankIcon;
			if (rank === 1) {
				rankIcon = '🥇';
			} else if (rank === 2) {
				rankIcon = '🥈';
			} else {
				rankIcon = '🥉';
			}
			_rank = `<span class="rank-icon">${rankIcon}</span>`;
		} else {
			_rank = rank;
		}
	</script>
{/snippet}

<style>
	.comparison-keyword {
		display: flex;
		flex-direction: column;
		justify-content: flex-start;
		/* 子元素會向上集中排列 */
		align-items: stretch;
		padding: 20px;
		gap: 50px;
	}

	.comparison-keyword {
		position: relative;
		transition: box-shadow 0.2s ease-in-out;
		border-radius: 8px;
	}

	.keyword-input {
		background-color: white;
		z-index: 10;
		position: sticky;
		top: 10px;
		font-size: 20px;
		font-weight: 500;

		width: 100%;
		padding: 12px 40px 12px 20px;
		/* 左側留空以容納 icon */
		border: 1px solid #dfe1e5;
		border-radius: 8px;
		font-size: 16px;
		box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
		outline: none;
		transition: box-shadow 0.2s ease-in-out;
		box-sizing: border-box;
		height: 44px;
	}

	.WordCloud {
		width: 100%;
		height: 400px;
	}

	.controls {
		margin-bottom: 1rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.select-container {
		position: relative;
	}

	.select-container select {
		padding: 0.5rem 2rem 0.5rem 1rem;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		background-color: white;
		font-size: 0.875rem;
		cursor: pointer;
		appearance: none;
		color: #4f46e5;
		font-weight: 500;
	}

	select:hover {
		border-color: #4f46e5;
	}

	select:focus {
		outline: 2px solid #4f46e5;
		outline-offset: 1px;
	}

	.select-container::after {
		content: '▼';
		font-size: 0.8rem;
		color: #4f46e5;
		position: absolute;
		right: 0.8rem;
		top: 50%;
		transform: translateY(-50%);
		pointer-events: none;
	}

	.label {
		font-weight: 500;
		color: #4b5563;
	}

	.table-container {
		width: 100%;
		margin: 0;
		background: white;
		border-radius: 10px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		overflow: hidden;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		background: white;
	}

	th {
		background: linear-gradient(45deg, #4f46e5, #6366f1);
		color: white;
		padding: 1rem;
		text-align: center;
	}

	td {
		padding: 1rem;
		border-bottom: 1px solid #e5e7eb;
		text-align: center;
		/* 所有表格內容置中 */
	}

	tr:hover {
		background: #f8fafc;
	}

	tr:last-child td {
		border-bottom: none;
	}

	.rank_1 {
		background: linear-gradient(45deg, rgba(255, 215, 0, 0.1), transparent);
	}

	.rank_2 {
		background: linear-gradient(45deg, rgba(192, 192, 192, 0.1), transparent);
	}

	.rank_3 {
		background: linear-gradient(45deg, rgba(205, 127, 50, 0.1), transparent);
	}

	.rank_icon {
		font-size: 1.5rem;
	}

	.percentage {
		color: #6366f1;
		font-weight: 500;
	}
</style>
