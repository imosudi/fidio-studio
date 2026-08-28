# Fídíò Studio — AI-Powered Creative Production

**Brand:** Fídíò  
**Product:** Fídíò Studio  
**Tagline:** Imagine. Create. Fídíò.  
**Repository:** `fidio-studio`  
**Namespace:** `fidio`  
**Docker Prefix:** `fidio-*`  
**Staging Host:** [https://fidio.site](https://fidio.site)  

---

## Overview

Fídíò Studio is a production-oriented, modular AI video generation platform. Built on a modular monolith architecture, Fídíò Studio transforms creative text prompts into structured multi-scene video plans, coordinates multi-modal AI model providers via OpenRouter, manages intermediate media assets in S3-compatible MinIO object storage, tracks asynchronous generation jobs in PostgreSQL, and orchestrates automated FFmpeg composition into final video renders.

---

## Architecture & Module Boundaries

```
                                  FÍDÍÒ
                                    │
    ┌───────────────┬───────────────┼───────────────┬───────────────┐
    ↓               ↓               ↓               ↓               ↓
  Studio          Engine           API            Cloud         Enterprise
(Creator UI)    (AI & Render)  (Dev Integration) (Hosted Platform) (Self-Hosted)
```

```
apps/api ────────────┐
                     ↓
services/worker ───> packages/generation ───> packages/domain <─── packages/storage
                     │                      │                  │
                     ├──> packages/providers─┘                  └──> packages/media
                     │
                     └──> packages/shared
```

---

## Technology Stack

- **Backend REST API:** Python 3.11+, FastAPI, Pydantic v2, uvicorn (`apps/api`)
- **Async Pipeline Worker:** Python 3.11+, PostgreSQL job queue polling loop (`services/worker`)
- **Domain & Engine:** Modular Python packages (`packages/domain`, `packages/generation`, `packages/providers`, `packages/storage`, `packages/media`)
- **Relational Database:** PostgreSQL 15+ (Alembic migrations, SQLAlchemy 2.0 async engine)
- **Object Storage:** S3-compatible MinIO (Presigned URLs for secure asset delivery)
- **Media Processing:** FFmpeg 6.0+ CLI wrapper for probing, scaling, concatenation, and audio muxing
- **Web Frontend Application:** Modern Single Page Web App featuring obsidian dark mode, glassmorphism UI, real-time job progress polling, scene inspector, and HTML5 player (`public/index.html`)

---

## Prerequisites

- **Python:** 3.11 or higher
- **PostgreSQL:** 15.0+ (running locally or remote host)
- **MinIO / AWS S3:** Running S3-compatible service
- **FFmpeg:** Installed on PATH (`ffmpeg` and `ffprobe`)
- **Git & Docker:** Git 2.30+, Docker Compose (v2+)

---

## Developer Quickstart Guide

### 1. Clone & Setup Environment
```bash
git clone https://github.com/imosudi/fidio-studio.git
cd fidio-studio
cp .env.example .env
```

### 2. Setup Local Python Virtual Environment & Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install -r requirements.txt  # If applicable
```

### 3. Run Database Migrations
```bash
PYTHONPATH=. alembic upgrade head
```

### 4. Execute Full Automated Test Suite
```bash
PYTHONPATH=. .venv/bin/pytest -v
```

### 5. Launch REST API Server
```bash
PYTHONPATH=. uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Launch Async Pipeline Worker
```bash
PYTHONPATH=. python services/worker/main.py
```

### 7. Run System Integration Smoke Test
```bash
python scripts/smoke_test.py http://localhost:8000/api/v1
```

---

## Docker Compose Quickstart

To spin up the local development stack via Docker Compose:

```bash
docker compose up -d --build
```

### Services & Ports
- **Web Application:** `http://localhost:3000`
- **REST API Documentation (Swagger):** `http://localhost:8000/docs`
- **Prometheus Metrics:** `http://localhost:8000/metrics`
- **MinIO Storage Console:** `http://localhost:9001` (User: `minioadmin` / Pass: `minioadmin`)

---

## Environment Variable Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | Runtime environment (`development`, `staging`, `production`) |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `MINIO_ENDPOINT` | `minio:9000` | S3 / MinIO server endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | S3 Access Key ID |
| `MINIO_SECRET_KEY` | `minioadmin` | S3 Secret Access Key |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | OpenRouter API Key for LLM planning |
| `LLM_PROVIDER` | `mock` | LLM Provider mode (`mock` or `openrouter`) |
| `MEDIA_PROVIDER` | `mock` | Media Provider mode (`mock` or `live`) |

---

## Key Development & Operational Commands

```bash
# Run unit, failure, performance, security, and telemetry tests
PYTHONPATH=. .venv/bin/pytest -v tests/unit tests/failure tests/performance tests/security

# Run end-to-end integration test suite
PYTHONPATH=. .venv/bin/pytest -v tests/e2e/test_end_to_end_flow.py

# Format and check code quality
flake8 packages/ apps/ services/

# Execute database migration head
PYTHONPATH=. alembic upgrade head

# Rollback latest database migration
PYTHONPATH=. alembic downgrade -1
```

---

## Microservices Extraction Roadmap

The modular monolith is designed with strict boundaries to enable extraction into independent microservices:
1. `services/worker` → Independent Celery/RQ job execution cluster
2. `packages/media` → FFmpeg rendering microservice on GPU instances
3. `packages/providers` → Dedicated AI Provider Gateway

---

## License

See [LICENSE](LICENSE) for license details.
