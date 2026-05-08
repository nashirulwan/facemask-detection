# Backend

Folder ini berisi service inference `FastAPI` untuk face mask detection.

## Isi Utama

- `app/main.py`
  entry point aplikasi backend
- `app/api/routes/`
  route HTTP dan WebSocket untuk prediksi serta data eksperimen
- `app/services/detector.py`
  pipeline inti:
  - deteksi wajah dengan OpenCV DNN SSD
  - klasifikasi `Mask` / `No Mask` dengan CNN
- `app/core/`
  konfigurasi dan model loader
- `app/schemas/`
  schema response API
- `models/`
  model `.h5`, face detector, dan hasil eksperimen
- `Dockerfile`
  build image backend
- `requirements.txt`
  dependency Python backend

## Endpoint Penting

- `POST /api/predict/image`
  prediksi dari upload gambar
- `WS /api/predict/stream`
  realtime webcam via WebSocket
- `GET /api/health`
  health check backend
- `GET /api/experiments/*`
  data ringkasan training dan evaluasi

## Catatan

- Mode `image` dan `webcam` memakai profil deteksi yang berbeda.
- `image` lebih sensitif untuk group photo atau wajah kecil.
- `webcam` lebih ketat untuk mengurangi false positive saat selfie atau realtime.
