<script>
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  import {
    getExperimentSummary,
    getClassificationReport,
    getConfusionMatrix,
    getTrainingHistory,
    getCurveUrl,
  } from '$lib/api.js';

  Chart.register(...registerables);

  let summary = $state(null);
  let report = $state(null);
  let matrix = $state(null);
  let history = null;
  let loading = $state(true);
  let error = $state(null);

  // Canvas refs: plain let (NOT $state) — Chart.js needs the raw DOM node,
  // not a Svelte 5 Proxy, otherwise it throws state_descriptors_fixed.
  let accChartCanvas;
  let lossChartCanvas;
  let accChart = null;
  let lossChart = null;

  onMount(async () => {
    try {
      const [s, r, m, h] = await Promise.all([
        getExperimentSummary(),
        getClassificationReport(),
        getConfusionMatrix(),
        getTrainingHistory(),
      ]);
      summary = s;
      report = r;
      matrix = m;
      history = h;
      loading = false;

      // Wait for DOM to render
      await new Promise(r => setTimeout(r, 100));
      renderCharts();
    } catch (err) {
      error = err.message || 'Failed to load experiment data. Is the backend running?';
      loading = false;
    }
  });

  function renderCharts() {
    if (!history || !accChartCanvas || !lossChartCanvas) return;

    const epochs = Array.from({ length: history.accuracy.length }, (_, i) => i + 1);
    const chartDefaults = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#a0a0b8', font: { family: 'Inter' } },
        },
      },
      scales: {
        x: {
          title: { display: true, text: 'Epoch', color: '#6b6b80' },
          ticks: { color: '#6b6b80' },
          grid: { color: 'rgba(255,255,255,0.04)' },
        },
        y: {
          ticks: { color: '#6b6b80' },
          grid: { color: 'rgba(255,255,255,0.04)' },
        },
      },
    };

    // Accuracy chart
    accChart = new Chart(accChartCanvas, {
      type: 'line',
      data: {
        labels: epochs,
        datasets: [
          {
            label: 'Train Accuracy',
            data: history.accuracy,
            borderColor: '#10B981',
            backgroundColor: 'rgba(16,185,129,0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2,
          },
          {
            label: 'Val Accuracy',
            data: history.val_accuracy,
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59,130,246,0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2,
          },
        ],
      },
      options: {
        ...chartDefaults,
        scales: {
          ...chartDefaults.scales,
          y: { ...chartDefaults.scales.y, title: { display: true, text: 'Accuracy', color: '#6b6b80' } },
        },
      },
    });

    // Loss chart
    lossChart = new Chart(lossChartCanvas, {
      type: 'line',
      data: {
        labels: epochs,
        datasets: [
          {
            label: 'Train Loss',
            data: history.loss,
            borderColor: '#EF4444',
            backgroundColor: 'rgba(239,68,68,0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2,
          },
          {
            label: 'Val Loss',
            data: history.val_loss,
            borderColor: '#F59E0B',
            backgroundColor: 'rgba(245,158,11,0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2,
          },
        ],
      },
      options: {
        ...chartDefaults,
        scales: {
          ...chartDefaults.scales,
          y: { ...chartDefaults.scales.y, title: { display: true, text: 'Loss', color: '#6b6b80' } },
        },
      },
    });
  }
</script>

<svelte:head>
  <title>Experiments — MaskDetect</title>
  <meta name="description" content="Training experiment results: accuracy, loss curves, confusion matrix, and classification report." />
</svelte:head>

