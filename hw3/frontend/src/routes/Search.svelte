<script>
    import { options, searchData, history } from "./shared.svelte.ts";
	import { goto } from '$app/navigation';
	import { PUBLIC_API_URL } from '$env/static/public'
	
    function triggerFileInput() {}

	function handleFileUpload() {}

	async function search() {
		if(!options.query) return;
		const path = window.location.pathname;
        if (path === '/searchResults') {
            goto(`?query=${options.query}`)
        } else {
            goto(`/searchResults?query=${options.query}`)
        }

		console.log("search!")

		const res = await fetch(
			`${PUBLIC_API_URL}/api/search?query=${options.query}&usePorterStem=${options.useStem}&operator=${options.operator}&page=1&pageSize=12` +
			`${options.startDate? "&startDate="+ options.startDate : ""}` + `${options.endDate? "&endDate="+ options.endDate : ""}`
		);
		const data = await res.json()
		
		searchData.data = data;

		history.push({query: options.query, response_data:data})
	}
	// $inspect(searchData)
	$inspect(history)

</script>

<div class="search-bar-wrapper">
	<img src="/file.png" style="width: 300px;" alt="iir logo" />
	<div class="search-container" id="search-bar">
		<input bind:value={options.query} type="search" id="search" name="q" placeholder="Search..." />
		<!-- Icon for uploading an image -->
		<button class="search-icon" onclick={triggerFileInput}>
			<img src="/paper-clip.svg" alt="Upload icon" />
		</button>

		<!-- 顯示的檔案上傳欄位，允許多個檔案 -->
		<div class="file-upload">
			<input type="file" id="file-input" accept=".json,.xml" multiple onchange={handleFileUpload} />
		</div>
	</div>
	<div class="search-options">
		<div class="option">
			詞幹提取
			<label class="switch">
				<input id="useStem" type="checkbox" bind:checked={options.useStem} />
				<span class="slider round"></span>
			</label>
		</div>
		<div class="option">
			<label for="birthday">時間範圍</label>
			<input type="date" id="startDate" bind:value={options.startDate} />
			<input type="date" id="endDate" bind:value={options.endDate} />
		</div>
		<div class="option">
			搜尋邏輯
			<select id="operator" class="custom-select" bind:value={options.operator}>
				<option value="or" selected>OR</option>
				<option value="and">AND</option>
			</select>
		</div>
	</div>
	<button class="search-btn" onclick={search}>IIR Search</button>
</div>

<style>
	.search-bar-wrapper {
		position: relative;
		width: 100%;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
	}

	.search-container {
		position: relative;
		margin: 0 auto 20px auto;
		display: flex;
		align-items: center;
		max-width: 500px;
		width: 100%;
	}

	input[type='search'] {
		width: 100%;
		padding: 12px 40px 12px 20px;
		/* 左側留空以容納 icon */
		border: 1px solid #dfe1e5;
		border-radius: 24px;
		font-size: 16px;
		box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
		outline: none;
		transition: box-shadow 0.2s ease-in-out;
		box-sizing: border-box;
		height: 44px;
	}

	input[type='search']:focus {
		box-shadow: 0 1px 8px #4285f4;
		outline: none;
	}

	input[type='date'] {
		width: 137px;
		height: 27px;
		color: #686868;
		font-size: 16px;
		border: 2px solid #cccccc;
		border-radius: 5px;
		box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
		transition: border-color 0.3s ease;
		padding-left: 10px;
		box-sizing: border-box;
		outline: none;
	}

	.search-btn {
		background-color: #4285f4;
		color: white;
		border: none;
		border-radius: 24px;
		padding: 10px 20px;
		font-size: 16px;
		cursor: pointer;
		margin-left: 10px;
		box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
		transition:
			background-color 0.2s ease-in-out,
			box-shadow 0.2s ease-in-out;
	}

	.search-btn:hover {
		background-color: #357ae8;
		box-shadow: 0 1px 8px rgba(32, 33, 36, 0.3);
	}

	.search-icon {
		position: absolute;
		right: 10px;
		/* 調整 icon 位置 */
		top: 50%;
		transform: translateY(-50%);
		cursor: pointer;
        background-color: transparent;
        border: none;
	}

	.search-icon img {
		width: 20px;
		height: 20px;
	}

	#file-input {
		display: none;
		/* 隱藏檔案上傳 input */
	}

	#search-bar {
		display: flex;
		justify-content: center;
		align-items: center;
		margin-top: 20px;
	}

	.custom-select {
		outline: none;
		height: 27px;
		color: #686868;
		font-size: 16px;
		border: 2px solid #cccccc;
		border-radius: 5px;
		box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
		transition: border-color 0.3s ease;
		padding-left: 5px;
		box-sizing: border-box;
		outline: none;
	}

	.search-options {
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 20px;
		margin-bottom: 20px;
		flex-wrap: wrap;
	}

	.option {
		color: #686868;
		display: flex;
		flex-wrap: nowrap;
		gap: 10px;
		/* 增加輸入框之間的間距 */
		align-items: center;
		/* 垂直居中對齊 */
		text-wrap: nowrap;
	}

	.switch {
		position: relative;
		display: inline-block;
		width: 35px;
		height: 18px;
	}

	.switch input {
		opacity: 0;
		width: 0;
		height: 0;
	}

	.slider {
		position: absolute;
		cursor: pointer;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: #ccc;
		-webkit-transition: 0.4s;
		transition: 0.4s;
	}

	.slider:before {
		position: absolute;
		content: '';
		height: 14px;
		width: 14px;
		left: 3px;
		bottom: 2px;
		background-color: white;
		-webkit-transition: 0.4s;
		transition: 0.4s;
	}

	input:checked + .slider {
		background-color: #4285f4;
	}

	input:focus + .slider {
		box-shadow: 0 0 1px #2196f3;
	}

	input:checked + .slider:before {
		-webkit-transform: translateX(14px);
		-ms-transform: translateX(14px);
		transform: translateX(14px);
	}

	/* Rounded sliders */
	.slider.round {
		border-radius: 34px;
	}

	.slider.round:before {
		border-radius: 50%;
	}

	.custom-select {
		outline: none;
		height: 27px;
		color: #686868;
		font-size: 16px;
		border: 2px solid #cccccc;
		border-radius: 5px;
		box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
		transition: border-color 0.3s ease;
		padding-left: 5px;
		box-sizing: border-box;
		outline: none;
	}
</style>
