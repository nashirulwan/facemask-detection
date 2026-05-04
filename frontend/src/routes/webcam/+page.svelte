<script>
  import { onMount } from 'svelte';
  import { predictImage } from '$lib/api.js';

  let videoEl = $state(null);
  let canvasEl = $state(null);
  let stream = $state(null);
  let cameraActive = $state(false);
  let capturing = $state(false);
  let result = $state(null);
  let loading = $state(false);
  let error = $state(null);
  let capturedImageUrl = $state(null);
  let frameOrientation = $state('landscape');

  async function startCamera() {
    error = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      if (videoEl) {
        videoEl.srcObject = stream;
        videoEl.onloadedmetadata = () => {
          frameOrientation = videoEl.videoHeight > videoEl.videoWidth ? 'portrait' : 'landscape';
        };
        await videoEl.play();
        frameOrientation = videoEl.videoHeight > videoEl.videoWidth ? 'portrait' : 'landscape';
        cameraActive = true;
      }
    } catch (err) {
      error = 'Could not access camera. Please allow camera permissions.';
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
    cameraActive = false;
    frameOrientation = 'landscape';
  }

  async function captureAndDetect() {
    if (!videoEl || !canvasEl) return;

    capturing = true;
    loading = true;
    error = null;
    result = null;

    const ctx = canvasEl.getContext('2d');
    canvasEl.width = videoEl.videoWidth;
    canvasEl.height = videoEl.videoHeight;
    ctx.drawImage(videoEl, 0, 0);

    capturedImageUrl = canvasEl.toDataURL('image/jpeg', 0.9);

    canvasEl.toBlob(async (blob) => {
      const file = new File([blob], 'webcam_capture.jpg', { type: 'image/jpeg' });
      try {
        result = await predictImage(file);
      } catch (err) {
        error = err.message || 'Prediction failed. Is the backend running?';
      } finally {
        loading = false;
      }
    }, 'image/jpeg', 0.9);
  }

  function resetCapture() {
    result = null;
    capturedImageUrl = null;
    capturing = false;
    error = null;
  }

  onMount(() => {
    return () => stopCamera();
  });
</script>

<svelte:head>
  <title>Webcam — MaskDetect</title>
  <meta name="description" content="Real-time face mask detection using your webcam." />
</svelte:head>

