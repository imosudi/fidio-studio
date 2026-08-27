# Architecture Overview — Fídíò Studio

**Brand:** Fídíò  
**Product:** Fídíò Studio  
**Product Descriptor:** AI-powered creative production  
**Core Stack:** Python (FastAPI, Celery/RQ, SQLAlchemy), PostgreSQL, MinIO, Redis, Docker Compose, FFmpeg, Modern Web UI (Next.js/React)  

---

## 1. Executive Summary

Fídíò Studio is a modular, AI-powered video generation platform. Users provide creative text or media prompts, which the Fídíò Engine transforms into structured generation plans (scenes, audio, visual prompts, voice balance), invokes configurable multi-modal AI generation providers (LLMs via OpenRouter, video/image models, audio models), persists intermediate and final media assets into MinIO object storage, tracks long-running generation jobs, and orchestrates final FFmpeg video composition.

---

## 2. High-Level System Architecture

```
                  ┌─────────────────────────────────────────┐
                  │          Fídíò Studio Web UI            │
                  │              (apps/web)                 │
                  └────────────────────┬────────────────────┘
                                       │ HTTPS / REST API
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │            Fídíò REST API               │
                  │              (apps/api)                 │
                  └───────┬─────────────────────────┬───────┘
                          │                         │
            Persist Jobs  │                         │ Enqueue Tasks
            & Metadata    │                         │
                          ▼                         ▼
            ┌──────────────────┐          ┌──────────────────┐
            │  External DB     │          │  Redis Queue     │
            │  (PostgreSQL)    │          │  (Broker/Result) │
            └──────────────────┘          └────────┬─────────┘
                                                   │
                                                   │ Consume Tasks
                                                   ▼
                                          ┌──────────────────┐
                                          │ Async Worker     │
                                          │ (services/worker)│
                                          └────────┬─────────┘
                                                   │
                 ┌─────────────────────────────────┼─────────────────────────────────┐
                 │                                 │                                 │
                 ▼                                 ▼                                 ▼
    ┌─────────────────────────┐       ┌─────────────────────────┐       ┌─────────────────────────┐
    │  AI Provider Adapter    │       │ MinIO Object Storage    │       │  FFmpeg Engine          │
    │  (packages/providers)   │       │ (packages/storage)      │       │  (packages/media)       │
    │  - OpenRouter (LLM)     │       │ - Presigned URLs        │       │ - Probing & Concatenation│
    │  - Dev Mocks & External │       │ - Raw/Asset/Render Buckets│     │ - Muxing & Encoding     │
    └─────────────────────────┘       └─────────────────────────┘       └─────────────────────────┘
```

---

## 3. Core Component Responsibilities

| Component | Directory | Responsibility | Primary Tech |
|---|---|---|---|
| **Web Frontend** | `apps/web` | Provides interactive creator dashboard for project management, prompt creation, progress polling, asset inspection, and video downloading. | Next.js / React, Tailwind CSS |
| **REST API** | `apps/api` | Stateless HTTP service handling user authentication, project CRUD, generation requests, job state retrieval, and presigned asset URL issuance. | FastAPI, Pydantic, uvicorn |
| **Async Worker** | `services/worker` | Background execution service running generation jobs (LLM script planning, image/video generation, audio processing, FFmpeg composition). | Celery / RQ, Redis |
| **Domain Core** | `packages/domain` | Enterprise business entities, domain models, state machines, repository interfaces, and value objects. | Python 3.11+, Pydantic v2 |
| **Generation Engine** | `packages/generation` | Pipeline stage handlers, job dispatcher, stage execution orchestrator, retry logic, and stage state persistence. | Python 3.11+ |
| **AI Providers** | `packages/providers` | Infrastructure adapters implementing provider interfaces (OpenRouter LLM provider, Dev Mock providers). | `httpx`, Pydantic |
| **Storage Abstraction** | `packages/storage` | S3-compatible MinIO adapter handling bucket initialization, file streaming, MIME validation, and presigned URL generation. | `boto3` / `aioboto3` / MinIO SDK |
| **Media Engine** | `packages/media` | FFmpeg execution abstraction for probing video/audio properties, scaling aspect ratios, concatenation, and audio-video muxing. | FFmpeg CLI wrapper |
| **Shared Core** | `packages/shared` | Cross-cutting concerns: structured JSON logging, metrics, tracing hooks, and environment configuration parser. | `structlog`, `pydantic-settings` |

---

## 4. End-to-End Execution Flow

1. **Project & Request Creation:**
   - User creates a Project via the REST API or Web UI.
   - User submits a text/video generation request (`prompt`, `style`, `target_duration`, `aspect_ratio`).
2. **Job Scheduling:**
   - API creates a `GenerationJob` record in PostgreSQL with state `QUEUED` and enqueues a background job in Redis.
   - API immediately returns HTTP 202 (Accepted) with the `job_id`.
3. **AI Planning Stage (`services/worker`):**
   - Worker picks up the job, transitions status to `PLANNING`.
   - Calls `GenerationPlanner` adapter via OpenRouter LLM to decompose prompt into structured `GenerationPlan` JSON containing N scenes, narrative voiceover script, visual prompts, and shot timing.
   - Stores structured `GenerationPlan` and `Scene` entities in PostgreSQL.
4. **Media Generation Stage:**
   - Worker transitions status to `GENERATING_ASSETS`.
   - Invokes configured `ImageProvider` / `VideoProvider` / `VoiceProvider` adapters per scene.
   - Saves intermediate image, video, and audio binaries directly into MinIO storage.
   - Saves `MediaAsset` records with S3 key references and metadata in PostgreSQL.
5. **Video Composition & Rendering Stage:**
   - Worker transitions status to `RENDERING`.
   - Downloads scene assets to isolated temp volume.
   - Invokes `packages/media` FFmpeg suite to stitch visual clips, overlay audio/narration tracks, conform aspect ratios, and export `final_render.mp4`.
   - Uploads final render file to MinIO bucket `fidio-renders`.
6. **Completion & Delivery:**
   - Worker transitions job status to `COMPLETED` and updates output `Render` record with S3 key and metadata.
   - Web UI polling/websocket receives status update and fetches presigned MinIO URL for instant streaming and downloading.

---

## 5. Deployment Architecture & Infrastructure

- **Containerized Services:** `apps/api`, `apps/web`, `services/worker`, `minio`, `redis` run as Docker containers orchestrated via `docker-compose.yml`.
- **External Database:** PostgreSQL runs externally (on host machine or managed DB instance) to ensure persistence across container lifecycles.
- **FFmpeg Integration:** The worker container includes pre-installed FFmpeg binaries (`ffmpeg`, `ffprobe`) enabling scalable local media assembly without external video processing SaaS.
