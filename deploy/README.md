# Deploy

Folder ini berisi file deployment yang dipakai untuk menjalankan aplikasi secara lokal maupun di server.

## Isi Utama

- `docker-compose.yml`
  menjalankan service:
  - `backend`
  - `frontend`
  - `nginx`
- `nginx.conf`
  reverse proxy:
  - route `/api` ke backend
  - route web ke frontend

## Cara Menjalankan

Dari folder project root:

```bash
cd deploy
docker compose up -d --build
```

Lalu buka:

- `http://localhost`
- `http://localhost/api/health`

## Catatan Deploy Server

Saat ini deployment produksi project ini menggunakan:

- Proxmox LXC
- Docker Compose
- Tailscale
- Cloudflare Tunnel

Domain publik saat ini:

- `https://mask.nashiru.me`
