<script>
  import { onMount } from 'svelte';
  import { getModelInfo } from '$lib/api.js';

  let info = $state(null);
  let loading = $state(true);

  onMount(async () => {
    try {
      info = await getModelInfo();
    } catch (err) {
      // Use fallback data if backend is not running
      info = {
        paper_title: 'A real time face mask detection system using convolutional neural network',
        paper_doi: '10.1007/s11042-022-12166-x',
        architecture: '5× Conv2D(16→256) + MaxPool → Flatten → Dense(1024) → Dense(64) → Dense(2, softmax)',
        input_size: 96,
        num_classes: 2,
        class_labels: ['with_mask', 'without_mask'],
        face_detector: 'OpenCV DNN SSD (res10_300x300_ssd_iter_140000)',
      };
    }
    loading = false;
  });

  const layers = [
    { name: 'Conv2D(16, 3×3)', type: 'conv', desc: 'First convolutional layer with ReLU' },
    { name: 'MaxPooling2D(2×2)', type: 'pool', desc: 'Spatial downsampling' },
    { name: 'Conv2D(32, 3×3)', type: 'conv', desc: 'Increasing feature depth' },
    { name: 'MaxPooling2D(2×2)', type: 'pool', desc: 'Spatial downsampling' },
    { name: 'Conv2D(64, 3×3)', type: 'conv', desc: 'Mid-level features' },
    { name: 'MaxPooling2D(2×2)', type: 'pool', desc: 'Spatial downsampling' },
    { name: 'Conv2D(128, 3×3)', type: 'conv', desc: 'High-level features' },
    { name: 'MaxPooling2D(2×2)', type: 'pool', desc: 'Spatial downsampling' },
    { name: 'Conv2D(256, 3×3)', type: 'conv', desc: 'Deep features' },
    { name: 'MaxPooling2D(2×2)', type: 'pool', desc: 'Spatial downsampling' },
    { name: 'Flatten', type: 'flat', desc: 'Reshape to 1D vector' },
    { name: 'Dense(1024)', type: 'dense', desc: 'Fully connected' },
    { name: 'Dense(64)', type: 'dense', desc: 'Dimensionality reduction' },
    { name: 'Dense(2, softmax)', type: 'out', desc: 'with_mask / without_mask' },
  ];

  const techStack = [
    { icon: '🐍', name: 'FastAPI', desc: 'Backend REST API & WebSocket' },
    { icon: '🧡', name: 'SvelteKit', desc: 'Frontend web framework' },
    { icon: '🧠', name: 'TensorFlow/Keras', desc: 'CNN model inference' },
    { icon: '👁️', name: 'OpenCV', desc: 'Face detection (DNN SSD)' },
    { icon: '🐳', name: 'Docker', desc: 'Containerized deployment' },
    { icon: '📊', name: 'Chart.js', desc: 'Interactive training charts' },
  ];
</script>

<svelte:head>
  <title>About — MaskDetect</title>
  <meta name="description" content="About the face mask detection paper, model architecture, and team." />
</svelte:head>

