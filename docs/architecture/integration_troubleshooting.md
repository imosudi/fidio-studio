# Integration Troubleshooting & Architecture Operations Guide

**System:** Fídíò Studio Platform  
**Target Audience:** DevOps, System Engineers, Platform Developers  

---

## 1. System Component Architecture & Flow Map

```
                  FÍDÍÒ STUDIO WEB APP (Public Port 80/443)
                                 │
                        ProxyPass /api/v1
                                 ↓
                  FASTAPI REST API (127.0.0.1:8000)
                                 │
           ┌─────────────────────┼─────────────────────┐
           ↓                     ↓                     ↓
     PostgreSQL DB          MinIO S3 Storage     Redis Queue / Systemd
   (State & Metadata)     (Media & Renders)      (Worker Engine)
```

---

## 2. Environment Configurations & Dependencies

| Environment Variable | Required Service | Default Local | Production Staging | Description |
| :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | API / Worker | `postgresql+asyncpg://...` | `postgresql+asyncpg://mosud_fidio:...@104.207.88.53:5432/fidio_db` | Async SQLAlchemy PostgreSQL connection string |
| `MINIO_ENDPOINT` | Storage Adapter | `http://localhost:9000` | `http://104.207.88.53:9000` | Internal MinIO S3 API endpoint |
| `MINIO_EXTERNAL_ENDPOINT` | API Presigned URLs | `http://localhost:9000` | `https://fidio.site` | Client-facing S3 presigned URL host |
| `OPENROUTER_API_KEY` | AI Planner | `dev_mock_key` | Real Key / `dev_mock_key` | OpenRouter API Key for live LLM planning |
| `APP_ENV` | Global | `development` | `production` | Environment mode (`development`, `staging`, `production`) |

---

## 3. Common Integration Failure Modes & Diagnostic Playbook

### Failure Mode 1: Job Stuck in `QUEUED` State
- **Symptom:** UI progress remains at 0% or job status is perpetually `QUEUED`.
- **Root Cause:** Background worker service (`fidio-worker.service`) is stopped or crashing on database pool initialization.
- **Diagnostic Command:**
  ```bash
  systemctl status fidio-worker.service --no-pager
  journalctl -u fidio-worker.service -n 50 --no-pager
  ```
- **Resolution:** Restart the worker service: `sudo systemctl restart fidio-worker`.

---

### Failure Mode 2: Presigned S3 Download URLs Return 404 or Host Unreachable
- **Symptom:** Asset previews or render download buttons fail in browser.
- **Root Cause:** `MINIO_EXTERNAL_ENDPOINT` is misconfigured or pointing to an unroutable internal IP address.
- **Diagnostic Command:**
  ```bash
  curl -I "$MINIO_EXTERNAL_ENDPOINT/fidio-renders/..."
  ```
- **Resolution:** Set `MINIO_EXTERNAL_ENDPOINT` in `.env` to point to public domain or proxy endpoint (`https://fidio.site`).

---

### Failure Mode 3: Apache Reverse Proxy 404 for `/api/v1`
- **Symptom:** Frontend web application shows `API Engine Inactive` or fetch errors.
- **Root Cause:** Missing `ProxyPass` rules in Apache SSL virtual host (`fidio-le-ssl.conf`).
- **Diagnostic Command:**
  ```bash
  sudo apache2ctl -S
  sudo cat /etc/apache2/sites-available/fidio-le-ssl.conf
  ```
- **Resolution:** Ensure `ProxyPass /api/v1 http://127.0.0.1:8000/api/v1` and `ProxyPassReverse /api/v1 http://127.0.0.1:8000/api/v1` are present and reload Apache (`sudo systemctl reload apache2`).

---

## 4. Automated Smoke Test Verification

To execute automated end-to-end integration health validation against any live or staging environment:

```bash
python3 scripts/smoke_test.py https://fidio.site/api/v1
```
