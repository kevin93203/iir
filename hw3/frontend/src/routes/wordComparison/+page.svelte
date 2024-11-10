<script>
    import ComparisonKeyWord from "./ComparisonKeyWord.svelte";
</script>

<h2>字詞比較</h2>
<div class="compare-row">
    <ComparisonKeyWord/>
    <ComparisonKeyWord/>
</div>

<style>
    .compare-row {
        width: 100%;
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }

    @media (max-width: 1200px) {
		.compare-row {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (max-width: 700px) {
		.compare-row {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>