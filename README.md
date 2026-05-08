# Facemask Detection

Face mask detection web app built from a CNN-based reproduction workflow and served as a full-stack demo with `SvelteKit`, `FastAPI`, `Docker`, `Tailscale`, and `Cloudflare Tunnel`.

Live demo: `https://mask.nashiru.me`

## Overview

This repository contains:

- a `FastAPI` backend for face detection and mask classification
- a `SvelteKit` frontend for image upload, webcam snapshot, realtime webcam, and experiment visualization
- Docker-based deployment files
- trained model artifacts and experiment outputs

The implementation is adapted from a paper reproduction workflow and an upstream open-source implementation documented in [references/UPSTREAM.md](references/UPSTREAM.md).

## Stack

- Frontend: `SvelteKit`
- Backend: `FastAPI`
- Model runtime: `TensorFlow` and `OpenCV`
- Deployment: `Docker Compose`, `Nginx`
- Networking: `Tailscale`, `Cloudflare Tunnel`

## Project Structure

- `frontend/` SvelteKit web application
- `backend/` FastAPI inference service and model assets
- `deploy/` Docker Compose and Nginx config
- `assets/` demo images and UI assets
- `references/` upstream attribution and paper references
- `dataset/` dataset placeholder only, not the full raw dataset

## Run Locally

### Docker

```bash
cd deploy
docker compose up -d --build
```

Then open:

- `http://localhost/`
- `http://localhost/api/health`

### Development Mode

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Then open:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`

## Features

- image-based face mask detection
- webcam snapshot detection
- realtime webcam detection via WebSocket
- separate detection tuning for `image` and `webcam` use cases
- experiment results page with training metrics
- Dockerized deployment for local or server hosting

## Deployment Notes

Production deployment currently uses:

- app container in a Proxmox LXC
- `Tailscale` for stable private routing
- `cloudflared` on an infra node for public domain exposure

Public endpoint:

- `https://mask.nashiru.me`

## Attribution

- Paper reproduction target: `10.1007/s11042-022-12166-x`
- Upstream repository: `techyhoney/Facemask_Detection`

More detail is available in [references/UPSTREAM.md](references/UPSTREAM.md).
