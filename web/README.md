# Facemask Detection

Aplikasi web deteksi masker wajah berbasis CNN yang dibangun sebagai implementasi dan reproduksi paper:

> **"A real time face mask detection system using convolutional neural network"**
> Goyal et al., 2022 — DOI: `10.1007/s11042-022-12166-x`

**Live demo:** [https://mask.nashiru.me](https://mask.nashiru.me)

## Deskripsi

Sistem ini mendeteksi masker wajah pada gambar statis maupun video real-time menggunakan dua tahap:

1. **Face detection** — OpenCV DNN dengan model SSD ResNet-10 untuk mendeteksi lokasi wajah
2. **Mask classification** — CNN kustom 5 layer yang dilatih dari dataset 4000 gambar (2000 `with_mask`, 2000 `without_mask`)

Model CNN mencapai **98.50% test accuracy** dengan precision dan recall 0.98 pada kedua kelas, mendekati hasil paper (~98%).

## Fitur

- Upload gambar dan deteksi masker secara langsung
- Webcam real-time via WebSocket
- Halaman eksperimen: kurva akurasi/loss, classification report, confusion matrix
- Halaman tentang paper dan arsitektur model

## Teknologi

| Komponen | Teknologi |
|---|---|
| Frontend | SvelteKit |
| Backend | FastAPI + TensorFlow + OpenCV |
| Deployment | Docker Compose + Nginx |
| Model | CNN kustom (5× Conv2D + MaxPool + Dense) |
| Face Detector | OpenCV DNN SSD (res10_300x300) |

## Struktur Project

```
facemask-project/
├── frontend/       SvelteKit web app
├── backend/        FastAPI inference service + model
├── deploy/         Docker Compose dan Nginx config
└── assets/         Demo images
```

## Hasil Eksperimen

| Metrik | Nilai |
|---|---|
| Test Accuracy | 98.50% |
| Precision (with_mask) | 0.98 |
| Recall (with_mask) | 0.98 |
| Precision (without_mask) | 0.98 |
| Recall (without_mask) | 0.98 |
| Dataset | 4000 gambar (80/20 split) |
| Epochs | 100 |
| Optimizer | Adam (lr=0.0005) |

## Referensi

- Paper: Goyal et al. (2022), DOI `10.1007/s11042-022-12166-x`
- Upstream repo: [techyhoney/Facemask_Detection](https://github.com/techyhoney/Facemask_Detection)
