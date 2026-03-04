# Order Processing Automation

Asynchronous order pipeline with idempotency guarantees and intelligent provider routing.

## Quickstart (3 Minutes)

```bash
# 1. Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Start services (Postgres + Redis)
docker-compose up -d

# 3. Run demo
python scripts/run_demo.py

# 4. Run tests
pytest tests/ -v
```

## Architecture

### System Overview

```mermaid
graph TB
    subgraph Input["Order Input"]
        API[API Endpoint]
        WH[Webhooks]
    end

    subgraph Queue["Task Queue"]
        RD[(Redis)]
        CW[Celery Workers]
    end

    subgraph Routing["Provider Routing"]
        RL[Router Logic]
        P1[Provider A]
        P2[Provider B]
        P3[Provider C]
    end

    subgraph Storage["Storage"]
        PG[(PostgreSQL)]
    end

    API --> RD
    WH --> RD
    RD --> CW
    CW --> RL
    RL --> P1
    RL --> P2
    RL --> P3
    CW --> PG
```

### Order Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Task as Celery Task
    participant Router as Provider Router
    participant Provider as Fulfillment Provider
    participant DB as PostgreSQL

    Client->>API: POST /orders
    API->>DB: Create order record
    API->>Task: Submit async task
    API-->>Client: 202 Accepted + order_id
    
    Task->>Router: Select provider
    Router-->>Task: provider_id
    Task->>Provider: Submit fulfillment
    Provider-->>Task: confirmation
    Task->>DB: Update status
    
    alt Webhook notification
        Provider->>API: POST /webhooks/status
        API->>DB: Update order status
    end
```

### Idempotency Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Layer
    participant IDM as Idempotency Manager
    participant Redis as Redis Cache
    participant DB as Database

    Client->>API: POST /orders (Idempotency-Key: abc123)
    API->>IDM: Check key
    IDM->>Redis: GET idempotency:abc123
    
    alt Key exists
        Redis-->>IDM: Cached response
        IDM-->>API: Return cached
        API-->>Client: 200 OK (cached)
    else New key
        Redis-->>IDM: Not found
        IDM->>DB: Process order
        DB-->>IDM: Result
        IDM->>Redis: SET idempotency:abc123
        IDM-->>API: Result
        API-->>Client: 201 Created
    end
```

### Project Structure

```
src/
├── api/               # FastAPI application
│   ├── main.py        # App entry point
│   ├── routes.py      # API endpoints
│   └── dependencies.py
├── domain/            # Domain models
│   ├── models.py      # Order, Provider models
│   └── events.py      # Domain events
├── services/          # Business logic
│   ├── order_service.py
│   ├── provider_router.py
│   └── idempotency.py
├── tasks/             # Celery tasks
│   └── order_tasks.py
├── adapters/          # Provider integrations
│   ├── provider_a.py
│   ├── provider_b.py
│   └── mock_providers.py
└── storage/           # Database
    ├── database.py
    └── repositories.py
```

## Features

- **Async Processing**: Celery workers for scalable order handling
- **Idempotency**: Guaranteed exactly-once processing with idempotency keys
- **Job Tracking**: Real-time status updates via API and webhooks
- **Provider Routing**: Rule-based order distribution with fallback
- **Failure Recovery**: Automatic retry with exponential backoff
- **Webhook Integration**: Provider status update handling

## Demo Instructions

### Mock Mode (Default)

```bash
# Run the demo with mock providers
python scripts/run_demo.py
```

The demo will:
1. Submit sample orders via API
2. Route orders to mock providers
3. Show async processing with Celery
4. Display idempotency in action
5. Generate processing metrics

### With Flower (Task Monitoring)

```bash
# Start Flower for Celery monitoring
docker-compose up -d flower

# Open Flower dashboard
open http://localhost:5555

# Run demo
python scripts/run_demo.py
```

## API Examples

### Submit Order

