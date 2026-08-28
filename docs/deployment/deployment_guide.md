# Fídíò Studio Production Deployment & Operations Guide

**Target Host:** Linux (Ubuntu 24.04 LTS / Debian 12)  
**Production Domain:** `https://fidio.site`  

---

## 1. Architecture Infrastructure Stack

- **REST API:** FastAPI application managed by systemd (`fidio-api.service`) on port `8000`.
- **Worker:** Celery/RQ async pipeline runner managed by systemd (`fidio-worker.service`).
- **Database:** Remote PostgreSQL database (`postgresql+asyncpg://...`).
- **Object Storage:** MinIO S3 server running on port `9000`.
- **Web Server / Reverse Proxy:** Apache 2.4 with SSL certificate (`mod_ssl`, Let's Encrypt) proxying `/api/v1` and `/healthz` to FastAPI backend and serving static web UI (`/var/www/html/public`).

---

## 2. Systemd Service Configurations

### `/etc/systemd/system/fidio-api.service`
```ini
[Unit]
Description=${APP_SERVICE_NAME}
After=network.target

[Service]
User=${DEPLOY_USER}
WorkingDirectory=${DEPLOY_PATH}
EnvironmentFile=${DEPLOY_PATH}/.env
ExecStart=${DEPLOY_PATH}/.venv/bin/uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/fidio-worker.service`
```ini
[Unit]
Description=${WORKER_SERVICE_NAME}
After=network.target

[Service]
User=${DEPLOY_USER}
WorkingDirectory=${DEPLOY_PATH}
EnvironmentFile=${DEPLOY_PATH}/.env
ExecStart=${DEPLOY_PATH}/.venv/bin/python services/worker/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 3. Operational Deployment Steps

```bash
# SSH into production server (configured via DEPLOY_USER and DEPLOY_HOST)
ssh ${DEPLOY_USER}@${DEPLOY_HOST}

# Navigate to application deployment directory
cd ${DEPLOY_PATH}
git status

# Apply database migrations
PYTHONPATH=. ${DEPLOY_PATH}/.venv/bin/alembic upgrade head

# Restart services
sudo systemctl restart fidio-api fidio-worker

# Check service health
sudo systemctl status fidio-api fidio-worker
python scripts/smoke_test.py https://fidio.site/api/v1
```
