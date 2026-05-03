# Facemask Project

Kelompok project untuk reproduksi paper face mask detection, eksperimen lokal, dan deployment demo web.

## Struktur

- `frontend/`:
  Frontend app. Rencana: SvelteKit.
- `backend/`:
  Backend inference. Rencana: FastAPI.
- `deploy/`:
  File deploy seperti `docker-compose.yml`, `Dockerfile`, dan config reverse proxy.
- `reports/`:
  Laporan tugas, ringkasan hasil, dan catatan eksperimen.
- `sample_results/`:
  Contoh output prediksi, grafik akurasi/loss, dan aset presentasi.
- `assets/`:
  Aset UI, gambar, ikon, dan branding kelompok.
- `references/`:
  Sitasi paper, kredit repo upstream, dan referensi teknis.
- `dataset/`:
  Placeholder untuk petunjuk dataset. Tidak untuk commit seluruh dataset mentah.
- `notebooks/`:
  Notebook analisis atau eksplorasi tambahan.
- `docs/`:
  Dokumentasi setup, arsitektur, dan panduan anggota tim.

## Catatan

- Repo ini dipisahkan dari repo upstream agar hasil kelompok lebih rapi.
- Model training dan pipeline reproduksi awal saat ini masih ada di repo `../Facemask_Detection`.
- Langkah berikutnya: scaffold `backend` dan `frontend`, lalu hubungkan ke model hasil training sendiri.
