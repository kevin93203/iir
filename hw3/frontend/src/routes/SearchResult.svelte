<script lang="ts">
	import { untrack } from 'svelte';
	import Pagination from './Pagination.svelte';
	import SearchResultDoc from './SearchResultDoc.svelte';
	import { options, searchData, history } from './shared.svelte.ts';
	import { PUBLIC_API_URL } from '$env/static/public';

	let currentPage = $state(1);
	let current = $state(0);

	async function search(currentPage: number, query?: string) {
		query = query ? query : options.query;
		const res = await fetch(
			`${PUBLIC_API_URL}/api/search?query=${untrack(() => query)}&usePorterStem=${untrack(() => options.useStem)}&operator=${untrack(() => options.operator)}&page=${currentPage}&pageSize=12`
		);
		const data = await res.json();
		return data;
	}

	$effect(() => {
		console.log(`[Effect]: ${currentPage}`);
		if (untrack(() => options.query)) {
			search(currentPage).then((data) => {
				searchData.data = data;
			});
		}
	});

	$inspect(history);
</script>

<div id="search-history">
	<h2>搜尋紀錄</h2>
	<div id="search-history-keywords">
		{#each history as record, i}
			<button
				class="history"
				class:current={current == i}
				onclick={() => {
					current = i;
					searchData.data = history[i].response_data;
				}}
			>
				{record.query}
			</button>
		{/each}
	</div>
</div>
<div id="related">
	<h2>相關</h2>
	<div id="related-keywords">
		{#each searchData.data?.related_keyword as keyword}
			<button
				class="history"
				onclick={() => {
					search(currentPage, keyword).then((data) => {
						searchData.data = data;
						history.push({ query: keyword, response_data: data });
						current = history.length - 1;
					});
				}}
			>
				{keyword}
			</button>
		{/each}
	</div>
</div>
<div id="search-result">
	<h2>搜尋結果</h2>
	<div id="search-result-msg">{searchData.data ? `${searchData.data.total}個結果` : ''}</div>
	<div class="documents-contents">
		{#if searchData.data}
			{#each searchData.data.items as item}
				<SearchResultDoc {item} bind:current />
			{/each}
		{/if}
	</div>
</div>

{#if searchData.data}
	<Pagination bind:currentPage totalPages={searchData.data.totalPages} />
{/if}

<style>
	.documents-contents {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 30px;
		grid-auto-rows: 420px;
	}

	#search-history {
		/* width: 600px; */
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		gap: 10px;
	}

	#search-result-msg {
		color: #686868;
		margin-bottom: 20px;
	}

	#search-history-keywords {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 10px;
	}

	#search-result,
	#search-history {
		/* width: 600px; */
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		gap: 10px;
	}

	#related {
		/* width: 600px; */
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		gap: 10px;
	}

	#related-keywords {
		display: flex;
		justify-content: center;
		align-items: center;
		flex-wrap: wrap;
		gap: 10px;
	}

	.history {
		font-size: 16px;
		/* font-weight: bold; */
		text-decoration-line: underline;
		color: #686868;
		cursor: pointer;
		margin: 16px 0;
	}

	.history:hover {
		color: #1dac92;
	}

	.current {
		color: #1dac92;
	}

	button {
		background-color: transparent;
		border: none;
	}

	@media (max-width: 1200px) {
		.documents-contents {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (max-width: 700px) {
		.documents-contents {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