<section class="section">
  <div class="container">
    <div class="page-header animate-in">
      <h1><span class="gradient-text">Webcam Detection</span></h1>
      <p>Use your webcam to capture a photo and detect face masks in real-time.</p>
    </div>

    <!-- Camera controls -->
    <div class="camera-controls animate-in delay-1">
      {#if !cameraActive}
        <button class="btn btn-primary btn-lg" onclick={startCamera}>Start Camera</button>
      {:else}
        <button class="btn btn-secondary" onclick={stopCamera}>Stop Camera</button>
        {#if !capturing}
          <button class="btn btn-primary btn-lg" onclick={captureAndDetect}>Capture & Detect</button>
        {:else}
          <button class="btn btn-ghost" onclick={resetCapture}>New Capture</button>
        {/if}
      {/if}
    </div>

    {#if error}
      <div class="error-banner animate-in">
        <span>{error}</span>
      </div>
    {/if}

    <div class="webcam-layout animate-in delay-2">
      <!-- Video feed -->
      <div class="video-section glass-card">
        <h3>Camera Feed</h3>
        <div class="video-wrapper" class:inactive={!cameraActive} class:portrait={frameOrientation === 'portrait'}>
          {#if !cameraActive}
            <div class="camera-placeholder">
              <p>Camera is off. Click "Start Camera" to begin.</p>
            </div>
          {/if}
          <!-- svelte-ignore element_invalid_self_closing_tag -->
          <video bind:this={videoEl} class:hidden={!cameraActive} playsinline muted />
        </div>
      </div>

      <!-- Result -->
      <div class="result-section glass-card">
        <h3>Detection Result</h3>
        <div class="result-wrapper" class:portrait={frameOrientation === 'portrait'}>
          {#if loading}
            <div class="skeleton-img skeleton"></div>
          {:else if result}
            <img src="data:image/jpeg;base64,{result.annotated_image}" alt="Detection result" />
            <div class="result-badges">
              <span class="badge badge-green">{result.faces_detected} face{result.faces_detected !== 1 ? 's' : ''}</span>
              <span class="badge badge-blue">{result.processing_time_ms.toFixed(0)}ms</span>
            </div>
          {:else if capturedImageUrl}
            <img src={capturedImageUrl} alt="Captured frame" />
          {:else}
            <div class="camera-placeholder">
              <p>Capture a photo to see detection results.</p>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- Detection details -->
    {#if result && result.detections.length > 0}
      <div class="detections-list glass-card animate-in">
        <h3>Detected Faces</h3>
        <div class="detection-cards">
          {#each result.detections as det, i}
            <div class="detection-item">
              <span class="detection-index">{i + 1}</span>
              <span class="badge" class:badge-green={det.label === 'Mask'} class:badge-red={det.label === 'No Mask'}>
                {det.label}
              </span>
              <span class="detection-conf">{det.confidence.toFixed(1)}%</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <canvas bind:this={canvasEl} hidden></canvas>
  </div>
</section>

<style>
  .page-header {
    text-align: center;
    margin-bottom: var(--space-xl);
  }
  .page-header h1 { margin-bottom: var(--space-sm); }
  .page-header p {
    max-width: 500px;
    margin: 0 auto;
  }

  .camera-controls {
    display: flex;
    gap: var(--space-md);
    justify-content: center;
    margin-bottom: var(--space-xl);
  }

  .error-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-md) var(--space-lg);
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-lg);
    color: var(--accent-red);
  }

  .webcam-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-lg);
    margin-bottom: var(--space-lg);
  }

  .video-section h3,
  .result-section h3 {
    font-size: 0.85rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-md);
  }

  .video-wrapper,
  .result-wrapper {
    aspect-ratio: 4 / 3;
    border-radius: var(--radius-md);
    overflow: hidden;
    background: var(--bg-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  .video-wrapper.portrait,
  .result-wrapper.portrait {
    aspect-ratio: 3 / 4;
  }

  video {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: var(--radius-md);
    background: var(--bg-secondary);
  }
  video.hidden {
    display: none;
  }

  .camera-placeholder {
    text-align: center;
    color: var(--text-muted);
    padding: var(--space-xl);
  }
  .result-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  .result-badges {
    position: absolute;
    bottom: var(--space-md);
    left: var(--space-md);
    display: flex;
    gap: var(--space-sm);
  }

  .skeleton-img {
    width: 100%;
    height: 100%;
  }

  .detections-list h3 {
    margin-bottom: var(--space-md);
  }

  .detection-cards {
    display: flex;
    gap: var(--space-md);
    flex-wrap: wrap;
  }

  .detection-item {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    padding: var(--space-sm) var(--space-md);
    background: var(--bg-glass-light);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(255, 255, 255, 0.04);
  }

  .detection-index {
    font-weight: 700;
    color: var(--text-muted);
    font-size: 0.85rem;
  }

  .detection-conf {
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    color: var(--text-secondary);
    font-size: 0.9rem;
  }

  @media (max-width: 768px) {
    .camera-controls {
      flex-direction: column;
      align-items: stretch;
    }
    .webcam-layout {
      grid-template-columns: 1fr;
    }
    .video-wrapper,
    .result-wrapper,
    .video-wrapper.portrait,
    .result-wrapper.portrait {
      aspect-ratio: auto;
      min-height: 280px;
    }
    .result-badges {
      left: 0.75rem;
      right: 0.75rem;
      bottom: 0.75rem;
      flex-wrap: wrap;
    }
  }
</style>
