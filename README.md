# Fídíò Studio — AI-Powered Creative Production

**Brand:** Fídíò  
**Product:** Fídíò Studio  
**Tagline:** Imagine. Create. Fídíò.  
**Repository:** `fidio-studio`  
**Namespace:** `fidio`  
**Docker Prefix:** `fidio-*`  

---

## Overview

Fídíò Studio is a production-oriented, modular AI video generation platform. Built on a modular monolith architecture, Fídíò Studio transforms creative text and video generation prompts into structured multi-scene video plans, coordinates multi-modal AI model providers via OpenRouter, manages intermediate media assets in S3-compatible MinIO object storage, tracks asynchronous generation jobs in PostgreSQL, and orchestrates automated FFmpeg composition into final video renders.

---

## Brand Architecture

```
                                  FÍDÍÒ
                                    │
    ┌───────────────┬───────────────┼───────────────┬───────────────┐
    ↓               ↓               ↓               ↓               ↓
  Studio          Engine           API            Cloud         Enterprise
(Creator UI)    (AI & Render)  (Dev Integration) (Hosted Platform) (Self-Hosted)
```

---

## Technical Stack & Architecture

- **Backend REST API:** Python 3.11+, FastAPI, Pydantic v2, uvicorn (`apps/api`)
- **Async Queue & Worker:** Celery / RQ, Redis (`services/worker`)
- **Domain & Engine:** Modular Python packages (`packages/domain`, `packages/generation`, `packages/providers`, `packages/storage`, `packages/media`)
- **Relational Database:** External PostgreSQL (Alembic migrations, SQLAlchemy 2.0 async engine)
- **Object Storage:** S3-compatible MinIO (presigned URLs for asset security)
- **Media Engine:** FFmpeg CLI wrapper for probing, scaling, concating, and muxing
- **Web Frontend:** Next.js / React, Tailwind CSS modern dark mode UI (`apps/web`)
- **Containerization:** Docker Compose for local development stack (`fidio-api`, `fidio-web`, `fidio-worker`, `fidio-minio`, `fidio-redis`)

---

## Directory Layout

```
fidio-studio/
├── AGENTS.md                      # Principal architect blueprint and agent rules
├── README.md                      # Project introduction & quickstart guide
├── LICENSE                        # Project license
├── SECURITY.md                    # Security policy & credential guidance
├── CONTRIBUTING.md                # Contribution & architecture guidelines
├── .env.example                   # Environment variable template
├── Makefile                       # Developer command interface
├── docker-compose.yml             # Local development environment container orchestration
│
├── apps/                          # Deployable Application Interfaces
│   ├── api/                       # REST API service (FastAPI)
│   └── web/                       # Modern frontend web application (Next.js / React)
│
├── services/                      # Background Execution Services
│   └── worker/                    # Asynchronous generation pipeline worker (Celery/RQ)
│
├── packages/                      # Shared Python Domain Packages (`fidio.*`)
│   ├── domain/                    # Core domain entities, interfaces, value objects, exceptions
│   ├── generation/                # Pipeline orchestrator, state machine, job executor
│   ├── providers/                 # AI provider adapters (OpenRouter, dev mocks, future APIs)
│   ├── storage/                   # Object storage abstraction & MinIO adapter
│   ├── media/                     # FFmpeg wrapper & media asset processing utils
│   └── shared/                    # Logging, telemetry, configuration, common utilities
│
├── infrastructure/                # Container & Deployment Infrastructure
│   ├── docker/                    # Dockerfiles for API, Worker, Web
│   ├── minio/                     # MinIO initialization scripts & policy configs
│   └── scripts/                   # Database seeding, entrypoints, healthchecks
│
├── migrations/                    # Database Schema Migrations (Alembic)
├── tests/                         # Automated Suite (Unit, Integration, Contract, End-to-End)
└── docs/                          # Comprehensive Architectural Documentation
    ├── architecture/              # Detailed module specs, diagrams, schemas
    └── branding/                  # Brand assets, guidelines, design tokens
```

---

## Quickstart Guide

1. **Clone & Configure:**
   ```bash
   cp .env.example .env
   ```
2. **Launch Development Stack (Docker Compose):**
   ```bash
   make dev
   # Or: docker compose up -d --build
   ```
3. **Run Database Migrations:**
   ```bash
   make migrate
   ```
4. **Access Web Application & API Specs:**
   - Web Dashboard: `http://localhost:3000`
   - REST API Docs (Swagger): `http://localhost:8000/docs`
   - MinIO Storage Console: `http://localhost:9001` (Credentials: `minioadmin` / `minioadmin`)

---

## Comprehensive Architecture Documentation

- [`AGENTS.md`](AGENTS.md): Architectural contract, dependency rules, and agent task assignments.
- [`docs/architecture/overview.md`](docs/architecture/overview.md): System architecture, execution flow, component responsibilities.
- [`docs/architecture/module_boundaries.md`](docs/architecture/module_boundaries.md): Package boundaries, import restrictions, microservice roadmap.
- [`docs/architecture/api_conventions.md`](docs/architecture/api_conventions.md): REST API endpoints, schemas, error envelopes, status codes.
- [`docs/architecture/database_conventions.md`](docs/architecture/database_conventions.md): PostgreSQL schema specification, entities, Alembic rules.
- [`docs/architecture/development_commands.md`](docs/architecture/development_commands.md): Makefile reference, Docker targets, local setup.
- [`docs/architecture/testing_strategy.md`](docs/architecture/testing_strategy.md): Test layers, mock providers, quality gates.

---

## License

See [LICENSE](License.md) for details.
