<script>
	import Search from "./Search.svelte";
	import Tab from "./Tab.svelte";
    import Modal from "./Modal.svelte";
    let { children } = $props();

</script>
<Search/>
<Tab/>
<Modal/>

<div class="tabcontent">
    {@render children()}
</div>

<style>
    :global(body){
        font-family: 'Roboto', sans-serif;
        margin: 0;
        padding: 60px 30px;
        background-color: #f2f2f2;
        color: #202124;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
    }
    /* Style the tab content */
    .tabcontent {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
        padding: 20px;
        background-color: #f7f8f9;
        box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
        border-radius: 8px;
        box-sizing: border-box;
        width: 100%;
    }
</style>
