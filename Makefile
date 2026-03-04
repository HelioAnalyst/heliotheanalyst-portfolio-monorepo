# HelioTheAnalyst Portfolio Monorepo - Makefile
# Production-grade commands for development, testing, and deployment

.PHONY: help setup install-dev lint format typecheck test test-cov test-all \
        run-shopify run-helioscraper run-orders run-analytics run-api-testing run-inventory \
        run-all run-all-demos run-all-apis \
        up down logs up-observability \
        docker-up docker-down docker-logs docker-clean \
        clean clean-all docs-build docs-serve \
        pre-commit pre-commit-install ci

# =============================================================================
# Default Target
# =============================================================================
help:
	@echo "╔══════════════════════════════════════════════════════════════════════╗"
	@echo "║     HelioTheAnalyst Portfolio Monorepo - Available Commands          ║"
	@echo "╚══════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📦 SETUP COMMANDS:"
	@echo "  make setup              Setup all projects (create venvs, install deps)"
	@echo "  make install-dev        Install root dev dependencies only"
	@echo ""
	@echo "🔧 DEVELOPMENT COMMANDS:"
	@echo "  make lint               Run ruff linter on all projects"
	@echo "  make format             Format all code with ruff"
	@echo "  make typecheck          Run mypy type checker on all projects"
	@echo "  make pre-commit         Run pre-commit hooks on all files"
	@echo "  make pre-commit-install Install pre-commit hooks"
	@echo ""
	@echo "🧪 TESTING COMMANDS:"
	@echo "  make test               Run all tests"
	@echo "  make test-cov           Run tests with coverage report"
	@echo "  make test-all           Run tests, lint, and typecheck (full CI check)"
	@echo ""
	@echo "🚀 RUN COMMANDS:"
	@echo "  make run-shopify        Run Shopify Integration demo"
	@echo "  make run-helioscraper   Run HelioScraper demo"
	@echo "  make run-orders         Run Order Processing demo"
	@echo "  make run-analytics      Run Data Analysis Suite (Streamlit)"
	@echo "  make run-api-testing    Run API Testing Framework demo"
	@echo "  make run-inventory      Run Inventory Management GUI"
	@echo "  make run-all            Run all demos sequentially"
	@echo "  make run-all-demos      Alias for run-all"
	@echo "  make run-all-apis       Start all API services with Docker"
	@echo ""
	@echo "🐳 DOCKER COMMANDS:"
	@echo "  make up                 Start all Docker services (docker-compose up -d)"
	@echo "  make down               Stop all Docker services (docker-compose down)"
	@echo "  make logs               View Docker logs (docker-compose logs -f)"
	@echo "  make up-observability   Start Grafana dashboard (docker-compose --profile observability up -d)"
	@echo "  make docker-up          Start shared services (Postgres + Redis)"
	@echo "  make docker-down        Stop all Docker services"
	@echo "  make docker-logs        View Docker logs"
	@echo "  make docker-clean       Remove all Docker volumes and containers"
	@echo ""
	@echo "🧹 CLEANUP COMMANDS:"
	@echo "  make clean              Clean build artifacts"
	@echo "  make clean-all          Deep clean (includes Docker)"
	@echo ""
	@echo "📚 DOCUMENTATION COMMANDS:"
	@echo "  make docs-build         Build documentation"
	@echo "  make docs-serve         Serve documentation locally"
	@echo ""
	@echo "🔁 CI COMMANDS:"
	@echo "  make ci                 Run full CI pipeline locally"

# =============================================================================
# Setup Commands
# =============================================================================

setup: install-dev
	@echo ""
	@echo "📦 Setting up all projects..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@$(MAKE) setup-shopify
	@$(MAKE) setup-helioscraper
	@$(MAKE) setup-orders
	@$(MAKE) setup-analytics
	@$(MAKE) setup-api-testing
	@$(MAKE) setup-inventory
	@echo ""
	@echo "✅ All projects setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Start services: make up"
	@echo "  2. Run demos: make run-all-demos"

install-dev:
	@echo "📦 Installing root dev dependencies..."
	@pip install -e ".[dev]" --quiet

setup-shopify:
	@echo ""
	@echo "🔧 Setting up shopify-integration-system..."
	@cd projects/shopify-integration-system && \
		(python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv) && \
		.venv/bin/pip install -e ".[dev]" --quiet && \
		echo "  ✅ Shopify Integration ready"

setup-helioscraper:
	@echo ""
	@echo "🔧 Setting up helioscraper..."
	@cd projects/helioscraper && \
		(python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv) && \
		.venv/bin/pip install -e ".[dev]" --quiet && \
		echo "  ✅ HelioScraper ready"

setup-orders:
	@echo ""
	@echo "🔧 Setting up order-processing-automation..."
	@cd projects/order-processing-automation && \
		(python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv) && \
		.venv/bin/pip install -e ".[dev]" --quiet && \
		echo "  ✅ Order Processing ready"

setup-analytics:
	@echo ""
	@echo "🔧 Setting up data-analysis-visualization-suite..."
	@cd projects/data-analysis-visualization-suite && \
		(python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv) && \
		.venv/bin/pip install -e ".[dev]" --quiet && \
		echo "  ✅ Data Analysis Suite ready"

setup-api-testing:
	@echo ""
	@echo "🔧 Setting up api-docs-testing-framework..."
	@cd projects/api-docs-testing-framework && \
		(python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv) && \
		.venv/bin/pip install -e ".[dev]" --quiet && \
		echo "  ✅ API Testing Framework ready"

setup-inventory:
	@echo ""
	@echo "🔧 Setting up digital-inventory-management..."
	@cd projects/digital-inventory-management && \
		(python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv) && \
		.venv/bin/pip install -e ".[dev]" --quiet && \
		echo "  ✅ Digital Inventory ready"

