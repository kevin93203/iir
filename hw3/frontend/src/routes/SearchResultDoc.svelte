<script lang="ts">
	import { modalState, zipfData } from './shared.svelte';
	import { options, history, searchData } from './shared.svelte';
	import { PUBLIC_API_URL } from '$env/static/public'

	let { item, current = $bindable() }: { item: any, current:number } = $props();
	let loadComplete = $state(false);
	let element: HTMLElement | undefined = $state();
	let related_doc_data: any[] | undefined = $state()

	async function handleLoadRelatedDoc() {
		if (loadComplete) return;
		if ( element && (element.scrollTop + element?.clientHeight >= element?.scrollHeight - 50)) {
			loadComplete = true;
			const url = `${PUBLIC_API_URL}/api/related_doc?pmid=${item.pmid}&top_n=4`
			const response = await fetch(url);
			const data = await response.json();
			related_doc_data = data;

		}
	}

	async function open_document_zipf() {
		modalState.isOpen = true;
		const res = await fetch(`${PUBLIC_API_URL}/api/document/zipf?pmid=${item.pmid}`);
		const data = await res.json();
		zipfData.data = data;
	}


	async function search(pmid: string) {
		const res = await fetch(
			`${PUBLIC_API_URL}/api/search?query=${pmid}&usePorterStem=${options.useStem}&operator=${options.operator}&page=1&pageSize=12`			
		);
		const data = await res.json();
		return data;
	}
</script>

<div class="document-wrapper search-result-wrapper">
	<div class="document-header">
		<div class="pmid">
			PMID: {item.pmid}
		</div>
		<div class="match-count">
			匹配數: {item.match_count}
		</div>
	</div>
	<div class="document-content-container">
		<div
			class="document-content"
			bind:this={element}
			role="button"
			tabindex="0"
			onscroll={handleLoadRelatedDoc}
			onmouseenter={handleLoadRelatedDoc}
		>
			<div class="date-zipf-container">
				<p class="articleDate">{item.articleDate}</p>
				<button class="document-zipf" onclick={open_document_zipf}>
					<img src="/chart.svg" alt="chart icon" />
				</button>
			</div>
			<h2 class="document-title">{@html item.title}</h2>
			<p>{@html item.abstract}</p>
			{#if loadComplete}
				<div class="document-related-doc">
					<div class="document-related-doc-header">
						<img src="/tags.svg" alt="tags icon" />
						相關文獻
					</div>
					{#if related_doc_data}
						{#each related_doc_data as r_data}
							<div
								class="related-title" 
								onclick={() => {
									search(r_data.pmid).then((data) => {
										searchData.data = data;
										history.push({query:r_data.pmid, response_data:data});
										current = history.length - 1;
								});}}
							>
								{r_data.title}
							</div>
						{/each}
					{/if}
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.document-content-container {
		display: flex;
		position: relative;
		background-color: #fff;
		padding: 20px;
		height: 380px;
		box-sizing: border-box;
	}

	.document-content {
		margin-top: 10px;
		max-height: 400px;
		overflow-y: scroll;
	}

	.document-wrapper {
		background-color: #4285f4;
		border-radius: 8px;
		display: flex;
		flex-direction: column;
		justify-content: stretch;
		box-shadow: 0 0 6px rgba(32, 33, 36, 0.28);
		overflow: hidden;
	}

	.document-wrapper:hover {
		box-shadow: 0 0 8px #4285f4;
	}

	.document-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		color: white;
		padding: 6px 10px;
		height: 36px;
		/* 固定第一個元素高度 */
	}

	.date-zipf-container {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 10px;
	}

	.document-zipf {
		width: 30px;
		height: 30px;
		cursor: pointer;
		border-radius: 4px;
		padding: 3px;
		transition: background-color 0.25s ease; /* 設定過渡效果 */
	}

	.document-zipf:hover {
		background-color: #ccc;
	}

	.document-zipf img {
		width: 100%;
		/* 設置圖片寬度等於 div */
		height: 100%;
		/* 設置圖片高度等於 div */
		object-fit: cover;
		/* 調整圖片的縮放方式 */
	}

	.search-result-wrapper {
		background-color: #1dac92;
	}

	.search-result-wrapper:hover {
		box-shadow: 0 0px 8px #1dac92;
	}

	button {
		border: none;
		background-color: transparent;
	}

	:global(mark) {
		background-color: #a3e8db;
		padding: 0 2px;
		border-radius: 4px;
	}

	.document-related-doc-header img {
		width: 30px;
		height: 30px;
	}

	.document-related-doc-header {
		font-size: 18px;
		padding: 5px 5px;
		display: inline-flex;
		justify-content: center;
		align-items: center;
		gap: 5px;
		border-radius: 4px;
		color: #1dac92;
		font-weight: bold;
	}

	.related-title {
		text-align: left;
		padding: 16px;
		font-weight: 500;
		border-bottom: 1px solid #ccc;
		cursor: pointer;
		transition: color 0.25s ease; /* 設定過渡效果 */
	}

	.related-title:hover {
		color: #1dac92;
	}
</style>
