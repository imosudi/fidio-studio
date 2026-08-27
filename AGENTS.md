# AGENTS.md — Architectural Contract & Agent Execution Blueprint
**Brand:** Fídíò  
**Product:** Fídíò Studio  
**Tagline:** Imagine. Create. Fídíò.  
**Repository:** `fidio-studio`  
**Namespace:** `fidio`  
**Docker Prefix:** `fidio-*`  

---

## 1. System Vision & Brand Architecture

Fídíò is an intelligent creative technology platform designed to transform user ideas into production-ready video content through structured AI understanding, multi-modal generation, and precise audio-visual composition.

```
                                  FÍDÍÒ
                                    │
    ┌───────────────┬───────────────┼───────────────┬───────────────┐
    ↓               ↓               ↓               ↓               ↓
  Studio          Engine           API            Cloud         Enterprise
(Creator UI)    (AI & Render)  (Dev Integration) (Hosted Platform) (Self-Hosted)
```

### End-to-End Creative Pipeline Flow

```
                 FÍDÍÒ STUDIO
                      │
                    Idea
                      ↓
               AI Understanding
                      ↓
                Creative Plan
                      ↓
              ┌───────┼───────┐
              ↓       ↓       ↓
            Visual   Audio   Voice
              │       │       │
              └───────┼───────┘
                      ↓
                 Composition
                      ↓
                 Final Video
```

---

## 2. Core Architectural Principles

1. **Modular Monolith First:** The MVP is built as a single codebase with strict package boundaries (`packages/`, `apps/`, `services/`). Selected modules (e.g., render engine, AI providers, job queue) are designed to be easily extracted into independent microservices in future iterations.
2. **Stateless API Services:** The REST API (`apps/api`) does not store session state or block on long-running generation jobs. State is persisted in PostgreSQL.
3. **Asynchronous Execution:** Generation tasks, script planning, asset fetching, and video rendering are handled asynchronously via worker processes (`services/worker`) consuming jobs from a Redis-backed queue.
4. **External PostgreSQL:** PostgreSQL runs externally to the Docker Compose stack (production/remote DB), maintaining strict relational schema for state management, metadata, and execution history. Binary assets are NEVER stored in PostgreSQL.
5. **S3-Compatible Storage (MinIO):** All generated, intermediate, and uploaded media files reside in MinIO (or AWS S3). Access to files is strictly provided through signed/presigned URLs.
6. **Abstracted AI Providers:** Domain logic MUST NOT depend on specific AI providers. Providers (OpenRouter, ElevenLabs, Runway, etc.) are implemented behind abstract Python interfaces (`LLMProvider`, `ImageProvider`, `AudioProvider`, `VideoProvider`).
7. **Environment-Driven Configuration:** All settings and secrets are read from environment variables (`.env`). Secrets are never committed to source control.
8. **FFmpeg Utility Layer:** FFmpeg media manipulation (stitching, muxing, scaling, color/audio processing) is encapsulated in a dedicated package (`packages/media`) and executed within worker containers equipped with FFmpeg binary tooling.

---

## 3. Repository Directory Structure & Module Boundaries

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

## 4. Module Dependency Rules

To maintain high code quality and enable future microservice extraction, agents must adhere to the following import hierarchy:

```
apps/api ────────────┐
                     ↓
services/worker ───> packages/generation ───> packages/domain <─── packages/storage
                     │                      │                  │
                     ├──> packages/providers─┘                  └──> packages/media
                     │
                     └──> packages/shared
```

* **`packages/domain`**: Zero external dependencies (except Pydantic/SQLAlchemy domain interfaces). Contains domain entities (`Project`, `GenerationJob`, `GenerationPlan`, `Scene`, `MediaAsset`), repository interfaces, and domain exceptions.
* **`packages/providers`**: Implements interfaces defined in `domain`. May import external HTTP clients (e.g. `httpx`). Must not import from `generation` or `apps`.
* **`packages/storage`**: Implements object storage adapters (MinIO/S3). Interfaces defined in `domain`.
* **`packages/media`**: Wraps FFmpeg binaries and probe tools.
* **`packages/generation`**: Pipeline orchestrator and stage handlers. Coordinates domain repositories, providers, media tools, and storage.
* **`apps/api`**: Exposes HTTP controllers. Depends on `generation` application services, `domain`, and `shared`. NEVER calls AI provider SDKs directly inside routes.
* **`services/worker`**: Consumes async tasks and invokes `generation` pipeline routines.

