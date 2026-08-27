# API Conventions & Endpoint Specification — Fídíò API

**Prefix:** `/api/v1`  
**Format:** JSON (UTF-8)  
**Authentication:** Bearer Token (JWT) or API Key (`X-API-Key`) for developer integrations  

---

## 1. General Principles

1. **RESTful Design:** Standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`) with resource-oriented URIs.
2. **Stateless Operations:** API endpoints do not store session state in memory. Long-running operations return `HTTP 202 Accepted` with a job resource URL.
3. **Correlation ID Tracking:** Every API request must include or generate an `X-Correlation-ID` header, propagated to backend logs and background worker queues.
4. **Idempotency Header:** Mutating POST endpoints accept `Idempotency-Key`. Submitting duplicate keys within 24 hours returns cached responses without re-triggering operations.
5. **No Exposure of Internal Paths:** Object storage file paths are never returned. Instead, temporal presigned S3 URLs (`download_url`, `stream_url`) are generated.

---

## 2. Standard Response Envelope & Error Format

### 2.1 Success Response Envelope

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "correlation_id": "req_01H9Z23456789ABCDEF",
    "timestamp": "2026-08-28T00:00:00Z"
  }
}
```

### 2.2 Error Response Schema

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PROMPT_FORMAT",
    "message": "Generation request prompt must be between 10 and 2000 characters.",
    "details": [
      {
        "field": "prompt",
        "issue": "String length is less than minimum 10 characters."
      }
    ],
    "correlation_id": "req_01H9Z23456789ABCDEF",
    "timestamp": "2026-08-28T00:00:00Z"
  }
}
```

### 2.3 Standard HTTP Status Codes

- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `202 Accepted`: Asynchronous job accepted for processing.
- `400 Bad Request`: Validation failure or malformed body.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: User lacks permission for the resource.
- `404 Not Found`: Resource does not exist.
- `409 Conflict`: Resource state conflict (e.g. duplicate idempotency key).
- `422 Unprocessable Entity`: Request syntax valid, but semantic validation failed.
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Server Error`: Unexpected backend error.

---

## 3. Core REST Endpoints Specification

### 3.1 System & Health

* `GET /api/v1/health`
  - Response: `{ "status": "ok", "version": "0.1.0", "database": "connected", "storage": "connected" }`
* `GET /api/v1/readiness`
  - Response: `{ "ready": true }`

### 3.2 Projects (`/api/v1/projects`)

* `POST /api/v1/projects`
  - Creates a new video project.
  - Body: `{ "name": "Launch Video", "description": "Product intro", "aspect_ratio": "16:9" }`
* `GET /api/v1/projects`
  - List projects for current user with pagination.
* `GET /api/v1/projects/{project_id}`
  - Get details of a specific project.
* `DELETE /api/v1/projects/{project_id}`
  - Soft-delete a project.

### 3.3 Generation Requests & Plans (`/api/v1/projects/{project_id}/generations`)

* `POST /api/v1/projects/{project_id}/generations`
  - Create a video generation request and enqueue job.
  - Headers: `Idempotency-Key: <uuid>`
  - Body:
    ```json
    {
      "prompt": "A futuristic cinematic showcase of Fídíò Studio operating in a neon-lit creative studio.",
      "style": "cinematic",
      "target_duration_seconds": 15,
      "aspect_ratio": "16:9",
      "voice_over_enabled": true,
      "model_config": {
        "llm_model": "anthropic/claude-3.5-sonnet",
        "image_model": "stabilityai/sdxl"
      }
    }
    ```
  - Response: `202 Accepted` with `{ "job_id": "job_123", "status": "QUEUED" }`.

* `GET /api/v1/projects/{project_id}/generations/{generation_id}`
  - Fetch generation request details, including generated plan and scenes once planned.

### 3.4 Generation Jobs & Status (`/api/v1/jobs`)

* `GET /api/v1/jobs/{job_id}`
  - Fetch job status, current stage (`QUEUED`, `PLANNING`, `GENERATING_ASSETS`, `RENDERING`, `COMPLETED`, `FAILED`), progress percentage, step details, and error metadata if failed.
* `POST /api/v1/jobs/{job_id}/cancel`
  - Request job cancellation.
* `POST /api/v1/jobs/{job_id}/retry`
  - Retry a failed generation job.

### 3.5 Media Assets & Renders (`/api/v1/media`)

* `GET /api/v1/media/{asset_id}`
  - Get metadata for a generated image, audio, or video clip. Includes temporary presigned MinIO URL.
* `GET /api/v1/projects/{project_id}/renders/{render_id}`
  - Get final output render metadata and presigned download URL.
