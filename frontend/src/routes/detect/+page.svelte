<script>
  import { predictImage } from '$lib/api.js';

  let fileInput = $state(null);
  let previewUrl = $state(null);
  let result = $state(null);
  let loading = $state(false);
  let error = $state(null);
  let dragover = $state(false);

  function handleFiles(files) {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!file.type.startsWith('image/')) {
      error = 'Please select an image file.';
      return;
    }
    error = null;
    result = null;
    previewUrl = URL.createObjectURL(file);
    runPrediction(file);
  }

  async function runPrediction(file) {
    loading = true;
    error = null;
    try {
      result = await predictImage(file);
    } catch (err) {
      error = err.message || 'Prediction failed. Is the backend running?';
    } finally {
      loading = false;
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    dragover = false;
    handleFiles(e.dataTransfer.files);
  }

  function handleDragOver(e) {
    e.preventDefault();
    dragover = true;
  }

  function handleDragLeave() {
    dragover = false;
  }

  function openFilePicker() {
    fileInput?.click();
  }

  function handleFileChange(e) {
    handleFiles(e.target.files);
  }

  function reset() {
    previewUrl = null;
    result = null;
    error = null;
    loading = false;
    if (fileInput) fileInput.value = '';
  }
</script>

<svelte:head>
  <title>Detect — MaskDetect</title>
  <meta name="description" content="Upload an image to detect face masks using our CNN model." />
</svelte:head>

<section class="section">
  <div class="container">
    <div class="page-header animate-in">
      <h1><span class="gradient-text">Image Detection</span></h1>
      <p>Upload an image to detect face masks. The model will identify faces and classify each as "Mask" or "No Mask".</p>
    </div>

    <!-- Upload area -->
    {#if !previewUrl}
      <div
        class="drop-zone animate-in delay-1"
        class:dragover
        role="button"
        tabindex="0"
        ondrop={handleDrop}
        ondragover={handleDragOver}
        ondragleave={handleDragLeave}
        onclick={openFilePicker}
        onkeydown={(e) => e.key === 'Enter' && openFilePicker()}
      >
        <h3>Drop image here or click to upload</h3>
        <p>Supports JPG, PNG, WebP</p>
      </div>
    {/if}

    <input
      type="file"
      accept="image/*"
      bind:this={fileInput}
      onchange={handleFileChange}
      hidden
    />

    <!-- Error -->
    {#if error}
      <div class="error-banner animate-in">
        <span>{error}</span>
        <button class="btn btn-ghost" onclick={reset}>Try Again</button>
      </div>
    {/if}

    <!-- Results -->
    {#if previewUrl}
      <div class="results-section animate-in delay-1">
        <!-- Controls -->
        <div class="results-header">
          <div class="results-meta">
            {#if result}
              <span class="badge badge-green">{result.faces_detected} face{result.faces_detected !== 1 ? 's' : ''} detected</span>
              <span class="badge badge-blue">{result.processing_time_ms.toFixed(0)}ms</span>
            {:else if loading}
              <span class="badge badge-blue" style="animation: pulse 1.5s infinite">Processing...</span>
            {/if}
          </div>
          <button class="btn btn-ghost" onclick={reset}>New Image</button>
        </div>

        <!-- Side by side comparison -->
        <div class="comparison-grid">
          <div class="comparison-card glass-card">
            <h3>Original</h3>
            <div class="image-wrapper">
              <img src={previewUrl} alt="Original uploaded image" />
            </div>
          </div>

          <div class="comparison-card glass-card">
            <h3>Detection Result</h3>
            <div class="image-wrapper">
              {#if loading}
                <div class="skeleton-img skeleton"></div>
              {:else if result}
                <img src="data:image/jpeg;base64,{result.annotated_image}" alt="Annotated detection result" />
              {:else}
                <div class="placeholder-img">
                  <p>Waiting for result...</p>
                </div>
              {/if}
            </div>
          </div>
        </div>

        <!-- Detection details table -->
        {#if result && result.detections.length > 0}
          <div class="detections-table glass-card animate-in delay-2">
            <h3>Detection Details</h3>
            <table class="styled-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Label</th>
                  <th>Confidence</th>
                  <th>Bounding Box</th>
                </tr>
              </thead>
              <tbody>
                {#each result.detections as det, i}
                  <tr>
                    <td>{i + 1}</td>
                    <td>
                      <span class="badge" class:badge-green={det.label === 'Mask'} class:badge-red={det.label === 'No Mask'}>{det.label}</span>
                    </td>
                    <td>
                      <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {det.confidence}%; background: {det.color}"></div>
                        <span>{det.confidence.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td class="mono">[{det.bbox.join(', ')}]</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</section>

<style>
  .page-header {
    text-align: center;
    margin-bottom: var(--space-2xl);
  }
  .page-header h1 {
    margin-bottom: var(--space-sm);
  }
  .page-header p {
    max-width: 600px;
    margin: 0 auto;
    font-size: 1.05rem;
  }

  .drop-zone {
    max-width: 600px;
    margin: 0 auto;
  }
  .drop-zone h3 {
    margin-bottom: var(--space-xs);
  }
  .drop-zone p {
    font-size: 0.85rem;
    color: var(--text-muted);
  }

  .error-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-md) var(--space-lg);
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: var(--radius-md);
    margin: var(--space-lg) 0;
    color: var(--accent-red);
  }

  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-lg);
    flex-wrap: wrap;
    gap: var(--space-sm);
  }
  .results-meta {
    display: flex;
    gap: var(--space-sm);
  }

  .comparison-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-lg);
    margin-bottom: var(--space-lg);
  }

  .comparison-card h3 {
    font-size: 0.9rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-md);
  }

  .image-wrapper {
    border-radius: var(--radius-md);
    overflow: hidden;
    background: var(--bg-secondary);
    aspect-ratio: 4/3;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .image-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  .skeleton-img {
    width: 100%;
    height: 100%;
  }

  .placeholder-img {
    color: var(--text-muted);
  }

  .detections-table h3 {
    margin-bottom: var(--space-md);
  }

  .confidence-bar {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    position: relative;
  }
  .confidence-fill {
    height: 6px;
    border-radius: 3px;
    min-width: 40px;
    max-width: 120px;
    transition: width var(--transition-slow);
  }
  .confidence-bar span {
    font-size: 0.85rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }

  .mono {
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
  }

  @media (max-width: 768px) {
    .page-header p {
      font-size: 0.95rem;
    }
    .drop-zone {
      padding: 1.25rem;
    }
    .results-meta {
      width: 100%;
      flex-direction: column;
      align-items: flex-start;
    }
    .results-header {
      align-items: stretch;
    }
    .comparison-grid {
      grid-template-columns: 1fr;
    }
    .styled-table {
      min-width: 560px;
    }
    .comparison-card h3,
    .detections-table h3 {
      font-size: 0.85rem;
    }
    .confidence-bar {
      min-width: 140px;
    }
  }
</style>
