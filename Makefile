.PHONY: help install test lint format db-create db-migrate db-reset clean

PYTHON := uv run python
PYTEST := uv run pytest
RUFF := uv run ruff

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	uv sync --all-extras

install-dev: ## Install with dev dependencies
	uv sync --extra dev

test: ## Run test suite
	$(PYTEST) tests/ -v

test-fast: ## Run tests excluding slow/integration
	$(PYTEST) tests/ -v -m "not slow and not integration"

test-cov: ## Run tests with coverage
	$(PYTEST) tests/ --cov --cov-report=html --cov-report=term

lint: ## Run linter
	$(RUFF) check src/ tests/

format: ## Format code
	$(RUFF) format src/ tests/
	$(RUFF) check --fix src/ tests/

typecheck: ## Run type checker
	uv run mypy src/

# Database commands
DB_NAME ?= toponymia
DB_USER ?= $(USER)
DB_HOST ?= localhost
DB_PORT ?= 5432

db-create: ## Create database with PostGIS
	createdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) $(DB_NAME) || true
	psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) -c "CREATE EXTENSION IF NOT EXISTS postgis;"
	psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
	psql -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

db-migrate: ## Run database migrations
	uv run alembic upgrade head

db-rollback: ## Rollback last migration
	uv run alembic downgrade -1

db-reset: ## Drop and recreate database (DESTRUCTIVE)
	@echo "This will destroy all data in $(DB_NAME). Press Ctrl+C to cancel."
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	dropdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) $(DB_NAME) || true
	$(MAKE) db-create
	$(MAKE) db-migrate

# Data ingestion commands
ingest-geonames: ## Ingest GeoNames data (set COUNTRY=XX)
	$(PYTHON) -m toponymia.cli ingest geonames --country $(COUNTRY)

ingest-wikidata: ## Ingest Wikidata place names (set REGION=bbox)
	$(PYTHON) -m toponymia.cli ingest wikidata --region "$(REGION)"

# Analysis commands
segment: ## Run morphological segmentation (set REGION=XX)
	$(PYTHON) -m toponymia.cli segment --region $(REGION)

test-correspondence: ## Run correspondence test (set ELEMENT=x SIGNAL=y REGION=z)
	$(PYTHON) -m toponymia.cli test correspondence --element "$(ELEMENT)" --signal "$(SIGNAL)" --region "$(REGION)"

# Documentation
docs-serve: ## Serve documentation locally
	uv run mkdocs serve

docs-build: ## Build documentation
	uv run mkdocs build

clean: ## Remove build artefacts
	rm -rf dist/ build/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