<section class="section">
  <div class="container">
    <div class="page-header animate-in">
      <h1>📄 <span class="gradient-text">About This Project</span></h1>
      <p>Reproducing a research paper on real-time face mask detection using CNN.</p>
    </div>

    <!-- Paper info -->
    <div class="glass-card paper-card animate-in delay-1">
      <div class="paper-badge">
        <span class="badge badge-blue">📝 Research Paper</span>
      </div>
      <h2>{info?.paper_title || 'Loading...'}</h2>
      <div class="paper-meta">
        <span class="meta-item">
          DOI: <a href="https://doi.org/{info?.paper_doi}" target="_blank" rel="noopener">{info?.paper_doi}</a>
        </span>
      </div>
      <p class="paper-desc">
        This paper proposes a real-time face mask detection system for both static images and live video.
        The system uses a two-stage pipeline: first, an SSD-based face detector locates faces in the image,
        then a custom CNN classifies each detected face as wearing a mask or not.
      </p>
      <div class="paper-specs">
        <div class="spec-item">
          <span class="spec-key">Input Size</span>
          <span class="spec-val">{info?.input_size}×{info?.input_size} RGB</span>
        </div>
        <div class="spec-item">
          <span class="spec-key">Classes</span>
          <span class="spec-val">{info?.num_classes} ({info?.class_labels?.join(', ')})</span>
        </div>
        <div class="spec-item">
          <span class="spec-key">Face Detector</span>
          <span class="spec-val">{info?.face_detector}</span>
        </div>
        <div class="spec-item">
          <span class="spec-key">Loss Function</span>
          <span class="spec-val">Binary Crossentropy</span>
        </div>
        <div class="spec-item">
          <span class="spec-key">Optimizer</span>
          <span class="spec-val">Adam (lr=0.0005)</span>
        </div>
        <div class="spec-item">
          <span class="spec-key">Reported Accuracy</span>
          <span class="spec-val">~98%</span>
        </div>
      </div>
    </div>

    <!-- Model Architecture -->
    <div class="glass-card animate-in delay-2">
      <h2>🧠 Model Architecture</h2>
      <p class="arch-subtitle">Custom CNN with 5 convolutional blocks followed by dense classification layers.</p>

      <div class="arch-layers">
        {#each layers as layer, i}
          <div class="layer-item" class:conv={layer.type === 'conv'} class:pool={layer.type === 'pool'} class:dense={layer.type === 'dense'} class:flat={layer.type === 'flat'} class:out={layer.type === 'out'}>
            <span class="layer-name">{layer.name}</span>
            <span class="layer-desc">{layer.desc}</span>
          </div>
          {#if i < layers.length - 1}
            <div class="layer-connector">↓</div>
          {/if}
        {/each}
      </div>
    </div>

    <!-- Tech Stack -->
    <div class="glass-card animate-in delay-3">
      <h2>🛠️ Tech Stack</h2>
      <div class="tech-grid">
        {#each techStack as tech}
          <div class="tech-item">
            <span class="tech-icon">{tech.icon}</span>
            <div>
              <strong>{tech.name}</strong>
              <p>{tech.desc}</p>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- References -->
    <div class="glass-card animate-in delay-3">
      <h2>🔗 References</h2>
      <div class="references">
        <a href="https://doi.org/10.1007/s11042-022-12166-x" target="_blank" rel="noopener" class="ref-link">
          <span class="ref-icon">📝</span>
          <div>
            <strong>Original Paper</strong>
            <p>DOI: 10.1007/s11042-022-12166-x</p>
          </div>
          <span class="ref-arrow">↗</span>
        </a>
        <a href="https://github.com/techyhoney/Facemask_Detection" target="_blank" rel="noopener" class="ref-link">
          <span class="ref-icon">💻</span>
          <div>
            <strong>Upstream Repository</strong>
            <p>github.com/techyhoney/Facemask_Detection (MIT License)</p>
          </div>
          <span class="ref-arrow">↗</span>
        </a>
      </div>
    </div>
  </div>
</section>

<style>
  .page-header {
    text-align: center;
    margin-bottom: var(--space-2xl);
  }
  .page-header h1 { margin-bottom: var(--space-sm); }
  .page-header p {
    max-width: 550px;
    margin: 0 auto;
  }

  .glass-card {
    margin-bottom: var(--space-xl);
  }

  .glass-card h2 {
    font-size: 1.4rem;
    margin-bottom: var(--space-md);
  }

  /* Paper card */
  .paper-card {
    border: 1px solid rgba(59, 130, 246, 0.2);
  }
  .paper-badge {
    margin-bottom: var(--space-md);
  }
  .paper-card h2 {
    font-size: 1.3rem;
    line-height: 1.4;
    margin-bottom: var(--space-sm);
  }
  .paper-meta {
    margin-bottom: var(--space-md);
  }
  .meta-item {
    font-size: 0.85rem;
    color: var(--text-muted);
  }
  .paper-desc {
    margin-bottom: var(--space-lg);
    font-size: 0.95rem;
  }
  .paper-specs {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-sm);
  }
  .spec-item {
    padding: var(--space-sm) var(--space-md);
    background: var(--bg-glass-light);
    border-radius: var(--radius-sm);
  }
  .spec-key {
    display: block;
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 2px;
  }
  .spec-val {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-primary);
  }

  /* Architecture */
  .arch-subtitle {
    font-size: 0.95rem;
    margin-bottom: var(--space-lg);
  }
  .arch-layers {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    max-width: 500px;
    margin: 0 auto;
  }
  .layer-item {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
  }
  .layer-item.conv { background: rgba(16, 185, 129, 0.1); border-left: 3px solid var(--accent-green); }
  .layer-item.pool { background: rgba(59, 130, 246, 0.08); border-left: 3px solid var(--accent-blue); }
  .layer-item.dense { background: rgba(139, 92, 246, 0.1); border-left: 3px solid var(--accent-purple); }
  .layer-item.flat { background: rgba(245, 158, 11, 0.08); border-left: 3px solid var(--accent-amber); }
  .layer-item.out { background: rgba(239, 68, 68, 0.1); border-left: 3px solid var(--accent-red); }

  .layer-name {
    font-weight: 600;
    font-family: 'Courier New', monospace;
    color: var(--text-primary);
  }
  .layer-desc {
    font-size: 0.75rem;
    color: var(--text-muted);
  }
  .layer-connector {
    color: var(--text-muted);
    font-size: 0.8rem;
  }

  /* Tech Stack */
  .tech-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-md);
  }
  .tech-item {
    display: flex;
    align-items: center;
    gap: var(--space-md);
    padding: var(--space-md);
    background: var(--bg-glass-light);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(255, 255, 255, 0.04);
  }
  .tech-icon {
    font-size: 1.5rem;
  }
  .tech-item strong {
    display: block;
    font-size: 0.9rem;
    margin-bottom: 2px;
  }
  .tech-item p {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin: 0;
  }

  /* References */
  .references {
    display: flex;
    flex-direction: column;
    gap: var(--space-sm);
  }
  .ref-link {
    display: flex;
    align-items: center;
    gap: var(--space-md);
    padding: var(--space-md) var(--space-lg);
    background: var(--bg-glass-light);
    border-radius: var(--radius-md);
    border: 1px solid rgba(255, 255, 255, 0.04);
    transition: all var(--transition-fast);
    text-decoration: none;
  }
  .ref-link:hover {
    background: var(--bg-card-hover);
    border-color: rgba(255, 255, 255, 0.1);
  }
  .ref-icon {
    font-size: 1.5rem;
  }
  .ref-link strong {
    display: block;
    color: var(--text-primary);
    font-size: 0.95rem;
  }
  .ref-link p {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin: 0;
  }
  .ref-arrow {
    margin-left: auto;
    color: var(--text-muted);
    font-size: 1.2rem;
    transition: transform var(--transition-fast);
  }
  .ref-link:hover .ref-arrow {
    transform: translate(2px, -2px);
    color: var(--accent-blue);
  }

  @media (max-width: 768px) {
    .paper-specs { grid-template-columns: 1fr 1fr; }
    .tech-grid { grid-template-columns: 1fr; }
  }
</style>
