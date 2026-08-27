# Module Boundaries & Architecture Specs — Fídíò Studio

This document defines explicit module boundaries, package responsibilities, import rules, and the migration strategy toward microservices.

---

## 1. Package Structure & Namespace Conventions

All backend domain packages reside in `packages/` under the Python namespace `fidio`:

```
packages/
├── domain/            --> fidio.domain
├── generation/        --> fidio.generation
├── providers/         --> fidio.providers
├── storage/           --> fidio.storage
├── media/             --> fidio.media
└── shared/            --> fidio.shared
```

---

## 2. Module Boundaries & Contract Definitions

### 2.1 `fidio.domain` (Domain Model & Core Interfaces)
* **Purpose:** Core enterprise logic, entities, value objects, domain events, repository abstractions, and custom exceptions.
* **Key Components:**
  - Entity Models: `User`, `Project`, `GenerationRequest`, `GenerationPlan`, `Scene`, `GenerationJob`, `JobStep`, `MediaAsset`, `Render`, `ProviderInvocation`.
  - Repository Contracts: `ProjectRepository`, `JobRepository`, `MediaRepository`.
  - Service Interfaces: `LLMProvider`, `ImageProvider`, `VideoProvider`, `AudioProvider`, `ObjectStorage`, `MediaProcessor`.
* **Rules:** MUST NOT depend on database ORMs (SQLAlchemy internals are hidden behind repositories), external APIs, HTTP frameworks, or storage drivers. Zero dependencies outside standard library and Pydantic.

### 2.2 `fidio.providers` (AI Provider Adapters)
* **Purpose:** Concrete implementations of AI provider abstractions.
* **Key Components:**
  - `OpenRouterLLMProvider` (OpenRouter API for LLM planning & scriptwriting).
  - `DevMockLLMProvider`, `DevMockImageProvider`, `DevMockVideoProvider`, `DevMockVoiceProvider` (Deterministic mock adapters for local dev and testing).
* **Rules:** All external HTTP calls must include timeouts, retries (with exponential backoff), circuit breakers, and rate-limit error normalization. Must not import from `fidio.generation` or API routes.

### 2.3 `fidio.storage` (Object Storage Abstraction)
* **Purpose:** Encapsulates S3/MinIO operations.
* **Key Components:**
  - `MinIOObjectStorageAdapter` (MinIO/S3 operations: upload, download, delete, presigned URL generation, bucket init).
* **Rules:** Raw filesystem paths must never be exposed outside this module. Clients consume presigned S3 URLs.

### 2.4 `fidio.media` (FFmpeg Media Processing)
* **Purpose:** Encapsulates FFmpeg command-line execution and media probing tools.
* **Key Components:**
  - `FFmpegMediaProcessor` (probe, transcode, scale, concatenate, mux audio/video).
* **Rules:** Isolated subprocess calls to `ffmpeg`/`ffprobe`. Must validate input file parameters (dimensions, codecs, frame rates) before processing.

### 2.5 `fidio.generation` (Orchestration & State Machine)
* **Purpose:** Manages the end-to-end execution of generation jobs across pipeline stages.
* **Key Components:**
  - `GenerationOrchestrator`, `StageHandler`, `PlanningStage`, `AssetGenerationStage`, `RenderingStage`, `RetryPolicy`.
* **Rules:** Enforces state transitions (`QUEUED` -> `PLANNING` -> `GENERATING_ASSETS` -> `RENDERING` -> `COMPLETED` / `FAILED`). Idempotency checks must prevent re-running completed steps.

### 2.6 `apps/api` (Stateless REST API)
* **Purpose:** HTTP interface for web application and developer clients.
* **Key Components:**
  - FastAPI routers (`/projects`, `/generation-requests`, `/jobs`, `/media-assets`, `/renders`).
  - Request validation schemas & API error handlers.
* **Rules:** API controllers MUST NOT execute long-running AI or FFmpeg operations. Controllers invoke `fidio.generation` or enqueue background jobs to Redis.

### 2.7 `services/worker` (Asynchronous Worker Service)
* **Purpose:** Background worker consuming Redis job queues and running heavy execution pipelines.
* **Key Components:**
  - Task consumers, concurrency worker settings, signal handlers for graceful shutdown.

---

## 3. Strict Import Guidelines

| Module | Can Import From | MUST NOT Import From |
|---|---|---|
| `fidio.domain` | None (Standard lib + Pydantic) | `providers`, `storage`, `media`, `generation`, `api`, `worker` |
| `fidio.providers` | `fidio.domain`, `fidio.shared` | `generation`, `api`, `worker`, `storage` |
| `fidio.storage` | `fidio.domain`, `fidio.shared` | `generation`, `api`, `worker`, `providers` |
| `fidio.media` | `fidio.domain`, `fidio.shared` | `generation`, `api`, `worker`, `providers` |
| `fidio.generation` | `fidio.domain`, `fidio.providers`, `fidio.storage`, `fidio.media`, `fidio.shared` | `api`, `worker` |
| `apps/api` | `fidio.domain`, `fidio.generation`, `fidio.storage`, `fidio.shared` | `services/worker` |
| `services/worker` | `fidio.domain`, `fidio.generation`, `fidio.providers`, `fidio.storage`, `fidio.media`, `fidio.shared` | `apps/api` |

---

## 4. Microservice Migration Path

While Fídíò Studio starts as a modular monolith in a single repository, modules are designed for easy microservice decomposition:

```
+-------------------------------------------------------------------------+
|                              Fídíò Platform                             |
+-------------------┬───────────────────┬───────────────────┬─────────────+
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
            │ Fídíò Engine  │   │  Fídíò Storage│   │  Fídíò Render │
            │  (AI Planner) │   │  (Media S3)   │   │  (FFmpeg Core)│
            └───────────────┘   └───────────────┘   └───────────────┘
```

1. **Extraction Step 1: Render Microservice:** `fidio.media` and FFmpeg rendering routines can be isolated into dedicated worker pools optimized for GPU/CPU heavy tasks.
2. **Extraction Step 2: AI Orchestration Microservice:** `fidio.providers` and `fidio.generation` can be converted into `Fídíò Engine`, an autonomous service listening on message bus topics (gRPC / RabbitMQ).
3. **Extraction Step 3: API Gateway & Auth:** `apps/api` transforms into a lean API gateway routing traffic to `Fídíò Engine`, `Fídíò Storage`, and user services.
