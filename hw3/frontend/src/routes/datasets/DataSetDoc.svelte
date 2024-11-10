<script lang="ts">
    import { modalState, zipfData } from "../shared.svelte.ts";
	import { PUBLIC_API_URL } from '$env/static/public';
	let { item }:{item:any} = $props();

	function openDetelConfirmModal() {}

    async function open_document_zipf() {
        modalState.isOpen = true;
        const res = await fetch(`${PUBLIC_API_URL}/api/document/zipf?pmid=${item.pmid}`);
	    const data = await res.json();
        zipfData.data = data;
    }
</script>

<div class="document-wrapper">
	<div class="document-header">
		<div class="pmid">
			PMID: {item.pmid}
		</div>
		<button class="delete" onclick={openDetelConfirmModal}>
			<img src="/delete.svg" alt="delete icon" />
		</button>
	</div>
	<div class="document-content-container">
		<div class="document-content">
			<div class="date-zipf-container">
				<p class="articleDate">{item.articleDate ? item.articleDate : ''}</p>
				<button class="document-zipf" onclick={open_document_zipf}>
					<img src="/chart.svg" alt="chart icon" />
				</button>
			</div>
			<div class="document-stats">
				<div>
					characters (including spaces): <strong>{item.statistics.characters_including_spaces}</strong>
				</div>
				<div>
					characters (excluding spaces): <strong>{item.statistics.characters_excluding_spaces}</strong>
				</div>
				<div>words: <strong>{item.statistics.words}</strong></div>
				<div>sentences: <strong>{item.statistics.sentences}</strong></div>
				<div>non-ASCII characters: <strong>{item.statistics.non_ascii_characters}</strong></div>
				<div>non-ASCII words: <strong>{item.statistics.non_ascii_words}</strong></div>
			</div>
			<h3 class="document-title">{item.title}</h3>
			<p>{item.abstract}</p>
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

	.document-wrapper:hover .delete {
		visibility: visible;
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

	.document-stats {
		position: relative;
		background-color: #f9f9f9;
		padding: 10px;
		border-radius: 8px;
		box-shadow: 0 1px 6px rgba(32, 33, 36, 0.1);
		font-size: 14px;
		color: #333;
		margin-bottom: 15px;
		line-height: 1.5;
	}

	.document-stats div {
		margin-bottom: 5px;
		font-weight: 700;
	}

	.document-stats div:last-child {
		margin-bottom: 0;
	}

	.document-stats strong {
		font-weight: bold;
		color: #4285f4;
	}

	.delete {
		padding: 5px;
		cursor: pointer;
		display: flex;
		justify-content: center;
		align-items: center;
		border-radius: 4px;
		visibility: hidden;
	}

	.delete img {
		width: 20px;
		height: 20px;
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

    button {
        border: none;
    }
</style>
