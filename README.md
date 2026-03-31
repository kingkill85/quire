# Quire

Book search & download sidecar for [Verso](https://github.com/kingkill85/verso). Searches multiple sources, downloads books, and pushes them directly to your Verso library.

## Features

- Search Anna's Archive, LibGen, Z-Library, Open Library, Project Gutenberg, Standard Ebooks
- Plugin-based source system — easy to add new sources
- Download queue with real-time progress
- Cloudflare bypass (built-in or external via FlareSolverr)
- Auth delegated to Verso — no separate user management
- Two Docker image variants: standard and lite

## Quick Start

```yaml
# Add to your Verso docker-compose.yml
services:
  quire:
    image: ghcr.io/kingkill85/quire:latest
    ports:
      - "8085:8085"
    environment:
      QUIRE_VERSO_URL: http://verso:3000
      QUIRE_VERSO_APP_PASSWORD_EMAIL: admin@example.com
      QUIRE_VERSO_APP_PASSWORD: your-app-password
```

## Development

```bash
# Backend
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn quire.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
