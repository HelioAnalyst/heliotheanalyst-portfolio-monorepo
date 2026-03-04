# README Alignment Checklist

Use this checklist to ensure project READMEs match website content exactly.

---

## General Alignment Rules

1. **Project names must match exactly** across all files
2. **Tech stack lists must be identical** (same order, same spelling)
3. **Demo commands must be copy-paste identical**
4. **Feature lists must contain the same items** (wording can vary slightly)
5. **Implemented vs Planned tables must be identical**

---

## Project 1: shopify-integration-system

### README Checklist
- [ ] One-liner matches: "Enterprise-grade e-commerce synchronisation with intelligent rate limiting and data reconciliation"
- [ ] Tech stack includes: FastAPI, PostgreSQL, SQLAlchemy, Redis, Pydantic, pytest, Docker
- [ ] Demo command is: `python scripts/run_demo.py`
- [ ] Endpoints listed: `/sync/products/bulk`, `/sync/inventory`, `/orders/process`, `/health`, `/metrics`
- [ ] Services mentioned: PostgreSQL, Redis
- [ ] Implemented vs Planned table matches website exactly

### Website Alignment
- [ ] `docs/website/projects.json` hero_summary matches README
- [ ] `docs/website/projects/shopify-integration-system.md` tech_stack matches README
- [ ] All 6 features in "Key Features (Implemented)" appear in README

---

## Project 2: helioscraper

### README Checklist
- [ ] One-liner matches: "Configurable web scraping framework with intelligent anti-detection and comprehensive reporting"
- [ ] Tech stack includes: Selenium, Pydantic, BeautifulSoup, pandas, Jinja2, PyYAML, pytest
- [ ] Demo command is: `python scripts/run_demo.py`
- [ ] Outputs mentioned: CSV, SQLite, HTML reports, Markdown reports
- [ ] Mock mode mentioned: "no Chrome needed"
- [ ] Implemented vs Planned table matches website exactly

### Website Alignment
- [ ] `docs/website/projects.json` hero_summary matches README
- [ ] `docs/website/projects/helioscraper.md` tech_stack matches README
- [ ] All 8 features in "Key Features (Implemented)" appear in README

---

## Project 3: order-processing-automation

### README Checklist
- [ ] One-liner matches: "Asynchronous order pipeline with idempotency guarantees and intelligent provider routing"
- [ ] Tech stack includes: FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, Pydantic, pytest, Docker
- [ ] Demo command is: `python scripts/run_demo.py`
- [ ] Endpoints listed: `/orders`, `/orders/{id}`, `/orders/{id}/process`, `/dashboard/metrics`, `/webhooks/provider-status`
- [ ] Services mentioned: PostgreSQL, Redis, Celery
- [ ] Implemented vs Planned table matches website exactly

### Website Alignment
- [ ] `docs/website/projects.json` hero_summary matches README
- [ ] `docs/website/projects/order-processing-automation.md` tech_stack matches README
- [ ] All 8 features in "Key Features (Implemented)" appear in README

---

## Project 4: data-analysis-visualization-suite

### README Checklist
- [ ] One-liner matches: "End-to-end analytics toolkit with automated insights and forecasting capabilities"
- [ ] Tech stack includes: Streamlit, pandas, NumPy, scikit-learn, SciPy, Matplotlib, Seaborn, Plotly, ReportLab, OpenPyXL
- [ ] Demo commands are: `python scripts/run_demo.py` AND `streamlit run src/app.py`
- [ ] Modules mentioned: ingest, clean, analyze, anomaly, predict, viz, report
- [ ] Outputs mentioned: PDF reports, Excel reports
- [ ] Implemented vs Planned table matches website exactly

### Website Alignment
- [ ] `docs/website/projects.json` hero_summary matches README
- [ ] `docs/website/projects/data-analysis-visualization-suite.md` tech_stack matches README
- [ ] All 9 features in "Key Features (Implemented)" appear in README

---

## Project 5: api-docs-testing-framework

### README Checklist
- [ ] One-liner matches: "Production-ready API with comprehensive documentation and automated testing pipeline"
- [ ] Tech stack includes: FastAPI, Pydantic, pytest, pytest-cov, Prometheus, GitHub Actions, Docker
- [ ] Demo command is: `python scripts/run_demo.py`
- [ ] Endpoints listed: `/health`, `/ready`, `/metrics`, `/users`, `/items` (CRUD)
- [ ] Coverage threshold mentioned: 80%+
- [ ] CI/CD mentioned: GitHub Actions
- [ ] Implemented vs Planned table matches website exactly

### Website Alignment
- [ ] `docs/website/projects.json` hero_summary matches README
- [ ] `docs/website/projects/api-docs-testing-framework.md` tech_stack matches README
- [ ] All 8 features in "Key Features (Implemented)" appear in README

---

## Project 6: digital-inventory-management

### README Checklist
- [ ] One-liner matches: "Desktop inventory system with demand forecasting for restaurant operations"
- [ ] Tech stack includes: Tkinter, SQLite, pandas, scikit-learn, Matplotlib
- [ ] Demo commands are: `python scripts/run_demo.py` AND `python src/main.py`
- [ ] Features mentioned: items, stock movements, expirations, waste tracking, reorder alerts, forecasting
- [ ] Barcode scanning mentioned: "simulated"
- [ ] Implemented vs Planned table matches website exactly

### Website Alignment
- [ ] `docs/website/projects.json` hero_summary matches README
- [ ] `docs/website/projects/digital-inventory-management.md` tech_stack matches README
- [ ] All 8 features in "Key Features (Implemented)" appear in README

---

## Terminology Consistency

### Must Use Exactly (Case-Sensitive)
| Term | Incorrect Variants |
|------|-------------------|
| FastAPI | Fastapi, fastapi |
| PostgreSQL | Postgres, postgres, POSTGRES |
| SQLAlchemy | SQL-Alchemy, sqlalchemy |
| Redis | redis, REDIS |
| Celery | celery, CELERY |
| Pydantic | pydantic, PYDANTIC |
| pytest | Pytest, PYTEST |
| Streamlit | streamlit, STREAMLIT |
| Tkinter | tkinter, TKINTER |
| scikit-learn | sklearn, Scikit-Learn |

### Phrasing Standards
| Use | Instead of |
|-----|-----------|
| mock mode | demo mode, test mode |
| idempotency | idempotent, duplicate prevention |
| rate limiting | rate-limiting, throttling |
| 80%+ coverage | 80 percent coverage, high coverage |

---

## Quick Verification Script

Run this to check for inconsistencies:

```bash
# Check project names
grep -r "Shopify Integration" docs/website/ projects/shopify-integration-system/README.md
grep -r "HelioScraper" docs/website/ projects/helioscraper/README.md
grep -r "Order Processing Automation" docs/website/ projects/order-processing-automation/README.md
grep -r "Data Analysis & Visualization" docs/website/ projects/data-analysis-visualization-suite/README.md
grep -r "API Docs & Testing" docs/website/ projects/api-docs-testing-framework/README.md
grep -r "Digital Inventory Management" docs/website/ projects/digital-inventory-management/README.md

# Check tech stack consistency
grep -i "fastapi" docs/website/projects.json projects/*/README.md
grep -i "postgresql" docs/website/projects.json projects/*/README.md
grep -i "redis" docs/website/projects.json projects/*/README.md
```
