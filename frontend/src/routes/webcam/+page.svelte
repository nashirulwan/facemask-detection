<script>
  import { onMount } from 'svelte';
  import { createPredictionSocket, predictImage } from '$lib/api.js';

  const LIVE_FPS = 3;
  const JPEG_QUALITY = 0.72;
  const MAX_FRAME_WIDTH = 640;

  let videoEl = $state(null);
  let canvasEl = $state(null);
  let stream = $state(null);
  let socket = $state(null);
  let cameraActive = $state(false);
  let liveMode = $state(false);
  let result = $state(null);
  let loading = $state(false);
  let error = $state(null);
  let capturedImageUrl = $state(null);
  let frameOrientation = $state('landscape');
  let connectionStatus = $state('idle');
  let frameRequestInFlight = false;
  let liveLoopId = 0;
  let lastFrameSentAt = 0;

  async function startCamera() {
    if (cameraActive) return;

    error = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user',
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
        audio: false,
      });

      if (videoEl) {
        videoEl.srcObject = stream;
        videoEl.onloadedmetadata = async () => {
          frameOrientation = videoEl.videoHeight > videoEl.videoWidth ? 'portrait' : 'landscape';
          await videoEl.play();
        };
        await videoEl.play();
        frameOrientation = videoEl.videoHeight > videoEl.videoWidth ? 'portrait' : 'landscape';
      }

      cameraActive = true;
    } catch (err) {
      error = 'Could not access camera. Please allow camera permissions.';
    }
  }

  function stopCamera() {
    stopLiveDetection();

    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }

    cameraActive = false;
    loading = false;
    frameOrientation = 'landscape';
  }

  function closeSocket() {
    if (socket) {
      socket.onopen = null;
      socket.onmessage = null;
      socket.onerror = null;
      socket.onclose = null;
      socket.close();
      socket = null;
    }
  }

  function stopLiveDetection() {
    liveMode = false;
    frameRequestInFlight = false;
    lastFrameSentAt = 0;
    connectionStatus = cameraActive ? 'camera-only' : 'idle';

    if (liveLoopId) {
      cancelAnimationFrame(liveLoopId);
      liveLoopId = 0;
    }

    closeSocket();
  }

  function drawCurrentFrame() {
    if (!videoEl || !canvasEl || videoEl.readyState < 2) return false;

    const scale = Math.min(1, MAX_FRAME_WIDTH / videoEl.videoWidth);
    const width = Math.max(1, Math.round(videoEl.videoWidth * scale));
    const height = Math.max(1, Math.round(videoEl.videoHeight * scale));
    const ctx = canvasEl.getContext('2d');

    canvasEl.width = width;
    canvasEl.height = height;
    ctx.drawImage(videoEl, 0, 0, width, height);
    return true;
  }

  function scheduleLiveLoop() {
    liveLoopId = requestAnimationFrame(pumpFrames);
  }

  function pumpFrames(timestamp) {
    if (!liveMode || !socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    const frameInterval = 1000 / LIVE_FPS;
    const canSendFrame = !frameRequestInFlight && timestamp - lastFrameSentAt >= frameInterval;

    if (canSendFrame && drawCurrentFrame()) {
      frameRequestInFlight = true;
      lastFrameSentAt = timestamp;

      canvasEl.toBlob(async (blob) => {
        if (!blob || !socket || socket.readyState !== WebSocket.OPEN || !liveMode) {
          frameRequestInFlight = false;
          return;
        }

        try {
          const buffer = await blob.arrayBuffer();
          socket.send(buffer);
        } catch (err) {
          frameRequestInFlight = false;
          error = 'Failed to send webcam frame to the server.';
        }
      }, 'image/jpeg', JPEG_QUALITY);
    }

    scheduleLiveLoop();
  }

  async function startLiveDetection() {
    error = null;
    result = null;
    capturedImageUrl = null;

    if (!cameraActive) {
      await startCamera();
    }

    if (!cameraActive || liveMode) return;

    connectionStatus = 'connecting';
    socket = createPredictionSocket('webcam');

    socket.onopen = () => {
      liveMode = true;
      loading = false;
      frameRequestInFlight = false;
      lastFrameSentAt = 0;
      connectionStatus = 'live';
      scheduleLiveLoop();
    };

    socket.onmessage = (event) => {
      try {
        result = JSON.parse(event.data);
        frameRequestInFlight = false;
      } catch (err) {
        frameRequestInFlight = false;
        error = 'Received an invalid realtime response from the server.';
      }
    };

    socket.onerror = () => {
      error = 'Realtime detection socket failed. Try again in a moment.';
      connectionStatus = 'error';
      frameRequestInFlight = false;
    };

    socket.onclose = () => {
      if (liveMode) {
        error ??= 'Realtime detection stopped because the connection was closed.';
      }
      liveMode = false;
      frameRequestInFlight = false;
      connectionStatus = cameraActive ? 'camera-only' : 'idle';
      socket = null;
    };
  }

  async function captureAndDetect() {
    if (!videoEl || !canvasEl || liveMode) return;
    if (!drawCurrentFrame()) return;

    loading = true;
    error = null;
    result = null;
    capturedImageUrl = canvasEl.toDataURL('image/jpeg', 0.9);

    canvasEl.toBlob(async (blob) => {
      if (!blob) {
        loading = false;
        error = 'Could not capture a frame from the webcam.';
        return;
      }

      const file = new File([blob], 'webcam_capture.jpg', { type: 'image/jpeg' });
      try {
        result = await predictImage(file, 'webcam');
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
    error = null;
  }

  onMount(() => {
    return () => stopCamera();
  });
</script>

<svelte:head>
  <title>Webcam — MaskDetect</title>
  <meta name="description" content="Realtime and snapshot face mask detection using your webcam." />
</svelte:head>

<section class="section">
  <div class="container">
    <div class="page-header animate-in">
      <h1><span class="gradient-text">Webcam Detection</span></h1>
      <p>Use snapshot mode for a stable single-shot test, or enable realtime mode for live webcam inference.</p>
    </div>

    <div class="camera-controls animate-in delay-1">
      {#if !cameraActive}
        <button class="btn btn-primary btn-lg" onclick={startCamera}>Start Camera</button>
      {:else}
        <button class="btn btn-secondary" onclick={stopCamera}>Stop Camera</button>
        {#if !liveMode}
          <button class="btn btn-primary btn-lg" onclick={startLiveDetection}>Start Realtime</button>
          <button class="btn btn-ghost" onclick={captureAndDetect}>Capture Snapshot</button>
        {:else}
          <button class="btn btn-primary btn-lg" onclick={stopLiveDetection}>Stop Realtime</button>
        {/if}
        {#if !liveMode && (result || capturedImageUrl)}
          <button class="btn btn-ghost" onclick={resetCapture}>Clear Result</button>
        {/if}
      {/if}
    </div>

    <div class="mode-note animate-in delay-1">
      <span class="badge" class:badge-green={liveMode} class:badge-blue={!liveMode}>
        {#if liveMode}
          Realtime stream: {LIVE_FPS} FPS target
        {:else}
          Snapshot mode: one captured frame per prediction
        {/if}
      </span>
      <span class="status-text">Connection: {connectionStatus}</span>
    </div>

    {#if error}
      <div class="error-banner animate-in">
        <span>{error}</span>
      </div>
    {/if}

    <div class="webcam-layout animate-in delay-2">
      <div class="video-section glass-card">
        <h3>Camera Feed</h3>
        <div class="video-wrapper" class:portrait={frameOrientation === 'portrait'}>
          {#if !cameraActive}
            <div class="camera-placeholder">
              <p>Camera is off. Click "Start Camera" to begin.</p>
            </div>
          {/if}
          <!-- svelte-ignore element_invalid_self_closing_tag -->
          <video bind:this={videoEl} class:hidden={!cameraActive} playsinline muted />
        </div>
      </div>

      <div class="result-section glass-card">
        <h3>{liveMode ? 'Realtime Result' : 'Detection Result'}</h3>
        <div class="result-wrapper" class:portrait={frameOrientation === 'portrait'}>
          {#if loading}
            <div class="skeleton-img skeleton"></div>
          {:else if result}
            <img src="data:image/jpeg;base64,{result.annotated_image}" alt="Detection result" />
            <div class="result-badges">
              <span class="badge badge-green">{result.faces_detected} face{result.faces_detected !== 1 ? 's' : ''}</span>
              {#if result.processing_time_ms}
                <span class="badge badge-blue">{result.processing_time_ms.toFixed(0)}ms</span>
              {/if}
            </div>
          {:else if capturedImageUrl}
            <img src={capturedImageUrl} alt="Captured frame" />
          {:else}
            <div class="camera-placeholder">
              <p>{liveMode ? 'Realtime stream is starting.' : 'Capture a frame to see detection results.'}</p>
            </div>
          {/if}
        </div>
      </div>
    </div>

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

  .page-header h1 {
    margin-bottom: var(--space-sm);
  }

  .page-header p {
    max-width: 640px;
    margin: 0 auto;
  }

  .camera-controls {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-md);
    justify-content: center;
    margin-bottom: var(--space-md);
  }

  .mode-note {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-sm);
    align-items: center;
    justify-content: center;
    margin-bottom: var(--space-xl);
  }

  .status-text {
    color: var(--text-muted);
    font-size: 0.9rem;
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
  .result-section h3,
  .detections-list h3 {
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

  video,
  .result-wrapper img {
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

  .result-badges {
    position: absolute;
    left: var(--space-md);
    bottom: var(--space-md);
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-sm);
  }

  .detections-list {
    margin-top: var(--space-lg);
  }

  .detection-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: var(--space-md);
  }

  .detection-item {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    padding: 0.9rem 1rem;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    min-width: 0;
  }

  .detection-index {
    width: 1.75rem;
    height: 1.75rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-primary);
    font-size: 0.8rem;
    flex-shrink: 0;
  }

  .detection-conf {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-left: auto;
  }

  .skeleton-img {
    width: 100%;
    height: 100%;
    border-radius: var(--radius-md);
  }

  @media (max-width: 900px) {
    .webcam-layout {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 640px) {
    .page-header p {
      max-width: 100%;
    }

    .camera-controls {
      gap: var(--space-sm);
    }

    .camera-controls :global(.btn) {
      width: 100%;
    }

    .mode-note {
      align-items: flex-start;
      justify-content: flex-start;
    }

    .result-badges {
      left: var(--space-sm);
      right: var(--space-sm);
      bottom: var(--space-sm);
    }

    .detection-item {
      padding: 0.8rem;
    }
  }
</style>
