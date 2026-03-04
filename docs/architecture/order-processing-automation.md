# Order Processing Automation - Architecture

## System Overview

The Order Processing Automation system is a fault-tolerant, asynchronous order pipeline that guarantees idempotent processing with intelligent provider routing.

## High-Level Architecture

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        Web["Web Application"]
        Mobile["Mobile App"]
        Webhook["Provider Webhooks"]
    end

    subgraph API["API Layer"]
        FastAPI["FastAPI Application"]
        Routes["Order Routes"]
        Middleware["Auth & Metrics"]
    end

    subgraph Queue["Task Queue"]
        Redis[(Redis Broker)]
        Celery["Celery Workers"]
        Flower["Flower Dashboard"]
    end

    subgraph Services["Service Layer"]
        OrderService["OrderService"]
        Router["Provider Router"]
        RetryHandler["Retry Handler"]
    end

    subgraph Providers["Fulfillment Providers"]
        ProviderA["Provider A (Premium)"]
        ProviderB["Provider B (Standard)"]
        Internal["Internal Fulfillment"]
    end

    subgraph Data["Data Layer"]
        Postgres[(PostgreSQL)]
    end

    Web --> FastAPI
    Mobile --> FastAPI
    Webhook --> FastAPI
    FastAPI --> Routes
    Routes --> Middleware
    Middleware --> OrderService
    OrderService --> Redis
    Redis --> Celery
    Celery --> Router
    Router --> ProviderA
    Router --> ProviderB
    Router --> Internal
    OrderService --> Postgres
    Celery --> Flower
```

## Order Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant OrderService
    participant DB as PostgreSQL
    participant Redis as Redis/Celery
    participant Worker as Celery Worker
    participant Provider as Fulfillment Provider

    Client->>API: POST /orders (with idempotency_key)
    API->>OrderService: create_order()
    OrderService->>DB: check_idempotency_key()
    alt Key exists
        DB-->>OrderService: Return existing order
        OrderService-->>API: Return existing order
    else New order
        OrderService->>DB: save_order()
        OrderService->>Redis: queue_for_processing()
        OrderService-->>API: Order created
    end
    API-->>Client: 201 Created

    Redis->>Worker: process_order(order_id)
    Worker->>OrderService: process_order()
    OrderService->>OrderService: select_provider()
    OrderService->>Provider: submit_order()
    Provider-->>OrderService: provider_order_id
    OrderService->>DB: update_status(completed)
```

## Provider Routing Logic

```mermaid
flowchart TD
    Start[New Order] --> CheckValue{Order Total}
    CheckValue -->|"> £500| ProviderA["Provider A<br/>Premium Fulfillment"]
    CheckValue -->|£100-500| ProviderB["Provider B<br/>Standard Fulfillment"]
    CheckValue -->|"< £100| Internal["Internal<br/>Fulfillment"]
    ProviderA --> Process[Process Order]
    ProviderB --> Process
    Internal --> Process
    Process --> Success{Success?}
    Success -->|Yes| Complete[Mark Complete]
    Success -->|No| Retry{Retry Count < 3?}
    Retry -->|Yes| Backoff[Exponential Backoff]
    Backoff --> Process
    Retry -->|No| Fail[Mark Failed]
```

## Idempotency Guarantee

```mermaid
flowchart TD
    Request[Incoming Request] --> Extract[Extract Idempotency Key]
    Extract --> Check{Key in DB?}
    Check -->|Yes| ReturnExisting[Return Existing Order]
    Check -->|No| Create[Create New Order]
    Create --> Store[Store with Key]
    Store --> ReturnNew[Return New Order]
    ReturnExisting --> End[End]
    ReturnNew --> End
```

## Retry Mechanism

```mermaid
flowchart TD
    Failure[Processing Failure] --> CheckCount{Retry Count?}
    CheckCount -->|0| FirstRetry[Wait 60s]
    CheckCount -->|1| SecondRetry[Wait 120s]
    CheckCount -->|2| ThirdRetry[Wait 240s]
    CheckCount -->|>=3| PermanentFail[Permanent Failure]
    FirstRetry --> Requeue[Requeue Task]
    SecondRetry --> Requeue
    ThirdRetry --> Requeue
    Requeue --> Celery[Celery Worker]
```

## Database Schema

```mermaid
erDiagram
    ORDER {
        string id PK
        string idempotency_key UK
        string customer_id
        string customer_email
        json items
        json shipping_address
        decimal subtotal
        decimal tax
        decimal shipping_cost
        decimal total
        string status
        string provider
        string provider_order_id
        int retry_count
        int max_retries
        string failure_reason
        datetime created_at
        datetime updated_at
    }

    STOCK_MOVEMENT {
        int id PK
        string order_id FK
        string item_sku
        string movement_type
        int quantity
        string reference
        datetime created_at
    }

    ORDER ||--o{ STOCK_MOVEMENT : has
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI |
| Task Queue | Celery |
| Message Broker | Redis |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Monitoring | Flower |
| Testing | pytest with async support |
| Deployment | Docker Compose |

## Key Design Decisions

1. **Idempotency Keys**: Ensure exactly-once processing even with client retries
2. **Async Task Queue**: Celery workers handle processing without blocking API
3. **Smart Routing**: Order value determines fulfillment provider
4. **Exponential Backoff**: Prevents overwhelming providers with retries
5. **Status Tracking**: Full visibility into order lifecycle
