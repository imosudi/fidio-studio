# Development Commands & Developer Setup — Fídíò Studio

**Makefile Target Specifications & Docker Compose Execution Guide**

---

## 1. Prerequisites

Before running Fídíò Studio locally, verify your system has:
- **Docker & Docker Compose** (v24.0+)
- **Python** (v3.11+)
- **Node.js** (v18+ / v20+) & `npm`
- **PostgreSQL** (v14+ running on local host or accessible network IP)
- **FFmpeg** (installed locally for non-containerized CLI testing)

---

## 2. Environment Configuration Setup

1. Copy template configuration:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` to configure your external PostgreSQL credentials:
   ```env
   POSTGRES_HOST=127.0.0.1
   POSTGRES_PORT=5432
   POSTGRES_DB=fidio-studio
   POSTGRES_USER=fidio-studio
   POSTGRES_PASSWORD=your_password
   ```

---

## 3. Makefile Local Command Reference

A root `Makefile` is provided to simplify developer workflows:

| Command | Action |
|---|---|
| `make help` | Display available targets and descriptions. |
| `make setup` | Create Python virtual environment and install backend + frontend dependencies. |
| `make dev` | Start full Docker Compose development stack (`api`, `web`, `worker`, `minio`, `redis`). |
| `make dev-down` | Stop and remove all running Docker Compose containers. |
| `make dev-logs` | Tail real-time logs across container services. |
| `make migrate` | Execute Alembic database migrations against PostgreSQL. |
| `make migration msg="name"` | Generate a new Alembic migration script. |
| `make test` | Run complete backend and frontend test suites. |
| `make test-unit` | Run fast unit tests (`pytest tests/unit`). |
| `make test-integration` | Run integration tests against DB and MinIO (`pytest tests/integration`). |
| `make test-e2e` | Run end-to-end integration tests. |
| `make lint` | Run code quality linters (`ruff`, `mypy`, `eslint`). |
| `make format` | Auto-format codebase using `ruff format` and `prettier`. |
| `make seed` | Load sample dev projects, prompts, and mock media assets into local environment. |
| `make clean` | Remove Python cache files, build artifacts, and temporary test assets. |

---

## 4. Docker Compose Commands

### 4.1 Launching the Stack

To start application containers (API, Web, Worker, MinIO, Redis) with hot-reloading:

```bash
docker compose up -d --build
```

### 4.2 Verifying Container Services

```bash
docker compose ps
```

Expected containers:
- `fidio-api` (Port 8000)
- `fidio-web` (Port 3000)
- `fidio-worker` (Background task executor)
- `fidio-minio` (Port 9000 API, Port 9001 Console)
- `fidio-redis` (Port 6379)

### 4.3 MinIO Object Storage Setup

MinIO web console is accessible at `http://localhost:9001` (Credentials: `minioadmin` / `minioadmin`).  
Buckets (`fidio-raw`, `fidio-assets`, `fidio-renders`, `fidio-temp`) are automatically created during system bootstrap by `infrastructure/minio/init_buckets.sh`.

---

## 5. Local Database Setup (PostgreSQL)

If using a local PostgreSQL instance:

```bash
# Create database and user
sudo -u postgres psql -c "CREATE USER \"fidio-studio\" WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE \"fidio-studio\" OWNER \"fidio-studio\";"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"fidio-studio\" TO \"fidio-studio\";"

# Run migrations
make migrate
```
