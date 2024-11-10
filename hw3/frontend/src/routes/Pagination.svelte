<script lang="ts">
	import { goto } from '$app/navigation';

	let {
		currentPage = $bindable(1),
		totalPages = 1,
	}: { currentPage: number; totalPages: number} = $props();

	function updatePage(newPage: number | null) {
		currentPage = newPage || 1;
		goto(`?page=${currentPage}`);
	}
</script>

<div class="pagination">
	<button id="prevButton" aria-label="previous page" onclick={() => updatePage(currentPage - 1)}>
		<i class="arrow arrow-left"></i>
	</button>
	<div class="page-info">
		<input
			type="number"
			id="pageInput"
			class="page-input no-spin"
			value={currentPage}
			onblur={(event) => updatePage(Number(event.currentTarget.value))}
			min="1"
		/>
		<span class="page-total">of <span id="totalPages">{totalPages}</span></span>
	</div>
	<button id="nextButton" aria-label="next page" onclick={() => updatePage(currentPage + 1)}>
		<i class="arrow arrow-right"></i>
	</button>
</div>

<style>
	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 4px;
		margin-top: 20px;
		margin-bottom: 10px;
	}

	.pagination button {
		border: 1px solid #e2e8f0;
		background: white;
		padding: 8px 12px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		min-width: 36px;
		height: 36px;
	}

	.pagination button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.pagination button:not(:disabled):hover {
		background: #f8fafc;
	}

	.page-info {
		display: flex;
		align-items: center;
		padding: 0 12px;
		border: 1px solid #e2e8f0;
		height: 36px;
		gap: 8px;
	}

	.page-input {
		width: 40px;
		height: 24px;
		border: 1px solid #e2e8f0;
		border-radius: 3px;
		text-align: center;
		font-size: 14px;
		padding: 0 4px;
	}

	.page-total {
		color: #64748b;
		font-size: 14px;
	}

	.arrow {
		border: solid #64748b;
		border-width: 0 2px 2px 0;
		display: inline-block;
		padding: 3px;
	}

	.arrow-left {
		transform: rotate(135deg);
	}

	.arrow-right {
		transform: rotate(-45deg);
	}
</style>
