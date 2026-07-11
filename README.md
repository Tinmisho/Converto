# Converto

Self-hosted document and image converter. No file size limits (you control them), no ads, no cloud — runs entirely on your machine.

## Features

- Convert documents: PDF, DOCX, ODT, RTF, EPUB, HTML, Markdown, TXT
- Convert images: PNG, JPG, WEBP, AVIF, HEIC, TIFF, GIF, BMP
- Resize images (width × height or scale %)
- Full screen web UI — dark navy theme
- Job queue with real-time progress
- Auto-download option
- Docker Compose — one command to run

## Quick start

```bash
git clone https://github.com/yourname/converto.git
cd converto
cp .env.example .env
docker compose up -d
```

Open [http://localhost:8000](http://localhost:8000).

## Configuration

Edit `.env`:

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | Host port |
| `MAX_FILE_MB` | `100` | Max upload size in MB |
| `SECRET_KEY` | `changeme` | App secret — change this |

## Development (hot reload)

```bash
cp .env.example .env
docker compose up
```

The `docker-compose.override.yml` is applied automatically — it mounts source files so changes to `backend/` reload instantly.

## Architecture

```
browser → web (FastAPI :8000) → redis → worker (Celery)
                                              ↓
                                   LibreOffice / Pandoc / libvips
```

Uploaded files live in a shared Docker volume and are cleaned up after conversion.

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12, FastAPI, Celery |
| Queue | Redis 7 |
| Documents | LibreOffice, Pandoc |
| Images | libvips (pyvips) + libheif |
| Frontend | Vanilla JS + Vue 3 (no build step) |
