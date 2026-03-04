# Shopify Integration System - Architecture

## System Overview

The Shopify Integration System is a production-grade e-commerce synchronisation platform that connects Shopify storefronts with Business Central 365 ERP systems.

## High-Level Architecture

```mermaid
flowchart TB
    subgraph External["External Systems"]
        Shopify["Shopify API"]
        BC365["Business Central 365"]
    end

    subgraph Integration["Integration Layer"]
        API["FastAPI Application"]
        Services["Sync Services"]
        Adapters["API Adapters"]
    end

    subgraph Data["Data Layer"]
        Postgres[(PostgreSQL)]
        Redis[(Redis Cache)]
    end

    subgraph Monitoring["Monitoring"]
        Prometheus["Prometheus Metrics"]
        Health["Health Checks"]
    end

    Shopify <--> Adapters
    BC365 <--> Adapters
    Adapters --> Services
    Services --> API
    API --> Postgres
    API --> Redis
    API --> Prometheus
    API --> Health
```

## Component Architecture

```mermaid
flowchart TB
    subgraph API["API Layer (FastAPI)"]
        Routes["/sync/* Routes"]
        Middleware["Request Middleware"]
        Models["Pydantic Models"]
    end

    subgraph Service["Service Layer"]
        SyncService["SyncService"]
        RetryHandler["Retry Handler"]
        RateLimiter["Rate Limiter"]
    end

    subgraph Adapter["Adapter Layer"]
        ShopifyAdapter["ShopifyAdapter"]
        BC365Adapter["BC365Adapter"]
        MockShopify["MockShopifyAdapter"]
        MockBC365["MockBC365Adapter"]
    end

    subgraph Storage["Storage Layer"]
        DBRepo["DatabaseRepository"]
        CacheRepo["CacheRepository"]
    end

    Routes --> Middleware
    Middleware --> SyncService
    SyncService --> RetryHandler
    SyncService --> RateLimiter
    SyncService --> ShopifyAdapter
    SyncService --> BC365Adapter
    SyncService --> MockShopify
    SyncService --> MockBC365
    SyncService --> DBRepo
    SyncService --> CacheRepo
```

## Data Flow - Product Sync

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Service as SyncService
    participant Shopify as ShopifyAdapter
    participant BC365 as BC365Adapter
    participant DB as PostgreSQL

    Client->>API: POST /sync/products/bulk
    API->>Service: sync_products_bulk()
    Service->>Shopify: get_products()
    Shopify-->>Service: List[Product]
    loop For each product
        Service->>BC365: sync_product(product)
        BC365-->>Service: Success/Failure
    end
    Service->>DB: log_sync_result()
    Service-->>API: SyncResult
    API-->>Client: JSON Response
```

## Data Flow - Inventory Reconciliation

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Service as SyncService
    participant Shopify as ShopifyAdapter
    participant BC365 as BC365Adapter
    participant DB as PostgreSQL

    Client->>API: POST /sync/inventory
    API->>Service: sync_inventory()
    par Fetch from both systems
        Service->>Shopify: get_inventory_items()
        Shopify-->>Service: List[InventoryItem]
    and
        Service->>BC365: get_inventory()
        BC365-->>Service: List[InventoryItem]
    end
    Service->>Service: compare_inventory()
    Service->>Service: resolve_discrepancies()
    Service->>DB: log_reconciliation()
    Service-->>API: ReconciliationResult
    API-->>Client: JSON Response
```

## Rate Limiting Strategy

```mermaid
flowchart LR
    subgraph RateLimit["Rate Limiting"]
        Semaphore["Async Semaphore"]
        Counter["Request Counter"]
        Timer["Rate Window Timer"]
    end

    Request[Incoming Request] --> Semaphore
    Semaphore --> Counter
    Counter --> Timer
    Timer -->|Within limit| API[Process Request]
    Timer -->|Limit exceeded| Backoff[Exponential Backoff]
    Backoff --> Semaphore
```

## Retry Logic Flow

```mermaid
flowchart TD
    Start[API Call] --> Attempt{Attempt < Max?}
    Attempt -->|Yes| Execute[Execute Request]
    Attempt -->|No| Fail[Permanent Failure]
    Execute --> Success{Success?}
    Success -->|Yes| Return[Return Result]
    Success -->|No| RateLimit{Rate Limit?}
    RateLimit -->|Yes| Backoff[Calculate Backoff]
    RateLimit -->|No| Error[Other Error]
    Backoff --> Wait[Wait]
    Wait --> Attempt
    Error --> Retryable{Retryable?}
    Retryable -->|Yes| Backoff
    Retryable -->|No| Fail
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Cache | Redis 7 |
| Validation | Pydantic 2.x |
| Testing | pytest with async support |
| Deployment | Docker Compose |

## Key Design Decisions

1. **Adapter Pattern**: Abstracts external APIs for testability and future provider changes
2. **Mock Adapters**: Enable full offline development without credentials
3. **Async Throughout**: All I/O operations are async for performance
4. **Retry with Backoff**: Exponential backoff prevents overwhelming external APIs
5. **Idempotent Operations**: Sync operations can be safely retried