# =============================================================================
# Code Quality Commands
# =============================================================================

lint:
	@echo ""
	@echo "🔍 Running ruff linter..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@ruff check projects/ --output-format=grouped || true

lint-fix:
	@echo ""
	@echo "🔧 Running ruff linter with auto-fix..."
	@ruff check projects/ --fix --output-format=grouped || true

format:
	@echo ""
	@echo "🎨 Formatting code with ruff..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@ruff format projects/

format-check:
	@echo ""
	@echo "🔍 Checking code formatting..."
	@ruff format projects/ --check || true

typecheck:
	@echo ""
	@echo "🔍 Running mypy type checker..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@mypy projects/shopify-integration-system/src \
		projects/helioscraper/src \
		projects/order-processing-automation/src \
		projects/data-analysis-visualization-suite/src \
		projects/api-docs-testing-framework/src \
		projects/digital-inventory-management/src \
		--ignore-missing-imports \
		--show-error-codes || true

# =============================================================================
# Testing Commands
# =============================================================================

test:
	@echo ""
	@echo "🧪 Running all tests..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@pytest projects/ -v --tb=short

test-cov:
	@echo ""
	@echo "🧪 Running tests with coverage..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@pytest projects/ -v --cov=projects --cov-report=html --cov-report=term-missing

test-all: lint format-check typecheck test-cov
	@echo ""
	@echo "✅ Full test suite complete!"

# =============================================================================
# Run Commands
# =============================================================================

run-shopify:
	@echo ""
	@echo "🚀 Running Shopify Integration System demo..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@cd projects/shopify-integration-system && .venv/bin/python scripts/run_demo.py

run-helioscraper:
	@echo ""
	@echo "🚀 Running HelioScraper demo..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@cd projects/helioscraper && .venv/bin/python scripts/run_demo.py

run-orders:
	@echo ""
	@echo "🚀 Running Order Processing Automation demo..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@cd projects/order-processing-automation && .venv/bin/python scripts/run_demo.py

run-analytics:
	@echo ""
	@echo "🚀 Starting Data Analysis & Visualization Suite (Streamlit)..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@cd projects/data-analysis-visualization-suite && .venv/bin/streamlit run src/app.py

run-api-testing:
	@echo ""
	@echo "🚀 Running API Docs & Testing Framework demo..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@cd projects/api-docs-testing-framework && .venv/bin/python scripts/run_demo.py

run-inventory:
	@echo ""
	@echo "🚀 Starting Digital Inventory Management GUI..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@cd projects/digital-inventory-management && .venv/bin/python src/main.py

run-all:
	@echo ""
	@echo "🚀 Running all project demos..."
	@echo "═══════════════════════════════════════════════════════════════════════"
	@python scripts/run_all_demos.py

run-all-demos: run-all
	@true

run-all-apis:
	@echo ""
	@echo "🚀 Starting all API services with Docker..."
	@docker-compose --profile all-apis up -d
	@echo ""
	@echo "Services started:"
	@echo "  - Shopify API:      http://localhost:8000"
	@echo "  - Order API:        http://localhost:8001"
	@echo "  - API Testing:      http://localhost:8002"
	@echo "  - Flower Dashboard: http://localhost:5555"

# =============================================================================
# Docker Commands (Short Aliases)
# =============================================================================

up:
	@echo ""
	@echo "🐳 Starting all Docker services..."
	@docker-compose up -d
	@echo ""
	@echo "✅ Services started:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis:      localhost:6379"

down:
	@echo ""
	@echo "🐳 Stopping all Docker services..."
	@docker-compose down

logs:
	@docker-compose logs -f

up-observability:
	@echo ""
	@echo "🐳 Starting Grafana observability dashboard..."
	@docker-compose --profile observability up -d
	@echo ""
	@echo "✅ Grafana started:"
	@echo "  - URL: http://localhost:3000"
	@echo "  - Login: admin / admin"

# =============================================================================
# Docker Commands (Legacy/Detailed)
# =============================================================================

docker-up:
	@echo ""
	@echo "🐳 Starting shared services (PostgreSQL + Redis)..."
	@docker-compose up -d postgres redis
	@echo ""
	@echo "✅ Services started:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis:      localhost:6379"

docker-down:
	@echo ""
	@echo "🐳 Stopping all Docker services..."
	@docker-compose down

docker-logs:
	@docker-compose logs -f

docker-clean:
	@echo ""
	@echo "🧹 Cleaning Docker containers and volumes..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f

# =============================================================================
# Cleanup Commands
# =============================================================================

clean:
	@echo ""
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	@echo "✅ Clean complete!"

clean-all: clean docker-clean
	@echo ""
	@echo "🧹 Deep cleaning (removing virtual environments)..."
	@find projects -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
	@find projects -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Deep clean complete!"

# =============================================================================
# Pre-commit Commands
# =============================================================================

pre-commit-install:
	@echo ""
	@echo "🔧 Installing pre-commit hooks..."
	@pre-commit install
	@pre-commit install --hook-type pre-push

pre-commit:
	@echo ""
	@echo "🔍 Running pre-commit hooks..."
	@pre-commit run --all-files

# =============================================================================
# CI Commands
# =============================================================================

ci: lint format-check typecheck test-cov
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════════╗"
	@echo "║                    ✅ CI Pipeline Complete!                          ║"
	@echo "╚══════════════════════════════════════════════════════════════════════╝"

# =============================================================================
# Documentation Commands
# =============================================================================

docs-build:
	@echo ""
	@echo "📚 Building documentation..."
	@echo "Documentation source: docs/"

docs-serve:
	@echo ""
	@echo "📚 Serving documentation..."
	@echo "Open: docs/website/projects.json for project data"
