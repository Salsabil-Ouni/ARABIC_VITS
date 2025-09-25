<script lang="ts">
    import IpaEditor from '../components/IpaEditor.svelte';
    import AudioPlayer from '../components/AudioPlayer.svelte';

    let inputText = '';
    let ipaText = '';
    let audioBlob: Blob | null = null;
    let isLoading = false;
    let statusMessage = '';          // NEW
    let error = '';
    let vitsUrl = '/api/vits';

    let segments: Array<{
        text: string;
        ipa: string;
        duration: number;
        start: number;
        end: number;
    }> = [];

    // Generate IPA from text
    async function generateSpeech() {
        if (!inputText.trim()) {
            error = 'Please enter some text';
            return;
        }
        statusMessage = 'Generating IPA transcription…';   // NEW
        isLoading = true;
        error = '';

        try {
            const response = await fetch(`${vitsUrl}/synthesize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: inputText })
            });
            if (!response.ok) throw new Error('Failed to synthesize IPA');

            const data = await response.json();
            ipaText = data.ipa || '';
            segments = [];
            audioBlob = null; // clear old audio
        } catch (err) {
            error = err instanceof Error ? err.message : 'An error occurred';
            console.error(err);
        } finally {
            isLoading = false;
            statusMessage = '';       // reset
        }
    }

    // Clear audio when IPA changes manually
    function handleIpaChange(event: CustomEvent) {
        ipaText = event.detail;
        audioBlob = null;
    }

    // Generate audio from IPA
    async function generateFromIpa() {
        if (!ipaText.trim()) {
            error = 'Please enter IPA text';
            return;
        }
        statusMessage = 'Synthesizing speech…';            // NEW
        isLoading = true;
        error = '';

        try {
            const vitsResponse = await fetch(`${vitsUrl}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain' },
                body: ipaText
            });
            if (!vitsResponse.ok) throw new Error('Failed to generate speech');
            audioBlob = await vitsResponse.blob();
        } catch (err) {
            error = err instanceof Error ? err.message : 'An error occurred';
            console.error(err);
        } finally {
            isLoading = false;
            statusMessage = '';       // reset
        }
    }
</script>

<svelte:head>
    <title>Arabic Text-to-Speech with VITS</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" />
    <link rel="stylesheet" href="/css/style.css" />
</svelte:head>

<div class="container">
    <header class="header">
        <div class="header-content">
            <h1 class="logo">
                <i class="fas fa-microphone-alt"></i>
                Arabic Text-to-Speech with VITS
            </h1>
            <p class="subtitle">Synthesize Natural Sounding Arabic Speech</p>
        </div>
    </header>

    <main class="main-content">
        <!-- Text Input Card -->
        <div class="card">
            <div class="card-header">
                <h2><i class="fas fa-edit"></i> Text Input</h2>
            </div>
            <div class="card-body">
                <div class="form-group">
                    <label for="text-input">Enter your text:</label>
                    <textarea
                        id="text-input"
                        class="text-input"
                        rows="6"
                        bind:value={inputText}
                        placeholder="Type or paste your text here..."
                    ></textarea>
                </div>

                <div class="button-group">
                    <button
                        class="btn btn-primary"
                        on:click={generateSpeech}
                        disabled={isLoading || !inputText.trim()}
                    >
                        <i class="fas fa-language"></i>
                        {isLoading && statusMessage === 'Generating IPA transcription…'
                            ? 'Generating…'
                            : 'Generate IPA'}
                    </button>
                    <button
                        class="btn btn-secondary"
                        on:click={() => { inputText=''; ipaText=''; audioBlob=null; }}
                    >
                        <i class="fas fa-trash"></i> Clear Text
                    </button>
                </div>
            </div>
        </div>

        <!-- IPA Card -->
        {#if ipaText}
        <div class="card">
            <div class="card-header">
                <h2><i class="fas fa-language"></i> IPA Transcription</h2>
            </div>
            <div class="card-body">
                <!-- Remove the extra plain-text display if you don't want duplication -->
                <!-- <div class="ipa-output">{ipaText}</div> -->

                <IpaEditor bind:ipaText on:change={handleIpaChange} />

                <div class="button-group">
                    <button
                        class="btn btn-primary"
                        on:click={generateFromIpa}
                        disabled={isLoading || !ipaText.trim()}
                    >
                        <i class="fas fa-play"></i>
                        {isLoading && statusMessage === 'Synthesizing speech…'
                            ? 'Generating…'
                            : 'Synthesize Speech from IPA'}
                    </button>
                </div>
            </div>
        </div>
        {/if}

        <!-- Audio Player -->
        {#if audioBlob}
	<div class="card">
		<div class="card-header">
			<h2><i class="fas fa-music"></i> Generated Audio</h2>
		</div>
		<div class="card-body">
			<AudioPlayer {audioBlob} />

			<div class="button-group flex justify-center mt-4" style="margin-top: 1rem;">
				<a
					class="btn btn-secondary"
					href={URL.createObjectURL(audioBlob)}
					download="tts_audio.wav"
				>
					<i class="fas fa-download"></i> Download Audio
				</a>
			</div>
		</div>
	</div>
{/if}



        <!-- Status / Error -->
        <div class="card">
            <div class="card-header">
                <h2><i class="fas fa-info-circle"></i> Status</h2>
            </div>
            <div class="card-body">
                {#if error}
                    <div class="status-message error">{error}</div>
                {:else if isLoading}
                    <div class="status-message">{statusMessage}</div>
                {:else}
                    <div class="status-message">Ready to synthesize speech.</div>
                {/if}
            </div>
        </div>
    </main>
</div>
