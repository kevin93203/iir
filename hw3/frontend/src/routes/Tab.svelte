<script>
    import { onMount } from "svelte";
    import { goto } from '$app/navigation';
	import { options } from "./shared.svelte.ts";

    // 定義一個變數來追蹤當前選中的選項卡
    let activeTab = $state('searchResults');

    // 當組件掛載時，根據當前路由設置 activeTab
    onMount(() => {
        const path = window.location.pathname;
        if (path === '/datasets') {
            activeTab = 'datasets';
        } else if (path === '/wordComparison') {
            activeTab = 'wordComparison';
        } else {
            activeTab = 'searchResults';
        }
    });

    function changeTab(tabId) {
        activeTab = tabId;
        goto(`/${tabId}`);
    }

</script>

<div class="tab">
    <button class="tablinks {activeTab === 'searchResults' ? 'active' : ''}" onclick={() => changeTab('searchResults')}>
        搜尋結果
    </button>
    <button class="tablinks {activeTab === 'datasets' ? 'active' : ''}" onclick={() => changeTab('datasets')}>
        資料集
    </button>
    <button class="tablinks {activeTab === 'wordComparison' ? 'active' : ''}" onclick={() => changeTab('wordComparison')}>
        字詞比較
    </button>
</div>


<style>
	/* Style the tab */
	.tab {
		margin-top: 40px;
		width: 100%;
		overflow: hidden;
		background-color: #f1f1f1;
		border-bottom: 1px solid #ccc;
	}

	/* Style the buttons that are used to open the tab content */
	.tab button {
		font-family: 'Roboto', sans-serif;
		font-size: 16px;
		background-color: inherit;
		float: left;
		border: none;
		outline: none;
		cursor: pointer;
		padding: 14px 16px;
		transition: 0.3s;
		border-bottom: 2px solid rgba(32, 33, 36, 0);
	}

	/* Change background color of buttons on hover */
	.tab button:hover {
		background-color: #ddd;
	}

	/* Create an active/current tablink class */
	.tab button.active {
		color: #4285f4;
		border-bottom: 2px solid #4285f4;
	}

</style>
