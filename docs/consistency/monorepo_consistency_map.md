# Monorepo Consistency Map

Canonical reference for all portfolio projects to ensure consistency across website, GitHub, CV, and LinkedIn.

---

## Project 1: shopify-integration-system

| Field | Value |
|-------|-------|
| **Name** | Shopify Integration System |
| **One-liner** | Enterprise-grade e-commerce synchronisation with intelligent rate limiting and data reconciliation |
| **Tech Stack** | FastAPI, PostgreSQL, SQLAlchemy, Redis, Pydantic, pytest, Docker |
| **Core Features** | Bulk product sync, inventory reconciliation, order processing, rate limit handling, retry/backoff, mock adapters |
| **Demo Command** | `python scripts/run_demo.py` (mock mode, no credentials) |
| **Main Endpoints** | `POST /sync/products/bulk`, `POST /sync/inventory`, `POST /orders/process`, `GET /health`, `GET /metrics` |
| **Data Stores/Services** | PostgreSQL (transactional), Redis (caching/rate limiting), Docker Compose |
| **Test Coverage** | pytest with async support, mock adapters |
| **Demo Fixtures** | 10 mock products, 5 mock orders, inventory discrepancies for reconciliation demo |

---

## Project 2: helioscraper

| Field | Value |
|-------|-------|
| **Name** | HelioScraper |
| **One-liner** | Configurable web scraping framework with intelligent anti-detection and comprehensive reporting |
| **Tech Stack** | Selenium, Pydantic, BeautifulSoup, pandas, Jinja2, PyYAML, pytest |
| **Core Features** | YAML site configs, rotating user agents, randomized delays, data validation, CSV/SQLite output, HTML/Markdown reports |
| **Demo Command** | `python scripts/run_demo.py` (mock browser mode, no Chrome required) |
| **Main Endpoints** | CLI: `helioscraper --config <site>` |
| **Data Stores/Services** | SQLite (default), optional PostgreSQL |
| **Test Coverage** | pytest with mock browser |
| **Demo Fixtures** | Mock HTML generation, 5-10 items per page, 3 pages |

---

## Project 3: order-processing-automation

| Field | Value |
|-------|-------|
| **Name** | Order Processing Automation |
| **One-liner** | Asynchronous order pipeline with idempotency guarantees and intelligent provider routing |
| **Tech Stack** | FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, Pydantic, pytest, Docker |
| **Core Features** | Async processing, idempotency keys, job status tracking, provider routing rules, retry logic, webhook handlers |
| **Demo Command** | `python scripts/run_demo.py` |
| **Main Endpoints** | `POST /orders`, `GET /orders/{id}`, `POST /orders/{id}/process`, `GET /dashboard/metrics`, `POST /webhooks/provider-status`, `POST /orders/{id}/retry` |
| **Data Stores/Services** | PostgreSQL, Redis (broker), Celery workers, Flower (monitoring), Docker Compose |
| **Test Coverage** | pytest with async support |
| **Demo Fixtures** | 5 sample orders with varying totals for provider routing demo |

---

## Project 4: data-analysis-visualization-suite

| Field | Value |
|-------|-------|
| **Name** | Data Analysis & Visualization Suite |
| **One-liner** | End-to-end analytics toolkit with automated insights and forecasting capabilities |
| **Tech Stack** | Streamlit, pandas, NumPy, scikit-learn, SciPy, Matplotlib, Seaborn, Plotly, ReportLab, OpenPyXL |
| **Core Features** | Data ingestion (CSV/Excel), automated cleaning, statistical analysis, anomaly detection, time series forecasting, PDF/Excel report generation |
| **Demo Command** | `python scripts/run_demo.py` or `streamlit run src/app.py` |
| **Main Endpoints** | Streamlit UI: Upload, Cleaning, Analysis, Anomalies, Forecast, Export Report |
| **Data Stores/Services** | File-based (CSV, Excel, SQLite) |
| **Test Coverage** | pytest for modules |
| **Demo Fixtures** | 500-row sample dataset with sales, categories, dates |

---

## Project 5: api-docs-testing-framework

| Field | Value |
|-------|-------|
| **Name** | API Docs & Testing Framework |
| **One-liner** | Production-ready API with comprehensive documentation and automated testing pipeline |
| **Tech Stack** | FastAPI, Pydantic, pytest, pytest-cov, Prometheus, GitHub Actions, Docker |
| **Core Features** | Auto-generated OpenAPI docs, comprehensive test suite (unit/integration), 80%+ coverage enforcement, request timing middleware, Prometheus metrics, CI/CD pipeline |
| **Demo Command** | `python scripts/run_demo.py` |
| **Main Endpoints** | `GET /health`, `GET /ready`, `GET /metrics`, `GET/POST /users`, `GET/PUT/DELETE /users/{id}`, `GET/POST /items`, `GET/PUT/DELETE /items/{id}` |
| **Data Stores/Services** | In-memory (demo), optional PostgreSQL |
| **Test Coverage** | pytest with 80%+ threshold, coverage reporting |
| **Demo Fixtures** | 3 sample users, 3 sample items |

---

## Project 6: digital-inventory-management

| Field | Value |
|-------|-------|
| **Name** | Digital Inventory Management |
| **One-liner** | Desktop inventory system with demand forecasting for restaurant operations |
| **Tech Stack** | Tkinter, SQLite, pandas, scikit-learn, Matplotlib |
| **Core Features** | Stock management, movement tracking, expiration alerts, waste tracking, reorder alerts, demand forecasting, barcode scan simulation |
| **Demo Command** | `python scripts/run_demo.py` or `python src/main.py` for GUI |
| **Main Endpoints** | Tkinter GUI: Inventory view, Add Item, Stock In/Out, Forecast, Reports |
| **Data Stores/Services** | SQLite (default), optional PostgreSQL |
| **Test Coverage** | pytest for database and forecaster |
| **Demo Fixtures** | 10 sample inventory items (flour, sugar, oil, rice, etc.) |

---

## Terminology Standards

### Technology Names (use exactly)
- FastAPI (not Fastapi)
- PostgreSQL (not Postgres)
- SQLAlchemy (not SQL-Alchemy)
- Redis (not redis)
- Celery (not celery)
- Pydantic (not pydantic)
- pytest (not Pytest)
- Streamlit (not streamlit)
- Tkinter (not tkinter)
- scikit-learn (not sklearn)

### Architecture Terms
- Use "async" not "asynchronous"
- Use "idempotency" not "idempotent keys"
- Use "rate limiting" not "rate-limiting"
- Use "mock mode" not "demo mode"

### Metrics Guidelines
- Only claim metrics that are measured in code
- Use "handles X records in demo fixtures" for unmeasured scale
- Use "estimated" for projections
- Use "demonstrated" for actual observed behaviour
