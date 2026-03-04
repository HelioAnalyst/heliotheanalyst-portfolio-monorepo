# HelioTheAnalyst Portfolio Monorepo

A comprehensive collection of production-ready data engineering and automation projects by HelioTheAnalyst.

## Quickstart (3 Minutes)

```bash
# 1. Clone and enter the monorepo
cd heliotheanalyst-portfolio-monorepo

# 2. Setup all projects (creates venvs, installs deps)
make setup

# 3. Run all demos (mock mode - no credentials needed)
make run-all-demos

# 4. Run all tests
make test
```

## Projects Overview

| Project | Tech Stack | Description | Demo Time |
|---------|------------|-------------|-----------|
| [shopify-integration-system](./projects/shopify-integration-system/) | FastAPI, Postgres, Redis | E-commerce sync with rate limiting, retries, reconciliation | 30s |
| [helioscraper](./projects/helioscraper/) | Selenium, Pydantic | Configurable web scraper with rotating agents | 45s |
| [order-processing-automation](./projects/order-processing-automation/) | FastAPI, Celery, Redis | Async order pipeline with idempotency | 30s |
| [data-analysis-visualization-suite](./projects/data-analysis-visualization-suite/) | Streamlit, pandas, scikit-learn | Full analytics toolkit with forecasting | 60s |
| [api-docs-testing-framework](./projects/api-docs-testing-framework/) | FastAPI, pytest, GitHub Actions | Production API with comprehensive testing | 20s |
| [digital-inventory-management](./projects/digital-inventory-management/) | Tkinter, SQLite, scikit-learn | Restaurant inventory with forecasting GUI | 30s |

## Repository Structure

```
heliotheanalyst-portfolio-monorepo/
├── projects/                    # All portfolio projects
│   ├── shopify-integration-system/
│   ├── helioscraper/
│   ├── order-processing-automation/
│   ├── data-analysis-visualization-suite/
│   ├── api-docs-testing-framework/
│   └── digital-inventory-management/
├── docs/                        # Portfolio documentation
├── observability/               # Grafana dashboards & configs
├── scripts/                     # Shared automation scripts
├── Makefile                     # Common commands
├── pyproject.toml              # Monorepo tooling config
└── .pre-commit-config.yaml     # Code quality hooks
```

## Common Commands

```bash
# Setup everything
make setup

# Run specific project demo
make run-shopify        # Shopify integration demo
make run-helioscraper   # Web scraper demo
make run-orders         # Order processing demo
make run-analytics      # Data analysis suite (Streamlit)
make run-api-testing    # API testing framework
make run-inventory      # Inventory GUI (Tkinter)

# Run all demos
make run-all-demos      # Run all project demos sequentially

# Code quality
make lint               # Run ruff on all projects
make format             # Format all code
make typecheck          # Run mypy on all projects

# Testing
make test               # Run all tests
make test-cov           # Run tests with coverage report

# Docker services
make up                 # Start shared services (Postgres + Redis)
make down               # Stop all Docker services
make logs               # View Docker logs

# Utilities
make clean              # Clean all build artifacts
make ci                 # Run full CI check locally
```

## Observability (Optional)

Start Grafana for monitoring dashboards:

```bash
# Start Grafana dashboard
make up-observability

# Or manually:
docker compose --profile observability up -d

# Access Grafana at http://localhost:3000
# Default login: admin / admin
```

The observability stack includes a pre-configured "Portfolio Overview" dashboard for monitoring API metrics.

## Running Individual Projects

Each project has its own README with detailed instructions. All projects support **mock mode** - they run without real credentials using fixture data.

### Example: Shopify Integration

```bash
cd projects/shopify-integration-system
python scripts/run_demo.py  # Runs with mock adapters
```

To use real credentials:
```bash
cp .env.example .env
# Edit .env with your credentials
python scripts/run_demo.py --real-mode
```

## Architecture Standards

All projects follow consistent patterns:

- **src/ layout**: Clean separation of concerns
- **Layered architecture**: api/ → services/ → adapters/ → storage/
- **Type safety**: Full mypy coverage
- **Test coverage**: pytest with 80%+ threshold
- **Mock-first**: All demos run without real credentials
- **Docker support**: docker-compose.yml where services needed

## Requirements

- Python 3.11+
- Docker & Docker Compose (for services)
- Make (optional, for convenience commands)

## Portfolio Website Copy

See [docs/portfolio-projects.md](./docs/portfolio-projects.md) for website-ready project descriptions.

## License

MIT License - See individual project LICENSE files.

---

Built with by [HelioTheAnalyst](https://heliotheanalyst.co.uk)
