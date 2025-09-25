<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';

	const dispatch = createEventDispatcher();

	export let ipaText = '';

	let layouts: any[] = [];
	let currentLayout: any = null;
	let showTooltip = false;
	let tooltipText = '';
	let tooltipX = 0;
	let tooltipY = 0;
	let isLoading = true;
	let error = '';

	function addSymbol(action: string) {
		ipaText += action;
		dispatch('change', ipaText);
	}

	function clearText() {
		ipaText = '';
		dispatch('change', ipaText);
	}

	function backspace() {
		ipaText = ipaText.slice(0, -1);
		dispatch('change', ipaText);
	}

	function showSymbolTooltip(event: MouseEvent, label: string) {
		showTooltip = true;
		tooltipText = label;
		tooltipX = event.clientX;
		tooltipY = event.clientY;
	}

	function hideTooltip() {
		showTooltip = false;
	}

	function handleTextInput(event: Event) {
		const target = event.target as HTMLTextAreaElement;
		ipaText = target.value;
		dispatch('change', ipaText);
	}

	function handleLayoutChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		const layoutId = parseInt(target.value);
		currentLayout = layouts.find((layout) => layout.id === layoutId);
	}
</script>

<div class="ipa-editor">
	<!-- Text Area -->
	<div class="mb-4">
		<label for="ipaTextarea" class="mb-2 block text-sm font-medium text-gray-700"> IPA Text </label>
		<textarea
			id="ipaTextarea"
			bind:value={ipaText}
			on:input={handleTextInput}
			placeholder="Enter IPA text or use the keyboard below..."
			class="h-24 w-full resize-none rounded-md border border-gray-300 px-3 py-2 font-mono text-lg focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
		></textarea>
	</div>

	<!-- Control Buttons -->
	
	<!-- Tooltip -->
	{#if showTooltip}
		<div
			class="pointer-events-none fixed z-50 rounded bg-black px-2 py-1 text-xs text-white"
			style="left: {tooltipX + 10}px; top: {tooltipY - 30}px;"
		>
			{tooltipText}
		</div>
	{/if}
</div>

<style>
	.ipa-keyboard {
		max-height: 400px;
		overflow-y: auto;
	}

	.ipa-key {
		min-width: 40px;
		min-height: 40px;
	}
</style>
