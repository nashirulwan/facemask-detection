/**
 * Backend API client for the Facemask Detector.
 *
 * All functions communicate with the FastAPI backend.
 */

const API_BASE = import.meta.env.VITE_API_BASE || '';

/**
 * Upload an image for mask detection.
 * @param {File} file - Image file to analyze
 * @returns {Promise<object>} Prediction response with detections and annotated image
 */
export async function predictImage(file) {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${API_BASE}/api/predict/image`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) {
    throw new Error(`Prediction failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/**
 * Get training run summary.
 * @returns {Promise<object>}
 */
export async function getExperimentSummary() {
  const res = await fetch(`${API_BASE}/api/experiments/summary`);
  return res.json();
}

/**
 * Get classification report.
 * @returns {Promise<object>}
 */
export async function getClassificationReport() {
  const res = await fetch(`${API_BASE}/api/experiments/classification-report`);
  return res.json();
}

/**
 * Get confusion matrix.
 * @returns {Promise<number[][]>}
 */
export async function getConfusionMatrix() {
  const res = await fetch(`${API_BASE}/api/experiments/confusion-matrix`);
  return res.json();
}

/**
 * Get per-epoch training history.
 * @returns {Promise<object>}
 */
export async function getTrainingHistory() {
  const res = await fetch(`${API_BASE}/api/experiments/history`);
  return res.json();
}

/**
 * Get model info.
 * @returns {Promise<object>}
 */
export async function getModelInfo() {
  const res = await fetch(`${API_BASE}/api/model-info`);
  return res.json();
}

/**
 * Get experiment curve image URL.
 * @param {'accuracy_curve' | 'loss_curve'} name
 * @returns {string}
 */
export function getCurveUrl(name) {
  return `${API_BASE}/api/experiments/curves/${name}`;
}

/**
 * Create a WebSocket connection for real-time webcam streaming.
 * @returns {WebSocket}
 */
export function createPredictionSocket() {
  return new WebSocket(`${API_BASE.replace('http', 'ws')}/api/predict/stream`);
}
