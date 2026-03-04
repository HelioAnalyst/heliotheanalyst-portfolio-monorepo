# HelioScraper Pipeline - Architecture

## System Overview

HelioScraper is a configuration-driven web scraping framework with anti-detection measures, data validation, and comprehensive reporting.

## High-Level Architecture

```mermaid
flowchart TB
    subgraph Config["Configuration"]
        YAML["YAML Site Configs"]
        Selectors["CSS Selectors"]
        Pagination["Pagination Rules"]
    end

    subgraph Core["Core Pipeline"]
        Loader["ConfigLoader"]
        Scraper["Scraper Engine"]
        Browser["Browser Manager"]
    end

    subgraph Extraction["Extraction"]
        Fetch["HTTP Fetch"]
        Parse["HTML Parsing"]
        Validate["Pydantic Validation"]
    end

    subgraph Output["Output"]
        CSV["CSV Export"]
        SQLite["SQLite Database"]
        HTML["HTML Report"]
        Markdown["Markdown Report"]
    end

    YAML --> Loader
    Loader --> Scraper
    Scraper --> Browser
    Browser --> Fetch
    Fetch --> Parse
    Parse --> Validate
    Validate --> CSV
    Validate --> SQLite
    Validate --> HTML
    Validate --> Markdown
```

## Scraping Pipeline Flow

```mermaid
sequenceDiagram
    participant User
    participant Config as ConfigLoader
    participant Scraper as Scraper Engine
    participant Browser as BrowserManager
    participant Parser as BeautifulSoup
    participant Validator as Pydantic
    participant Output as Output Writers

    User->>Config: load_config(site_name)
    Config-->>User: SiteConfig
    User->>Scraper: Scraper(config)
    User->>Scraper: scrape()

    loop For each page
        Scraper->>Browser: get(url)
        Browser->>Browser: random_delay()
        Browser-->>Scraper: page_source
        Scraper->>Parser: parse(html)
        Parser-->>Scraper: soup
        Scraper->>Scraper: extract_items(soup)
        loop For each item
            Scraper->>Validator: ScrapedItem(**data)
            Validator-->>Scraper: validated_item
        end
        Scraper->>Scraper: next_page()
    end

    Scraper->>Output: export_csv()
    Scraper->>Output: export_sqlite()
    Scraper->>Output: generate_report()
```

## Anti-Detection Strategy

```mermaid
flowchart LR
    subgraph AntiDetection["Anti-Detection Measures"]
        UA["User Agent Rotation"]
        Delays["Random Delays"]
        ChromeFlags["Chrome Flags"]
        CDP["CDP Commands"]
    end

    subgraph Pool["User Agent Pool"]
        Chrome["Chrome/Windows"]
        Firefox["Firefox/Mac"]
        Safari["Safari/Mac"]
        Edge["Edge/Windows"]
    end

    Pool --> UA
    UA --> Request[HTTP Request]
    Delays --> Request
    ChromeFlags --> Browser[Browser Instance]
    CDP --> Browser
```

## Configuration Structure

```mermaid
flowchart TD
    SiteConfig["SiteConfig"] --> Base["base_url"]
    SiteConfig --> Selectors["selectors"]
    SiteConfig --> Pagination["pagination"]
    SiteConfig --> Delays["delays"]

    Selectors --> ProductList["product_list"]
    Selectors --> Title["title"]
    Selectors --> Price["price"]
    Selectors --> Image["image"]
    Selectors --> Link["link"]

    Pagination --> Enabled["enabled"]
    Pagination --> Selector["selector"]
    Pagination --> MaxPages["max_pages"]

    Delays --> Min["min"]
    Delays --> Max["max"]
```

## Data Validation Flow

```mermaid
flowchart TD
    Raw[Raw Extracted Data] --> Parse[Parse Fields]
    Parse --> Price{Price Field?}
    Price -->|Yes| ExtractPrice[Extract Numeric Price]
    Price -->|No| SkipPrice
    ExtractPrice --> CreateModel
    SkipPrice --> CreateModel
    CreateModel[Create ScrapedItem] --> Validate{Valid?}
    Validate -->|Yes| Store[Store in Results]
    Validate -->|No| LogError[Log Validation Error]
```

## Report Generation Pipeline

```mermaid
flowchart TB
    Results[Scraping Results] --> ReportGen["ReportGenerator"]

    ReportGen --> Stats["Calculate Statistics"]
    Stats --> Total["Total Items"]
    Stats --> Duration["Duration"]
    Stats --> Errors["Error Count"]

    ReportGen --> HTMLTemplate["HTML Template"]
    ReportGen --> MarkdownTemplate["Markdown Template"]

    HTMLTemplate --> HTMLReport["HTML Report"]
    MarkdownTemplate --> MDReport["Markdown Report"]

    HTMLReport --> StyledOutput["Styled Dashboard"]
    MDReport --> GitHubFriendly["GitHub-Friendly MD"]
```

## Mock Mode Architecture

```mermaid
flowchart TB
    subgraph Real["Real Mode"]
        Selenium["Selenium WebDriver"]
        Chrome["Chrome Browser"]
        Network["Network Requests"]
    end

    subgraph Mock["Mock Mode"]
        MockBrowser["MockBrowserManager"]
        HTMLGen["HTML Generator"]
        Fixtures["Fixture Data"]
    end

    Scraper["Scraper"] -->|use_mock=True| Mock
    Scraper -->|use_mock=False| Real

    MockBrowser --> HTMLGen
    HTMLGen --> Fixtures
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Browser | Selenium 4.x |
| Parsing | BeautifulSoup 4, lxml |
| Validation | Pydantic 2.x |
| Data | pandas |
| Reports | Jinja2 |
| Config | PyYAML |
| Testing | pytest |

## Key Design Decisions

1. **YAML Configuration**: Site rules without code changes
2. **Anti-Detection**: Multiple strategies to avoid blocking
3. **Data Validation**: Pydantic ensures quality at extraction time
4. **Mock Mode**: Test without browser for rapid development
5. **Multiple Outputs**: CSV, SQLite, and reports for flexibility