---

## 5. Agent Execution Roadmap & Task Assignments

The development of Fídíò Studio is partitioned into 13 specialized agent roles (Agents 00 through 12). Agents must execute tasks sequentially according to the dependency graph below:

```
[Agent 00: Branding] ──┐
                       ├──> [Agent 01: Repository Foundation]
                       │            │
                       │            ▼
                       │    [Agent 02: Domain & PostgreSQL]
                       │            │
                       │            ▼
                       │    [Agent 03: Backend API]
                       │            │
                       ├────────────┴────────────────────────┐
                       ▼                                     ▼
             [Agent 04: AI Planning]               [Agent 07: MVP Frontend]
                       │                                     │
                       ▼                                     │
             [Agent 06: MinIO & Media]                       │
                       │                                     │
                       ▼                                     │
             [Agent 05: Generation Orchestrator] <───────────┘
                       │
                       ▼
             [Agent 08: End-to-End Integration]
                       │
                       ▼
             [Agent 09: Testing & QA]
                       │
                       ├─────────────────────────────────────┐
                       ▼                                     ▼
             [Agent 10: Security Hardening]       [Agent 11: Observability]
                       │                                     │
                       └────────────┬────────────────────────┘
                                    ▼
                         [Agent 12: Release & Docs]
```

### Detailed Agent Roles

* **Agent 00 — Brand Identity & SVG Assets:** Design and build Fídíò visual brand assets, SVGs, color palette, typography, brand guidelines, and design tokens (`branding/`).
* **Agent 01 — Repository Foundation:** Establish runnable project scaffold, `Makefile`, `docker-compose.yml`, Dockerfiles, logging, health endpoints, environment configuration.
* **Agent 02 — Domain & PostgreSQL:** Define SQLAlchemy ORM entities, Alembic migrations, database repositories, state transition logic, and database unit tests.
* **Agent 03 — Backend API:** Build REST API endpoints in `apps/api` (Projects, Plans, Jobs, Media Assets, Renders) with correlation IDs, error middleware, and OpenAPI specs.
* **Agent 04 — AI Planning & OpenRouter:** Implement structured LLM planning engine using OpenRouter adapter, strict JSON schema validation, timeout/retry logic, and cost tracking.
* **Agent 05 — Generation Orchestrator:** Implement asynchronous pipeline in `services/worker` and `packages/generation`, state machine, stage handlers, retries, and dev mock adapters.
* **Agent 06 — MinIO & Media Management:** Implement S3/MinIO object storage client, signed URL generation, media probe validation, and FFmpeg composition engine.
* **Agent 07 — MVP Frontend:** Implement modern web dashboard in `apps/web` (Project creation, Prompt submission, Real-time job progress tracking, Scene inspector, Video player/downloader).
* **Agent 08 — End-to-End Integration:** Connect UI, API, Worker, OpenRouter (or mock provider), MinIO, and FFmpeg into a seamless workflow; execute full verification.
* **Agent 09 — Testing & QA:** Build automated test suite covering unit tests, API integration tests, worker stage tests, asset validation, and chaos/failure scenarios.
* **Agent 10 — Security Hardening:** Audit secret handling, signed URL expirations, CORS/security headers, input sanitization, rate-limiting, and binary path traversal protections.
* **Agent 11 — Observability:** Add structured JSON logging, Prometheus metrics, OpenTelemetry tracing hooks, worker status health checks, and dashboard metrics.
* **Agent 12 — Release & Documentation:** Finalize production documentation, user guides, API reference, deployment scripts, and deployment verification artifacts.

---

## 6. Development & Quality Guidelines for Agents

1. **Idempotency & Resilience:** All background task execution must be idempotent. Worker retries must not result in duplicated generation API costs or corrupt storage files.
2. **Development Adapters:** When live AI API keys are unavailable, tests and local runs MUST use realistic mock adapters (`DevMockLLMProvider`, `DevMockMediaProvider`) clearly tagged as development adapters.
3. **No Hardcoded Secrets:** Configuration must use environment variables loaded via Pydantic BaseSettings. Default values must be safe for local dev environments only.
4. **Structured JSON Logging:** Use `structlog` or standard library JSON formatter including `request_id`, `job_id`, `project_id`, `provider_name`, and execution timestamps.
5. **Definition of Done for Sub-Tasks:** Every sub-task implementation MUST include unit or integration tests verifying functional correctness before marked complete.
