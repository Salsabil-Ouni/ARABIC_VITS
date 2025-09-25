<script lang="ts">
	import { onMount } from 'svelte';

	export let audioBlob: Blob;

	let audioUrl: string;
	let audioElement: HTMLAudioElement;
	let isPlaying = false;
	let currentTime = 0;
	let duration = 0;
	let volume = 1;

	onMount(() => {
		audioUrl = URL.createObjectURL(audioBlob);
		return () => {
			if (audioUrl) URL.revokeObjectURL(audioUrl);
		};
	});

	function handleTimeUpdate() {
		currentTime = audioElement?.currentTime || 0;
	}
	function handleLoadedMetadata() {
		duration = audioElement?.duration || 0;
	}
	function handlePlay() { isPlaying = true; }
	function handlePause() { isPlaying = false; }
	function handleEnded() {
		isPlaying = false;
		currentTime = 0;
	}
	function togglePlay() {
		if (!audioElement) return;
		isPlaying ? audioElement.pause() : audioElement.play();
	}
	function handleSeek(e: Event) {
		const t = e.target as HTMLInputElement;
		const newTime = parseFloat(t.value);
		if (audioElement) audioElement.currentTime = newTime;
		currentTime = newTime;
	}
	function handleVolumeChange(e: Event) {
		const t = e.target as HTMLInputElement;
		volume = parseFloat(t.value);
		if (audioElement) audioElement.volume = volume;
	}
	function formatTime(time: number) {
		const m = Math.floor(time / 60);
		const s = Math.floor(time % 60).toString().padStart(2, '0');
		return `${m}:${s}`;
	}
</script>

<div class="audio-player">
	<audio
		bind:this={audioElement}
		src={audioUrl}
		on:timeupdate={handleTimeUpdate}
		on:loadedmetadata={handleLoadedMetadata}
		on:play={handlePlay}
		on:pause={handlePause}
		on:ended={handleEnded}
		preload="metadata"
	></audio>

	<!-- Controls -->
	<div class="controls">
		<button class="play-btn" on:click={togglePlay} aria-label="Play/Pause">
			{#if isPlaying}
				<i class="fas fa-pause"></i>
			{:else}
				<i class="fas fa-play"></i>
			{/if}
		</button>

		<div class="progress">
			<span class="time">{formatTime(currentTime)}</span>
			<input
				type="range"
				min="0"
				max={duration || 0}
				value={currentTime}
				on:input={handleSeek}
			/>
			<span class="time">{formatTime(duration)}</span>
		</div>

		<div class="volume">
			<i class="fas fa-volume-up"></i>
			<input
				type="range"
				min="0"
				max="1"
				step="0.05"
				value={volume}
				on:input={handleVolumeChange}
			/>
		</div>
	</div>
</div>

<style>
.audio-player {
	background: #f9fafb;
	border: 1px solid #e5e7eb;
	border-radius: 1rem;
	padding: 1rem 1.5rem;
	max-width: 600px;
	margin: auto;
	box-shadow: 0 2px 6px rgba(0,0,0,0.08);
	font-family: Inter, system-ui, sans-serif;
}

.controls {
	display: flex;
	align-items: center;
	gap: 1rem;
}

.play-btn {
	background: #3b82f6;
	color: #fff;
	border: none;
	border-radius: 50%;
	width: 3.5rem;
	height: 3.5rem;
	font-size: 1.4rem;
	display: flex;
	align-items: center;
	justify-content: center;
	cursor: pointer;
	transition: background 0.2s;
}
.play-btn:hover { background: #2563eb; }

.progress {
	display: flex;
	align-items: center;
	flex: 1;
	gap: 0.5rem;
}

.progress input[type="range"] {
	flex: 1;
	appearance: none;
	height: 6px;
	background: #d1d5db;
	border-radius: 3px;
	cursor: pointer;
}
.progress input[type="range"]::-webkit-slider-thumb {
	appearance: none;
	width: 14px;
	height: 14px;
	border-radius: 50%;
	background: #3b82f6;
	cursor: pointer;
}
.progress input[type="range"]::-moz-range-thumb {
	width: 14px;
	height: 14px;
	border-radius: 50%;
	background: #3b82f6;
	border: none;
	cursor: pointer;
}

.time {
	font-size: 0.85rem;
	color: #4b5563;
	width: 2.5rem;
	text-align: center;
}

.volume {
	display: flex;
	align-items: center;
	gap: 0.5rem;
}
.volume i {
	color: #4b5563;
}
.volume input[type="range"] {
	width: 80px;
	appearance: none;
	height: 6px;
	background: #d1d5db;
	border-radius: 3px;
	cursor: pointer;
}
.volume input[type="range"]::-webkit-slider-thumb {
	appearance: none;
	width: 14px;
	height: 14px;
	border-radius: 50%;
	background: #3b82f6;
	cursor: pointer;
}
.volume input[type="range"]::-moz-range-thumb {
	width: 14px;
	height: 14px;
	border-radius: 50%;
	background: #3b82f6;
	border: none;
	cursor: pointer;
}
</style>
