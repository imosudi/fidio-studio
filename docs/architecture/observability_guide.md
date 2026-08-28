# Operational Observability & Telemetry Guide

**Product:** Fídíò Studio  
**Namespace:** `fidio`  
**Observability Standard:** Structured JSON Logging + Prometheus Metrics  

---

## 1. Overview & Architecture

Fídíò Studio implements lightweight, production-grade observability without heavy external dependencies. It combines:
1. **Correlation Tracing:** `X-Correlation-ID` header injected at the API boundary and propagated through worker execution loops.
2. **Structured JSON Logs:** Machine-readable logs including timestamp, log level, correlation ID, job ID, and module context. Sensitive tokens are automatically redacted via `redact_secrets()`.
3. **Prometheus Metrics Exporter:** Real-time metrics scraped at `GET /metrics`.

---

## 2. Structured JSON Log Event Format

All logs output to standard output (`stdout`) in single-line JSON format:

```json
{
  "timestamp": "2026-08-28 03:40:55",
  "level": "INFO",
  "logger": "fidio",
  "message": "POST /api/v1/projects -> 201 (18.4ms)",
  "module": "main",
  "filename": "main.py",
  "line": 68,
  "correlation_id": "c7a29e48-8186-4830-bc05-7cca04687335",
  "job_id": "6d9e48d8-d905-484b-8186-2e8ea43d0921"
}
```

---

## 3. Prometheus Metrics Catalog (`/metrics`)

| Metric Name | Type | Description | Labels |
| :--- | :--- | :--- | :--- |
| `http_requests_total` | Counter | Total HTTP requests handled by REST API | `method`, `status` |
| `http_request_duration_seconds` | Histogram | Request latency distribution in seconds | `method` |
| `fidio_jobs_total` | Counter | Total generation jobs processed | `status` (`COMPLETED`, `FAILED`, `CANCELLED`) |
| `fidio_job_duration_seconds` | Histogram | Pipeline job execution time in seconds | `stage` (`FULL`, `PLANNING`, `RENDERING`) |
| `fidio_provider_requests_total` | Counter | AI provider invocations | `provider` (`OpenRouter`, `DevMock`) |

---

## 4. End-to-End Log Correlation Flow

```
HTTP Request (Header: X-Correlation-ID)
   │
   ├─► FastAPI Middleware (Logs: "POST /api/v1/projects/...")
   │
   ├─► Database Persist (Job ID: 6d9e48d8-d905...)
   │
   ├─► Worker Execution Loop (Logs: "Executing job ID=6d9e48d8...")
   │
   ├─► AI Provider Planner (Logs: "Generating plan for prompt...")
   │
   ├─► FFmpeg Composition (Logs: "Executing FFmpeg composition...")
   │
   └─► Completion (Logs: "Successfully completed GenerationJob ID=6d9e48d8 in 7.07s")
```

---

## 5. Prometheus Scrape Configuration (`prometheus.yml`)

```yaml
scrape_configs:
  - job_name: 'fidio-studio'
    scrape_interval: 15s
    metrics_path: '/metrics'
    static_configs:
      - targets: ['fidio.site:443']
        scheme: 'https'
```
