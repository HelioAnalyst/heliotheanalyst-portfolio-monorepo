# HelioScraper

Configurable web scraping framework with intelligent anti-detection and comprehensive reporting.

## Quickstart (3 Minutes)

```bash
# 1. Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Run demo (uses mock browser - no Chrome needed)
python scripts/run_demo.py

# 3. Run tests
pytest tests/ -v
```

## Architecture

### System Overview

```mermaid
graph TB
    subgraph Config["Configuration"]
        Y[YAML Site Configs]
    end

    subgraph Engine["Scraping Engine"]
        L[Loader]
        P[Parser]
        V[Validator]
        S[Storage]
    end

    subgraph AntiDetect["Anti-Detection"]
        UA[User Agent Rotation]
        DL[Delay Randomization]
        PX[Proxy Support]
        HC[Headless Chrome]
    end

    subgraph Output["Output"]
        CSV[CSV Files]
        SQL[SQLite/Postgres]
        RP[HTML Reports]
    end

    Y --> L
    L --> UA
    UA --> DL
    DL --> P
    P --> V
    V --> S
    S --> CSV
    S --> SQL
    S --> RP
```

### Scraping Pipeline

```mermaid
sequenceDiagram
    participant Config as YAML Config
    participant Scraper as Scraper Engine
    participant Browser as Selenium
    participant Site as Target Site
    participant Store as Data Store

    Config->>Scraper: Load site configuration
    Scraper->>Browser: Initialize driver
    loop For each page
        Scraper->>Browser: Navigate to URL
        Browser->>Site: HTTP GET
        Site-->>Browser: HTML response
        Scraper->>Browser: Extract elements
        Browser-->>Scraper: Raw data
        Scraper->>Scraper: Validate & transform
        Scraper->>Store: Save records
    end
    Scraper->>Scraper: Generate report
```

### Project Structure

```
src/
├── core/              # Core scraping engine
│   ├── scraper.py     # Main scraper class
│   ├── loader.py      # Page loader with anti-detection
│   ├── parser.py      # HTML parsing logic
│   └── validator.py   # Data validation
├── config/            # Configuration management
│   ├── loader.py      # YAML config loader
│   └── models.py      # Config Pydantic models
├── storage/           # Output handlers
│   ├── csv_exporter.py
│   ├── db_exporter.py
│   └── report_generator.py
├── adapters/          # Browser adapters
│   ├── selenium_adapter.py
│   └── mock_adapter.py
├── configs/           # Site configurations
│   └── sites/
│       ├── example.yml
│       └── books.yml
└── reports/           # Generated reports
```

## Features

- **YAML Configuration**: Define scraping rules in YAML files
- **Anti-Detection**: Rotating user agents, randomized delays, proxy support
- **Data Validation**: Pydantic models ensure data integrity
- **Multiple Outputs**: CSV, SQLite, PostgreSQL
- **Audit Reports**: HTML and Markdown reports with statistics
- **Selenium Grid**: Docker-based scaling support

## Demo Instructions

### Mock Mode (Default - No Browser Needed)

```bash
# Run the demo with mock browser
python scripts/run_demo.py
```

The demo will:
1. Load example site configurations
2. Scrape mock HTML pages
3. Extract product data
4. Export to CSV and SQLite
5. Generate HTML report

### Real Mode (With Chrome)

```bash
# Ensure Chrome is installed
# Install ChromeDriver
pip install webdriver-manager

# Run with real browser
python scripts/run_demo.py --real-mode
```

## Configuration

Site configs are stored in `configs/sites/`:

```yaml
# configs/sites/example.yml
name: "Example E-commerce Site"
base_url: "https://example.com"
category: "retail"

selectors:
  product_list: ".product-item"
  title: ".product-title"
  price: ".product-price"
  image: ".product-image img@src"
  description: ".product-description"
  
pagination:
  enabled: true
  selector: ".next-page"
  max_pages: 5

delays:
  min: 1.0
  max: 3.0

output:
  format: "csv"
  filename: "example_products.csv"
```

## API Examples

### Basic Usage

```python
from helioscraper import Scraper

# Load from config
scraper = Scraper.from_config("configs/sites/example.yml")

# Scrape all pages
results = scraper.scrape()
print(f"Scraped {len(results)} products")

# Export to CSV
scraper.export_csv("output.csv")

# Generate HTML report
scraper.generate_report("report.html")
```

### Advanced Usage

```python
from helioscraper import Scraper, Config

# Create config programmatically
config = Config(
    name="Custom Site",
    base_url="https://example.com",
    selectors={
        "product_list": ".product",
        "title": "h2",
        "price": ".price"
    },
    delays={"min": 2.0, "max": 5.0},
    pagination={"enabled": True, "max_pages": 10}
)

# Initialize scraper
scraper = Scraper(config)

# Scrape with callbacks
for product in scraper.scrape_iter():
    print(f"Found: {product.title} - ${product.price}")
    # Custom processing

# Multi-format export
scraper.export_csv("products.csv")
scraper.export_sqlite("products.db")
scraper.export_postgres("postgresql://user:pass@localhost/db")
```

### Report Generation

```python
from helioscraper.reports import ReportGenerator

# Generate comprehensive report
generator = ReportGenerator(scraper.results)
generator.generate_html(
    output_path="report.html",
    title="Scraping Report",
    include_charts=True
)

# Generate Markdown report
generator.generate_markdown(
    output_path="report.md",
    include_stats=True
)
```

## Environment Variables

```bash
# Selenium configuration
SELENIUM_HEADLESS=true
SELENIUM_TIMEOUT=30
SELENIUM_IMPLICIT_WAIT=10

# Proxy configuration (optional)
PROXY_URL=http://proxy.example.com:8080
PROXY_USERNAME=user
PROXY_PASSWORD=pass

# Database output (optional)
DATABASE_URL=postgresql://user:pass@localhost:5432/scraper

# Anti-detection
USER_AGENT_ROTATION=true
DELAY_RANDOMIZATION=true
```

## Implemented vs Planned

| Implemented | Planned |
|-------------|---------|
| ✅ Selenium scraper | 🔄 Playwright support |
| ✅ YAML configs | 🔄 Visual config builder |
| ✅ CSV/SQLite output | 🔄 S3/cloud storage |
| ✅ HTML reports | 🔄 Real-time monitoring |
| ✅ User agent rotation | 🔄 CAPTCHA solving |
| ✅ Delay randomization | 🔄 JavaScript rendering |
| ✅ Pagination support | 🔄 Distributed scraping |
| ✅ Data validation | 🔄 ML-based data extraction |

## Development

```bash
# Lint
ruff check src tests

# Format
ruff format src tests

# Type check
mypy src

# Test
pytest tests/ --cov=src --cov-report=html

# Run specific scraper
python -m helioscraper configs/sites/example.yml
```

## Docker

```bash
# Build scraper image
docker build -t helioscraper .

# Run with Selenium Grid
docker-compose up -d selenium-hub selenium-node

# Execute scraper
docker run --network=host helioscraper python scripts/run_demo.py
```

## Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires Chrome)
pytest tests/integration/ -v

# Mock tests (default)
pytest tests/ -v --mock-only
```

## License

MIT License
