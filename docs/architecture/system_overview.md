# Fídíò Studio System Architecture Specification

**Brand:** Fídíò  
**Product:** Fídíò Studio  
**Tagline:** Imagine. Create. Fídíò.  
**Repository:** `fidio-studio`  

---

## 1. System Vision & Architecture

Fídíò Studio is an intelligent creative technology platform designed to transform user text ideas into production-ready video content through structured AI understanding, multi-modal generation, and precise audio-visual composition.

```
                                  FÍDÍÒ
                                    │
    ┌───────────────┬───────────────┼───────────────┬───────────────┐
    ↓               ↓               ↓               ↓               ↓
  Studio          Engine           API            Cloud         Enterprise
(Creator UI)    (AI & Render)  (Dev Integration) (Hosted Platform) (Self-Hosted)
```

---

## 2. Package & Layer Structure

The codebase is organized into strict package boundaries (`packages/`, `apps/`, `services/`):

- **`apps/api/`**: FastAPI REST API handling Projects, Generation Requests, Job Status Polling, Asset Listing, and Security Middleware.
- **`apps/web/`**: Modern SPA Creator Dashboard (`public/index.html`).
- **`services/worker/`**: Asynchronous task worker loop polling PostgreSQL job queue and executing `PipelineOrchestrator`.
- **`packages/domain/`**: Pure domain entities (`Project`, `GenerationJob`, `GenerationPlan`, `Scene`, `MediaAsset`, `Render`), state machine rules (`JobStateMachine`), and SQLAlchemy 2.0 ORM mappings.
- **`packages/generation/`**: Generation pipeline orchestrator (`PipelineOrchestrator`), AI prompt planner (`GenerationPlanner`), and stage handlers.
- **`packages/providers/`**: Abstract AI provider adapters (`LLMProvider`, `OpenRouterLLMProvider`, `DevMockLLMProvider`, `DevMockMediaProvider`).
- **`packages/storage/`**: Object storage interface (`ObjectStorage`), `MinIOStorageAdapter`, and `DevMockStorageAdapter`.
- **`packages/media/`**: FFmpeg media composition engine (`FFmpegEngine`) and binary magic-byte probe validator (`MediaProbe`).
- **`packages/shared/`**: JSON structured logging (`logger`), Prometheus metrics exporter (`telemetry`), and exceptions.

---

## 3. Asynchronous Pipeline Execution Lifecycle

```
  [User UI]
     │
     ▼
[POST /api/v1/projects/{id}/generations]
     │
     ▼
[Save Request & Queue Job (Status: QUEUED)]
     │
     ▼
[Async Worker Polls Queue]
     │
     ▼
┌────┴──────────────────────────────────────────┐
│ PipelineOrchestrator Stage Execution          │
├───────────────────────────────────────────────┤
│ Stage 1: AI Planning (OpenRouter / DevMock)   │
│ Stage 2: Visual Generation (Images -> MinIO)  │
│ Stage 3: Audio Synthesis (Audio -> MinIO)     │
│ Stage 4: FFmpeg Video Render Composition      │
└────┬──────────────────────────────────────────┘
     │
     ▼
[Job Status: COMPLETED (100% Progress)]
     │
     ▼
[User Views & Downloads MP4 via Presigned URL]
```
