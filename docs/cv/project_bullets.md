# CV Project Bullets

Three action-oriented bullets per project, following the pattern: **Action + Technology + Outcome**

---

## Shopify Integration System

- Architected and built a FastAPI-based e-commerce integration platform handling Shopify-to-ERP synchronisation with automatic rate limiting and exponential backoff retry logic
- Implemented automated inventory reconciliation detecting SKU-level discrepancies between systems, reducing manual reconciliation effort
- Designed mock adapter pattern enabling full offline development and testing without production credentials

**Tech keywords for ATS**: FastAPI, PostgreSQL, Redis, SQLAlchemy, Pydantic, Docker, API integration, rate limiting, retry logic

---

## HelioScraper

- Developed a YAML-configurable web scraping framework using Selenium with rotating user agents and randomized delays to avoid anti-bot detection
- Implemented Pydantic data validation ensuring extracted data quality with immediate error detection
- Generated automated HTML/Markdown audit reports providing extraction statistics and traceability

**Tech keywords for ATS**: Python, Selenium, Web Scraping, Pydantic, BeautifulSoup, pandas, Data Extraction

---

## Order Processing Automation

- Architected an asynchronous order processing pipeline using FastAPI and Celery with idempotency guarantees preventing duplicate order creation
- Implemented intelligent provider routing based on order value, distributing load across premium and standard fulfillment partners
- Built automatic retry mechanism with exponential backoff and dashboard metrics for operational visibility

**Tech keywords for ATS**: FastAPI, Celery, Redis, PostgreSQL, Async Processing, Distributed Systems, Idempotency

---

## Data Analysis & Visualisation Suite

- Developed a modular analytics toolkit using Streamlit, pandas, and scikit-learn automating data cleaning, anomaly detection, and time series forecasting
- Implemented multiple anomaly detection methods (Z-score, Isolation Forest, LOF) identifying outliers in 500-record demo datasets
- Generated automated PDF, Excel, and Markdown reports reducing manual reporting effort

**Tech keywords for ATS**: Python, Streamlit, pandas, scikit-learn, Machine Learning, Data Analysis, Time Series Forecasting

---

## API Docs & Testing Framework

- Built a reference FastAPI implementation with auto-generated OpenAPI documentation and comprehensive pytest suite enforcing 80%+ coverage
- Implemented request timing middleware with Prometheus metrics export for operational monitoring
- Designed GitHub Actions CI/CD pipeline with automated linting, type checking, testing, and Docker build verification

**Tech keywords for ATS**: FastAPI, pytest, CI/CD, GitHub Actions, Docker, Prometheus, API Development, Test Coverage

---

## Digital Inventory Management

- Developed a Tkinter-based desktop inventory management application with SQLite storage and demand forecasting for restaurant operations
- Implemented demand prediction using scikit-learn Linear Regression calculating optimal reorder points with safety stock
- Designed barcode scan simulation and CSV export functionality for operational efficiency

**Tech keywords for ATS**: Python, Tkinter, SQLite, scikit-learn, Inventory Management, Desktop Application, Forecasting

---

## Usage Tips

### For Technical CVs
Include all 3 bullets per project under a "Technical Projects" section.

### For Concise CVs
Select 1-2 strongest bullets per project, or pick 3 projects total with full bullets.

### For Cover Letters
Pick 1-2 projects most relevant to the role and expand with context about problem/solution.

### Ordering
Order projects by relevance to target role:
- **Backend/API roles**: Shopify Integration → Order Processing → API Testing → others
- **Data/ML roles**: Data Analysis Suite → HelioScraper → Digital Inventory → others
- **Full-stack roles**: Order Processing → API Testing → Data Analysis Suite → others
