<script>
    import Pagination from "../Pagination.svelte";
    import DataSetDoc from "./DataSetDoc.svelte";

    let { data=null } = $props();

    $effect(()=>{
        console.log("Dataset Mounted");

        return () => {
            console.log("Dataset UnMounted");
        }
    })
</script>

{#if data}
    <!-- 資料集 -->
    <h2>資料集</h2>
    <div id="upload-documents-msg">
        {data.data.total}個結果
    </div>
    <div class="documents-contents">
        {#each data.data.items as item}
            <DataSetDoc {item}/>
        {/each}
    </div>
    <Pagination currentPage={data.data.currentPage} totalPages={data.data.totalPages}/>
{/if}
<style>
    .documents-contents {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 30px;
        grid-auto-rows: 420px;
    }

    #upload-documents-msg {
        color: #686868;
        margin-bottom: 20px;
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