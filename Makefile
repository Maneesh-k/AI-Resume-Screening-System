.PHONY: help dev-api dev-web dev up down build test lint migrate seed

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker ──────────────────────────────────────────────────
up: ## Start all services via Docker Compose
	docker-compose up --build

down: ## Stop all services
	docker-compose down

up-db: ## Start only Postgres and Redis
	docker-compose up -d postgres redis

logs: ## Tail logs for all services
	docker-compose logs -f

# ── Development ──────────────────────────────────────────────
dev-api: ## Start FastAPI dev server with hot reload
	cd apps/api && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-web: ## Start Next.js dev server
	cd apps/web && pnpm dev

dev-worker: ## Start SQS worker
	cd apps/api && python -m src.worker.main

# ── Database ─────────────────────────────────────────────────
migrate: ## Run Alembic migrations
	cd apps/api && alembic upgrade head

migrate-down: ## Rollback last Alembic migration
	cd apps/api && alembic downgrade -1

migrate-create: ## Create new migration (usage: make migrate-create name=add_table)
	cd apps/api && alembic revision --autogenerate -m "$(name)"

migrate-history: ## Show migration history
	cd apps/api && alembic history

seed: ## Seed database with sample data
	cd apps/api && python -m scripts.seed

# ── Testing ──────────────────────────────────────────────────
test-api: ## Run backend tests
	cd apps/api && pytest -v --cov=src --cov-report=term-missing

test-web: ## Run frontend tests
	cd apps/web && pnpm test

test: test-api test-web ## Run all tests

# ── Linting / Formatting ─────────────────────────────────────
lint-api: ## Lint backend
	cd apps/api && ruff check . && mypy src

format-api: ## Format backend
	cd apps/api && ruff format .

lint-web: ## Lint frontend
	cd apps/web && pnpm lint

type-check-web: ## Type check frontend
	cd apps/web && pnpm type-check

lint: lint-api lint-web ## Lint everything

# ── Setup ────────────────────────────────────────────────────
setup: ## Full project setup (install deps, copy env, migrate)
	@echo "Setting up AI Hiring Copilot..."
	@cp -n .env.example .env || true
	@cd apps/api && python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
	@cd apps/web && pnpm install
	@echo "Run 'make up-db && make migrate' to finish setup"

install-web: ## Install frontend dependencies
	cd apps/web && pnpm install

# ── Utilities ────────────────────────────────────────────────
shell-api: ## Open Python shell in API container
	docker-compose exec api python

psql: ## Open psql in DB container
	docker-compose exec postgres psql -U postgres -d hiring_copilot
