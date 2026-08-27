# Testing Strategy & Quality Assurance — Fídíò Studio

This document defines the multi-layer testing strategy, test types, mock adapters, asset validation routines, and continuous integration standards for Fídíò Studio.

---

## 1. Multi-Layer Testing Architecture

```
                  ┌───────────────────────────────────┐
                  │       End-to-End Tests            │
                  │   (Full system flow via browser)  │
                  └─────────────────┬─────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │      API & Service Contracts       │
                  │   (FastAPI TestClient + Schemas)  │
                  └─────────────────┬─────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │     Integration & Pipeline        │
                  │ (PostgreSQL, MinIO, Worker state) │
                  └─────────────────┬─────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │            Unit Tests             │
                  │ (Domain models, FFmpeg, Providers)│
                  └───────────────────────────────────┘
```

---

## 2. Test Categories & Responsibilities

| Test Layer | Directory | Scope & Targets | Primary Tools | Execution Speed |
|---|---|---|---|---|
| **Unit Tests** | `tests/unit/` | Pure business rules, domain entities, value validation, provider response parsing, FFmpeg command builder, cost calculations. | `pytest`, `pytest-mock` | High (< 5 seconds) |
| **Integration Tests** | `tests/integration/` | Database repositories, Alembic migration upgrades/downgrades, MinIO upload/download presigned URLs, Redis job queue handling. | `pytest-asyncio`, TestContainers / Disposable MinIO | Medium (< 30 seconds) |
| **API Contract Tests** | `tests/contract/` | REST API routes, OpenAPI schema conformance, correlation ID propagation, error body format, idempotency key deduplication. | `httpx`, Pydantic | Medium (< 15 seconds) |
| **Pipeline Stage Tests** | `tests/pipeline/` | Stage state machine execution (`PLANNING` -> `GENERATING_ASSETS` -> `RENDERING`), worker retries, failed stage recovery, mock provider integration. | `pytest`, Dev Mock Adapters | Medium (< 30 seconds) |
| **End-to-End Tests** | `tests/e2e/` | Full user journey: Project creation -> Prompt submission -> Plan generation -> Scene asset rendering -> Video preview & download. | Playwright / Subagent Browser | Slow (< 2 minutes) |

---

## 3. Mock Provider Integration Strategy

To ensure test suites run quickly, reliably, and deterministically without incurring API costs or requiring live secrets, Fídíò Studio provides explicit development mock adapters:

- **`DevMockLLMProvider`:** Returns deterministic `GenerationPlan` structures with configurable scene counts and pre-canned narrative scripts. Supports injecting malformed JSON, rate limit status codes (429), and timeout exceptions to verify error handling.
- **`DevMockImageProvider`:** Generates lightweight solid-color PNG/JPEG test assets locally and uploads to MinIO.
- **`DevMockVideoProvider`:** Generates short 2-second synthetic color-bar test MP4 files using local FFmpeg commands.
- **`DevMockVoiceProvider`:** Generates synthetic silent WAV/MP3 audio files.

---

## 4. Media Asset & Pipeline Validation Standards

Automated tests for media storage and rendering must validate:
1. **Container & Format Integrity:** Verify output files created by FFmpeg are valid MP4 containers (`ffprobe -v error -show_format`).
2. **Audio/Video Stream Alignment:** Ensure output renders contain both video and audio streams with matching durations.
3. **Aspect Ratio Enforcement:** Verify output dimensions match requested ratio (e.g. 1920x1080 for 16:9, 1080x1920 for 9:16).
4. **Presigned URL Expiration & Security:** Verify signed S3 URLs reject unauthorized access after expiration.

---

## 5. Quality Gate Execution Commands

```bash
# Run unit tests only
pytest tests/unit

# Run full test suite with coverage report
pytest --cov=packages --cov=apps/api tests/

# Run linting and type checks
ruff check packages/ apps/ services/
mypy packages/ apps/api
```
