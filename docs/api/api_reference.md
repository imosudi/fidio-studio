# Fídíò Studio REST API Reference

**Base URL:** `https://fidio.site/api/v1` (or `http://localhost:8000/api/v1`)  
**Format:** JSON  
**Header Requirements:** `Content-Type: application/json`  

---

## Endpoints

### 1. Projects Router (`/api/v1/projects`)

#### `POST /api/v1/projects`
Create a new creative project.

**Request Body:**
```json
{
  "name": "Cyberpunk City 2099",
  "description": "Futuristic neon city intro video",
  "aspect_ratio": "16:9"
}
```

**Response (201 Created):**
```json
{
  "id": "712162e9-26b9-4830-bc05-7cca04687335",
  "name": "Cyberpunk City 2099",
  "description": "Futuristic neon city intro video",
  "aspect_ratio": "16:9",
  "created_at": "2026-08-28T00:00:00Z"
}
```

#### `GET /api/v1/projects`
List all creative projects.

---

### 2. Generation Router (`/api/v1/projects/{id}/generations`)

#### `POST /api/v1/projects/{id}/generations`
Submit an AI video generation request for a project.

**Request Body:**
```json
{
  "prompt": "Cinematic wide shot of a cyberpunk city under rain with dramatic neon accents",
  "style": "cinematic",
  "target_duration_seconds": 15,
  "aspect_ratio": "16:9",
  "idempotency_key": "optional_unique_key_123"
}
```

**Response (202 Accepted):**
```json
{
  "generation_request_id": "892162e9-26b9-4830-bc05-7cca04687335",
  "job_id": "6d9e48d8-d905-484b-8186-2e8ea43d0921",
  "status": "QUEUED",
  "is_idempotent": false
}
```

---

### 3. Jobs Router (`/api/v1/jobs/{id}`)

#### `GET /api/v1/jobs/{id}`
Poll real-time job status and pipeline progress percentage.

**Response (200 OK):**
```json
{
  "job_id": "6d9e48d8-d905-484b-8186-2e8ea43d0921",
  "status": "COMPLETED",
  "stage": "COMPLETED",
  "progress_percentage": 100,
  "completed_at": "2026-08-28T00:00:07Z"
}
```

---

### 4. Media Assets Router (`/api/v1/projects/{id}/assets`)

#### `GET /api/v1/projects/{id}/assets`
List project media assets and video renders with S3 presigned download URLs.

**Response (200 OK):**
```json
{
  "project_id": "712162e9-26b9-4830-bc05-7cca04687335",
  "assets": [
    {
      "id": "70f3e197-6c0e-41b4-8b75-69449f1cd285",
      "type": "RENDER",
      "format": "mp4",
      "download_url": "https://fidio.site:9000/fidio-media/renders/test.mp4?token=..."
    }
  ]
}
```