<section class="section">
  <div class="container">
    <div class="page-header animate-in">
      <h1>📊 <span class="gradient-text">Experiment Results</span></h1>
      <p>Training metrics and evaluation results from reproducing the paper.</p>
    </div>

    {#if error}
      <div class="error-banner animate-in">
        <span>⚠️ {error}</span>
      </div>
    {/if}

    {#if loading}
      <div class="loading-grid grid-4">
        {#each Array(4) as _}
          <div class="skeleton" style="height: 100px; border-radius: var(--radius-md)"></div>
        {/each}
      </div>
    {:else if summary}
      <!-- Stats overview -->
      <div class="stats-grid grid-4 animate-in delay-1">
        <div class="stat-card glass-card">
          <div class="stat-value gradient-text">{(summary.test_accuracy * 100).toFixed(2)}%</div>
          <div class="stat-label">Test Accuracy</div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-value" style="color: var(--accent-green)">{summary.num_images.toLocaleString()}</div>
          <div class="stat-label">Total Images</div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-value" style="color: var(--accent-blue)">{summary.epochs}</div>
          <div class="stat-label">Epochs</div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-value" style="color: var(--accent-purple)">{summary.batch_size}</div>
          <div class="stat-label">Batch Size</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-grid grid-2 animate-in delay-2">
        <div class="glass-card chart-card">
          <h3>Accuracy Curve</h3>
          <div class="chart-wrapper">
            <canvas bind:this={accChartCanvas}></canvas>
          </div>
        </div>
        <div class="glass-card chart-card">
          <h3>Loss Curve</h3>
          <div class="chart-wrapper">
            <canvas bind:this={lossChartCanvas}></canvas>
          </div>
        </div>
      </div>

      <!-- Classification Report -->
      {#if report}
        <div class="glass-card animate-in delay-3">
          <h3>Classification Report</h3>
          <div class="table-wrapper">
            <table class="styled-table">
              <thead>
                <tr>
                  <th>Class</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>F1-Score</th>
                  <th>Support</th>
                </tr>
              </thead>
              <tbody>
                {#if report.with_mask}
                  <tr>
                    <td><span class="badge badge-green">with_mask</span></td>
                    <td>{report.with_mask.precision?.toFixed(4)}</td>
                    <td>{report.with_mask.recall?.toFixed(4)}</td>
                    <td>{report.with_mask['f1-score']?.toFixed(4)}</td>
                    <td>{report.with_mask.support}</td>
                  </tr>
                {/if}
                {#if report.without_mask}
                  <tr>
                    <td><span class="badge badge-red">without_mask</span></td>
                    <td>{report.without_mask.precision?.toFixed(4)}</td>
                    <td>{report.without_mask.recall?.toFixed(4)}</td>
                    <td>{report.without_mask['f1-score']?.toFixed(4)}</td>
                    <td>{report.without_mask.support}</td>
                  </tr>
                {/if}
                {#if report.accuracy !== undefined}
                  <tr class="total-row">
                    <td><strong>Overall Accuracy</strong></td>
                    <td colspan="2"></td>
                    <td><strong>{(typeof report.accuracy === 'number' ? report.accuracy : 0).toFixed(4)}</strong></td>
                    <td><strong>{report['macro avg']?.support || ''}</strong></td>
                  </tr>
                {/if}
              </tbody>
            </table>
          </div>
        </div>
      {/if}

      <!-- Confusion Matrix -->
      {#if matrix}
        <div class="glass-card cm-section animate-in delay-3">
          <h3>Confusion Matrix</h3>
          <div class="confusion-matrix">
            <div class="cm-header"></div>
            <div class="cm-header cm-label">Pred: with_mask</div>
            <div class="cm-header cm-label">Pred: without_mask</div>

            <div class="cm-label">True: with_mask</div>
            <div class="cm-cell cm-tp">{matrix[0][0]}</div>
            <div class="cm-cell cm-fn">{matrix[0][1]}</div>

            <div class="cm-label">True: without_mask</div>
            <div class="cm-cell cm-fp">{matrix[1][0]}</div>
            <div class="cm-cell cm-tn">{matrix[1][1]}</div>
          </div>
        </div>
      {/if}

      <!-- Training config -->
      <div class="glass-card animate-in delay-3">
        <h3>Training Configuration</h3>
        <div class="config-grid">
          <div class="config-item">
            <span class="config-key">Dataset</span>
            <span class="config-val">{summary.num_images} images ({summary.train_samples} train / {summary.test_samples} test)</span>
          </div>
          <div class="config-item">
            <span class="config-key">Learning Rate</span>
            <span class="config-val">{summary.learning_rate}</span>
          </div>
          <div class="config-item">
            <span class="config-key">Optimizer</span>
            <span class="config-val">Adam (decay = lr / epochs)</span>
          </div>
          <div class="config-item">
            <span class="config-key">Seed</span>
            <span class="config-val">{summary.seed}</span>
          </div>
          <div class="config-item">
            <span class="config-key">Final Train Acc</span>
            <span class="config-val">{(summary.final_train_accuracy * 100).toFixed(2)}%</span>
          </div>
          <div class="config-item">
            <span class="config-key">Final Val Acc</span>
            <span class="config-val">{(summary.final_val_accuracy * 100).toFixed(2)}%</span>
          </div>
        </div>
      </div>
    {/if}
  </div>
</section>

<style>
  .page-header {
    text-align: center;
    margin-bottom: var(--space-2xl);
  }
  .page-header h1 { margin-bottom: var(--space-sm); }
  .page-header p {
    max-width: 500px;
    margin: 0 auto;
  }

  .error-banner {
    text-align: center;
    padding: var(--space-md) var(--space-lg);
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: var(--radius-md);
    margin-bottom: var(--space-lg);
    color: var(--accent-red);
  }

  .stats-grid {
    margin-bottom: var(--space-xl);
  }

  .charts-grid {
    margin-bottom: var(--space-xl);
  }

  .chart-card h3 {
    margin-bottom: var(--space-md);
  }

  .chart-wrapper {
    height: 300px;
    position: relative;
  }

  h3 {
    margin-bottom: var(--space-md);
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .total-row td {
    border-top: 2px solid rgba(255, 255, 255, 0.1);
    padding-top: var(--space-md);
  }

  /* Confusion Matrix */
  .cm-section {
    margin-top: var(--space-xl);
  }

  .confusion-matrix {
    display: grid;
    grid-template-columns: auto 1fr 1fr;
    gap: 4px;
    max-width: 400px;
    margin: 0 auto;
  }

  .cm-header {
    padding: var(--space-sm) var(--space-md);
    font-size: 0.75rem;
    font-weight: 600;
    text-align: center;
    color: var(--text-muted);
  }

  .cm-label {
    padding: var(--space-sm) var(--space-md);
    font-size: 0.75rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    color: var(--text-secondary);
  }

  .cm-cell {
    padding: var(--space-lg);
    text-align: center;
    font-weight: 800;
    font-size: 1.5rem;
    border-radius: var(--radius-sm);
    font-variant-numeric: tabular-nums;
  }

  .cm-tp {
    background: rgba(16, 185, 129, 0.15);
    color: var(--accent-green);
  }
  .cm-tn {
    background: rgba(16, 185, 129, 0.15);
    color: var(--accent-green);
  }
  .cm-fp {
    background: rgba(239, 68, 68, 0.1);
    color: var(--accent-red);
  }
  .cm-fn {
    background: rgba(239, 68, 68, 0.1);
    color: var(--accent-red);
  }

  /* Config grid */
  .config-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-sm);
  }

  .config-item {
    display: flex;
    justify-content: space-between;
    padding: var(--space-sm) var(--space-md);
    background: var(--bg-glass-light);
    border-radius: var(--radius-sm);
  }

  .config-key {
    color: var(--text-muted);
    font-size: 0.85rem;
  }
  .config-val {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 0.85rem;
    font-variant-numeric: tabular-nums;
  }

  .glass-card {
    margin-bottom: var(--space-lg);
  }

  .loading-grid {
    margin-bottom: var(--space-xl);
  }

  @media (max-width: 768px) {
    .config-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