**Request:**
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{
    "customer_id": "cust-001",
    "items": [
      {"sku": "SKU-001", "quantity": 2, "price": 29.99},
      {"sku": "SKU-002", "quantity": 1, "price": 49.99}
    ],
    "shipping_address": {
      "name": "John Doe",
      "line1": "123 Main St",
      "city": "New York",
      "postcode": "10001"
    },
    "preferred_provider": "provider_a"
  }'
```

**Response:**
```json
{
  "order_id": "ord-abc123",
  "status": "pending",
  "total": 109.97,
  "currency": "GBP",
  "idempotency_key": "unique-key-123",
  "submitted_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T11:30:00Z"
}
```

### Get Order Status

**Request:**
```bash
curl http://localhost:8000/orders/ord-abc123
```

**Response:**
```json
{
  "order_id": "ord-abc123",
  "status": "processing",
  "provider": "provider_a",
  "provider_order_id": "pa-789",
  "tracking_number": null,
  "history": [
    {"status": "pending", "timestamp": "2024-01-15T10:30:00Z"},
    {"status": "processing", "timestamp": "2024-01-15T10:31:15Z"}
  ],
  "updated_at": "2024-01-15T10:31:15Z"
}
```

### Process Order Manually

**Request:**
```bash
curl -X POST http://localhost:8000/orders/ord-abc123/process \
  -H "Content-Type: application/json" \
  -d '{"provider": "provider_b"}'
```

**Response:**
```json
{
  "order_id": "ord-abc123",
  "status": "processing",
  "provider": "provider_b",
  "message": "Order manually routed to provider_b"
}
```

### Get Dashboard Metrics

**Request:**
```bash
curl http://localhost:8000/dashboard/metrics
```

**Response:**
```json
{
  "period": "24h",
  "orders": {
    "total": 150,
    "pending": 10,
    "processing": 25,
    "completed": 110,
    "failed": 5
  },
  "providers": {
    "provider_a": {"orders": 80, "avg_time": 45},
    "provider_b": {"orders": 70, "avg_time": 52}
  },
  "average_processing_time": 48
}
```

### Webhook Handler

**Request (from provider):**
```bash
curl -X POST http://localhost:8000/webhooks/provider-status \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "provider_a",
    "provider_order_id": "pa-789",
    "status": "shipped",
    "tracking_number": "1Z999AA1234567890",
    "timestamp": "2024-01-15T11:00:00Z"
  }'
```

**Response:**
```json
{
  "received": true,
  "order_id": "ord-abc123",
  "new_status": "shipped"
}
```

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/order_processing

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Provider API keys (optional - mock mode works without)
PROVIDER_A_API_KEY=your_key
PROVIDER_B_API_KEY=your_key
PROVIDER_C_API_KEY=your_key

# Webhook
WEBHOOK_SECRET=your_webhook_secret
```

## Implemented vs Planned

| Implemented | Planned |
|-------------|---------|
| ✅ Async order processing | 🔄 Saga pattern implementation |
| ✅ Idempotency keys | 🔄 Multi-region deployment |
| ✅ Provider routing | 🔄 ML-based provider selection |
| ✅ Retry logic | 🔄 Dead letter queue |
| ✅ Webhook handlers | 🔄 Event sourcing |
| ✅ Celery integration | 🔄 Kubernetes operators |
| ✅ Dashboard metrics | 🔄 Real-time notifications |
| ✅ Manual processing | 🔄 Automatic reconciliation |

## Development

```bash
# Start services
docker-compose up -d postgres redis

# Run worker (terminal 1)
celery -A src.tasks worker --loglevel=info

# Run API (terminal 2)
uvicorn src.api.main:app --reload

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f worker
docker-compose logs -f api

# Scale workers
docker-compose up -d --scale worker=3
```

## Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Load testing (requires running API)
locust -f tests/load/locustfile.py
```

## License

MIT License
