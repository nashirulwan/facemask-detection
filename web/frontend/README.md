# Frontend

Folder ini berisi web app `SvelteKit` untuk antarmuka face mask detection.

## Halaman Utama

- `/`
  landing page
- `/detect`
  upload gambar dan lihat hasil anotasi
- `/webcam`
  webcam snapshot dan realtime webcam
- `/experiments`
  ringkasan hasil training dan evaluasi
- `/about`
  informasi model, paper, dan referensi

## File Penting

- `src/routes/`
  page utama aplikasi
- `src/lib/api.js`
  client request ke backend HTTP dan WebSocket
- `src/app.css`
  styling global
- `Dockerfile`
  build image frontend

## Development

```bash
npm install
npm run dev
```

Frontend dev default:

- `http://localhost:5173`

Backend API default:

- `http://localhost:8000`

## Catatan

- Halaman `detect` memakai profil backend `image`
- Halaman `webcam` memakai profil backend `webcam`
- Realtime webcam menggunakan WebSocket
