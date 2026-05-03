<script>
  import '../app.css';

  let { children } = $props();

  let mobileMenuOpen = $state(false);
  let scrolled = $state(false);

  const navLinks = [
    { href: '/', label: 'Home', icon: '🏠' },
    { href: '/detect', label: 'Detect', icon: '🔍' },
    { href: '/webcam', label: 'Webcam', icon: '📹' },
    { href: '/experiments', label: 'Experiments', icon: '📊' },
    { href: '/about', label: 'About', icon: '📄' },
  ];

  function toggleMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  $effect(() => {
    function handleScroll() {
      scrolled = window.scrollY > 20;
    }
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });
</script>

<svelte:head>
  <title>Facemask Detector — Real-time Face Mask Detection</title>
  <meta name="description" content="Real-time face mask detection web application powered by a custom CNN, reproducing the research paper." />
</svelte:head>

<nav class="navbar" class:scrolled>
  <div class="nav-container">
    <a href="/" class="nav-brand">
      <span class="brand-icon">🛡️</span>
      <span class="brand-text">Mask<span class="gradient-text">Detect</span></span>
    </a>

    <div class="nav-links" class:open={mobileMenuOpen}>
      {#each navLinks as link}
        <a href={link.href} class="nav-link" onclick={() => mobileMenuOpen = false}>
          <span class="nav-icon">{link.icon}</span>
          {link.label}
        </a>
      {/each}
    </div>

    <button class="menu-toggle" onclick={toggleMenu} aria-label="Toggle menu">
      <span class="hamburger" class:open={mobileMenuOpen}></span>
    </button>
  </div>
</nav>

<main class="main-content">
  {@render children()}
</main>

<footer class="footer">
  <div class="container">
    <div class="footer-content">
      <div class="footer-brand">
        <span class="brand-icon">🛡️</span>
        <span>Mask<span class="gradient-text">Detect</span></span>
      </div>
      <p class="footer-text">
        Reproducing "A real time face mask detection system using CNN"
      </p>
      <div class="footer-links">
        <a href="https://doi.org/10.1007/s11042-022-12166-x" target="_blank" rel="noopener">Paper</a>
        <span class="footer-sep">•</span>
        <a href="https://github.com/techyhoney/Facemask_Detection" target="_blank" rel="noopener">Upstream</a>
      </div>
    </div>
  </div>
</footer>

<style>
  /* ===== NAVBAR ===== */
  .navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    height: var(--nav-height);
    display: flex;
    align-items: center;
    background: rgba(10, 10, 15, 0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid transparent;
    transition: all var(--transition-base);
  }
  .navbar.scrolled {
    background: rgba(10, 10, 15, 0.92);
    border-bottom-color: rgba(255, 255, 255, 0.06);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }

  .nav-container {
    width: 100%;
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 var(--space-lg);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .nav-brand {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    text-decoration: none;
  }
  .brand-icon {
    font-size: 1.5rem;
  }
  .brand-text {
    letter-spacing: -0.02em;
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: var(--space-xs);
  }

  .nav-link {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0.5rem 0.9rem;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary);
    text-decoration: none;
    transition: all var(--transition-fast);
  }
  .nav-link:hover {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.05);
  }
  .nav-icon {
    font-size: 1rem;
  }

  .menu-toggle {
    display: none;
    background: none;
    border: none;
    padding: 8px;
    cursor: pointer;
  }

  .hamburger {
    display: block;
    width: 24px;
    height: 2px;
    background: var(--text-primary);
    position: relative;
    transition: all var(--transition-fast);
  }
  .hamburger::before,
  .hamburger::after {
    content: '';
    position: absolute;
    width: 24px;
    height: 2px;
    background: var(--text-primary);
    transition: all var(--transition-fast);
  }
  .hamburger::before { top: -7px; }
  .hamburger::after { top: 7px; }
  .hamburger.open { background: transparent; }
  .hamburger.open::before { top: 0; transform: rotate(45deg); }
  .hamburger.open::after { top: 0; transform: rotate(-45deg); }

  /* ===== MAIN ===== */
  .main-content {
    padding-top: var(--nav-height);
    min-height: 100vh;
    position: relative;
    z-index: 1;
  }

  /* ===== FOOTER ===== */
  .footer {
    position: relative;
    z-index: 1;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding: var(--space-xl) 0;
  }
  .footer-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-sm);
    text-align: center;
  }
  .footer-brand {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    font-weight: 700;
    font-size: 1.1rem;
  }
  .footer-text {
    font-size: 0.85rem;
    color: var(--text-muted);
  }
  .footer-links {
    display: flex;
    gap: var(--space-sm);
    font-size: 0.85rem;
  }
  .footer-sep {
    color: var(--text-muted);
  }

  /* ===== MOBILE ===== */
  @media (max-width: 768px) {
    .menu-toggle {
      display: block;
    }
    .nav-links {
      position: fixed;
      top: var(--nav-height);
      left: 0;
      right: 0;
      background: rgba(10, 10, 15, 0.97);
      backdrop-filter: blur(20px);
      flex-direction: column;
      padding: var(--space-lg);
      gap: var(--space-xs);
      transform: translateY(-120%);
      transition: transform var(--transition-slow);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    .nav-links.open {
      transform: translateY(0);
    }
    .nav-link {
      width: 100%;
      padding: 0.75rem 1rem;
      font-size: 1rem;
    }
  }
</style>
