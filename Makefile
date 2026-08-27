# ==============================================================================
# FÍDÍÒ STUDIO — DEVELOPER MAKEFILE
# Brand: Fídíò | Tagline: Imagine. Create. Fídíò.
# ==============================================================================

.PHONY: help setup dev dev-down dev-logs migrate migration test test-unit test-integration test-e2e lint format seed clean

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Fídíò Studio — Available Makefile Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Install local dependencies and virtual environment
	@echo "Setting up Fídíò Studio local environment..."
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	@echo "Setup complete. Activate with: source .venv/bin/activate"

dev: ## Start Docker Compose development stack (API, Web, Worker, MinIO, Redis)
	@echo "Starting Fídíò Studio Docker Compose services..."
	docker compose up -d --build

dev-down: ## Stop and remove Docker Compose services
	@echo "Stopping Fídíò Studio Docker Compose services..."
	docker compose down --remove-orphans

dev-logs: ## Tail real-time logs for all services
	docker compose logs -f

migrate: ## Run Alembic database migrations against external PostgreSQL
	@echo "Running database migrations..."
	.venv/bin/alembic upgrade head || docker compose exec api alembic upgrade head

migration: ## Generate new Alembic migration script (Usage: make migration msg="add_table")
	@echo "Generating migration: $(msg)..."
	.venv/bin/alembic revision --autogenerate -m "$(msg)"

test: test-unit test-integration ## Run unit and integration tests

test-unit: ## Run fast backend unit tests
	@echo "Running unit tests..."
	pytest tests/unit

test-integration: ## Run database and object storage integration tests
	@echo "Running integration tests..."
	pytest tests/integration

test-e2e: ## Run end-to-end user flow integration tests
	@echo "Running end-to-end tests..."
	pytest tests/e2e

lint: ## Run linters and type checkers (ruff, mypy)
	@echo "Linting Python packages and services..."
	ruff check packages/ apps/ services/
	mypy packages/ apps/api

format: ## Format Python code (ruff format)
	@echo "Formatting Python files..."
	ruff format packages/ apps/ services/ tests/

seed: ## Seed PostgreSQL database with sample development projects and mock data
	@echo "Seeding development database..."
	python3 infrastructure/scripts/seed_dev_db.py

clean: ## Remove python cache, test artifacts, and temp build directories
	@echo "Cleaning temporary build and test files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf dist/ build/ *.egg-info
