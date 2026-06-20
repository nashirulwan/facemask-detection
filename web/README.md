### Web app

The SvelteKit frontend and the FastAPI backend that runs the mask detection model. You upload an image or turn on your webcam, and it draws boxes on each face with mask or no mask.

#### Features

- Upload an image and get the detection right away
- Real time webcam detection over a WebSocket
- Experiment pages: accuracy/loss curves, classification report, confusion matrix
- An about page covering the paper and the model

#### Stack

| Part | Tech |
|------|------|
| Frontend | SvelteKit |
| Backend | FastAPI + TensorFlow + OpenCV |
| Deploy | Docker Compose + Nginx |
| Face detector | OpenCV DNN SSD (res10_300x300) |
| Classifier | custom CNN, bundled in `backend/models` |

#### Run

```bash
cd deploy
docker compose up --build
```

The backend serves the inference API, the frontend talks to it. Compose file and nginx config are in `deploy/`.

#### Structure

```
frontend/   SvelteKit app
backend/    FastAPI inference service + the bundled model
deploy/     Docker Compose and nginx config
assets/     demo images
```

The model and how it was trained live in `../training`.
