<script>
  const features = [
    {
      title: 'Image Upload',
      desc: 'Upload any image and detect face masks instantly with bounding box annotations.',
      href: '/detect',
      color: 'green',
    },
    {
      title: 'Webcam Demo',
      desc: 'Real-time face mask detection using your webcam with live bounding boxes.',
      href: '/webcam',
      color: 'blue',
    },
    {
      title: 'Experiments',
      desc: 'Explore training metrics, accuracy curves, confusion matrix, and classification report.',
      href: '/experiments',
      color: 'purple',
    },
    {
      title: 'About',
      desc: 'Learn about the reproduced research paper, model architecture, and methodology.',
      href: '/about',
      color: 'amber',
    },
  ];

  const stats = [
    { value: '97.25%', label: 'Test Accuracy' },
    { value: '4,000', label: 'Training Images' },
    { value: '2', label: 'Classes' },
    { value: '<500ms', label: 'Inference Time' },
  ];
</script>

<svelte:head>
  <title>MaskDetect — Real-time Face Mask Detection</title>
  <meta name="description" content="Real-time face mask detection web application powered by a custom CNN model. Upload images or use your webcam for instant detection." />
</svelte:head>

<!-- Hero Section -->
<section class="hero">
  <div class="container">
    <div class="hero-content animate-in">
      <h1 class="hero-title">
        Real-time <span class="gradient-text">Face Mask</span> Detection
      </h1>
      <p class="hero-subtitle">
        A simple web interface for running a CNN-based face mask detector on images
        and webcam captures.
      </p>
      <div class="hero-actions">
        <a href="/detect" class="btn btn-primary btn-lg">Start Detecting</a>
        <a href="/about" class="btn btn-ghost btn-lg">About</a>
      </div>
    </div>

    <!-- Stats bar -->
    <div class="stats-bar animate-in delay-2">
      {#each stats as stat}
        <div class="stat-card">
          <div class="stat-value gradient-text">{stat.value}</div>
          <div class="stat-label">{stat.label}</div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Decorative elements -->
  <div class="hero-glow hero-glow-1"></div>
  <div class="hero-glow hero-glow-2"></div>
</section>

<!-- Features Section -->
<section class="section">
  <div class="container">
    <div class="section-header animate-in">
      <h2>Explore <span class="gradient-text">Features</span></h2>
      <p>Everything you need to understand and demo face mask detection.</p>
    </div>

    <div class="features-grid">
      {#each features as feature, i}
        <a href={feature.href} class="feature-card glass-card animate-in delay-{i + 1}" data-color={feature.color}>
          <h3>{feature.title}</h3>
          <p>{feature.desc}</p>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- How It Works Section -->
<section class="section how-it-works">
  <div class="container">
    <div class="section-header animate-in">
      <h2>How It <span class="gradient-text">Works</span></h2>
      <p>A two-stage pipeline: face detection followed by mask classification.</p>
    </div>

    <div class="pipeline animate-in delay-1">
      <div class="pipeline-step">
        <div class="step-number">1</div>
        <h3>Input Image</h3>
        <p>Upload an image or capture from webcam</p>
      </div>
      <div class="pipeline-step">
        <div class="step-number">2</div>
        <h3>Face Detection</h3>
        <p>SSD network finds all faces (300×300 blob)</p>
      </div>
      <div class="pipeline-step">
        <div class="step-number">3</div>
        <h3>Mask Classification</h3>
        <p>Custom CNN classifies each face (96×96 crop)</p>
      </div>
      <div class="pipeline-step">
        <div class="step-number">4</div>
        <h3>Results</h3>
        <p>Annotated image with labels & confidence</p>
      </div>
    </div>
  </div>
</section>

<style>
  /* ===== HERO ===== */
  .hero {
    position: relative;
    padding: var(--space-3xl) 0;
    min-height: 80vh;
    display: flex;
    align-items: center;
    overflow: hidden;
  }

  .hero-content {
    text-align: center;
    max-width: 700px;
    margin: 0 auto;
  }

  .hero-title {
    font-size: clamp(2.5rem, 6vw, 4rem);
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: var(--space-lg);
  }

  .hero-subtitle {
    font-size: 1.15rem;
    color: var(--text-secondary);
    max-width: 550px;
    margin: 0 auto var(--space-xl);
    line-height: 1.7;
  }

  .hero-actions {
    display: flex;
    gap: var(--space-md);
    justify-content: center;
    flex-wrap: wrap;
  }

  .stats-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-md);
    margin-top: var(--space-3xl);
    padding: var(--space-lg);
    background: var(--bg-glass);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: var(--radius-xl);
  }

  .hero-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(120px);
    pointer-events: none;
    z-index: -1;
  }
  .hero-glow-1 {
    width: 500px;
    height: 500px;
    background: rgba(16, 185, 129, 0.12);
    top: -100px;
    right: -100px;
    animation: float 6s ease-in-out infinite;
  }
  .hero-glow-2 {
    width: 400px;
    height: 400px;
    background: rgba(139, 92, 246, 0.1);
    bottom: -100px;
    left: -50px;
    animation: float 8s ease-in-out infinite reverse;
  }

  /* ===== SECTION HEADER ===== */
  .section-header {
    text-align: center;
    margin-bottom: var(--space-2xl);
  }
  .section-header p {
    margin-top: var(--space-sm);
    font-size: 1.05rem;
  }

  /* ===== FEATURES ===== */
  .features-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-lg);
  }

  .feature-card {
    display: flex;
    flex-direction: column;
    text-decoration: none;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  .feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-hero);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform var(--transition-slow);
  }
  .feature-card:hover::before {
    transform: scaleX(1);
  }

  .feature-card h3 {
    font-size: 1.2rem;
    margin-bottom: var(--space-sm);
  }

  .feature-card p {
    font-size: 0.9rem;
    flex: 1;
  }

  /* ===== PIPELINE ===== */
  .pipeline {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-md);
    flex-wrap: wrap;
  }

  .pipeline-step {
    flex: 1;
    min-width: 160px;
    text-align: center;
    padding: var(--space-xl) var(--space-md);
    background: var(--bg-glass);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: var(--radius-lg);
    backdrop-filter: blur(8px);
  }

  .step-number {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--gradient-hero);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.1rem;
    margin: 0 auto var(--space-md);
    color: white;
  }

  .pipeline-step h3 {
    font-size: 1rem;
    margin-bottom: var(--space-xs);
  }
  .pipeline-step p {
    font-size: 0.8rem;
  }

  /* ===== RESPONSIVE ===== */
  @media (max-width: 768px) {
    .hero {
      min-height: auto;
      padding: var(--space-2xl) 0;
    }
    .hero-title {
      font-size: 2rem;
    }
    .hero-subtitle {
      font-size: 1rem;
    }
    .features-grid {
      grid-template-columns: 1fr;
    }
    .stats-bar {
      grid-template-columns: repeat(2, 1fr);
      padding: 1rem;
      gap: 0.75rem;
    }
    .pipeline {
      flex-direction: column;
    }
    .pipeline-step {
      width: 100%;
      min-width: 0;
      text-align: left;
    }
  }
</style>
