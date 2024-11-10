<script lang="ts">
	import { onMount } from 'svelte';
	import * as echarts from 'echarts';

	let {
		options,
		width = '100%',
		height = '400px'
	}: { options: any; width?: string; height?: string } = $props();

	let chartDiv: any;

	onMount(() => {
		// 实例化 ECharts
		const chart = echarts.init(chartDiv);

		// 设置 ECharts 的配置项
		chart.setOption(options);

		// 监听窗口大小调整，重新渲染图表
		window.addEventListener('resize', () => chart.resize());

		// 销毁图表实例
		return () => {
			chart.dispose();
		};
	});
</script>

<div bind:this={chartDiv} style="width: {width}; height: {height};"></div>

<style>
	/* 样式可以根据需求自定义 */
</style>
