# Shopify Integration System

Enterprise-grade e-commerce synchronization platform connecting Shopify with Business Central 365.

## Quickstart (3 Minutes)

```bash
# 1. Setup (creates venv, installs deps)
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Start services (Postgres + Redis)
docker-compose up -d

# 3. Run demo (mock mode - no credentials needed)
python scripts/run_demo.py

# 4. Run tests
pytest tests/ -v
```

## Architecture

### System Overview

```mermaid
graph TB
    subgraph External["External Systems"]
        S[Shopify API]
        BC[Business Central 365]
    end

    subgraph API["FastAPI Application"]
        R[Routes]
        M[Middleware]
        D[Domain Models]
        SV[Services]
    end

    subgraph Adapters["Adapters"]
        SA[Shopify Adapter]
        BA[BC365 Adapter]
        MA[Mock Adapters]
    end

    subgraph Storage["Storage"]
        PG[(PostgreSQL)]
        RD[(Redis Cache)]
    end

    S <--> SA
    BC <--> BA
    R <--> M
    M <--> SV
    SV <--> D
    SV <--> SA
    SV <--> BA
    SA <--> MA
    BA <--> MA
    SV <--> PG
    SV <--> RD
```

### Data Flow - Product Sync

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Service as Sync Service
    participant Shopify as Shopify Adapter
    participant BC as BC365 Adapter
    participant DB as PostgreSQL

    Client->>API: POST /sync/products/bulk
    API->>Service: sync_products_bulk()
    Service->>Shopify: fetch_products()
    Shopify-->>Service: products[]
    Service->>BC: create_or_update_products()
    BC-->>Service: results[]
    Service->>DB: log_sync_operation()
    Service-->>API: sync_results
    API-->>Client: 200 OK + results
```

### Project Structure

```
src/
├── api/           # FastAPI routes and middleware
│   ├── routes.py      # API endpoints
│   └── middleware.py  # Logging, timing, error handling
├── domain/        # Pydantic models and business logic
│   ├── models.py      # Product, Order, Inventory models
│   └── events.py      # Domain events
├── services/      # Core business services
│   ├── sync.py        # Synchronization logic
│   └── reconciliation.py  # Inventory reconciliation
├── adapters/      # External API adapters
│   ├── shopify.py     # Shopify API client
│   ├── bc365.py       # Business Central 365 client
│   └── mock/          # Mock implementations for demos
├── storage/       # Database and cache repositories
│   ├── database.py    # SQLAlchemy models
│   └── cache.py       # Redis operations
└── config.py      # Configuration management
```

## Features

- **Bulk Product Sync**: `POST /sync/products/bulk` - Sync products from Shopify to BC365
- **Inventory Sync**: `POST /sync/inventory` - Reconcile inventory levels
- **Order Processing**: `POST /orders/process` - Process orders from Shopify
- **Health Check**: `GET /health` - Service health status
- **Metrics**: `GET /metrics` - Prometheus metrics

## Demo Instructions

### Mock Mode (Default - No Credentials Needed)

```bash
# Run the demo with mock adapters
python scripts/run_demo.py
```

The demo will:
1. Create mock Shopify products (100 items)
2. Sync them to mock BC365
3. Show sync statistics and timing
4. Display reconciliation results

### Real Mode (With Credentials)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
# SHOPIFY_API_KEY=your_api_key
# SHOPIFY_API_PASSWORD=your_api_password

# Run with real APIs
python scripts/run_demo.py --real-mode
```

## API Examples

### Sync Products

**Request:**
```bash
curl -X POST http://localhost:8000/sync/products/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "batch_size": 100,
    "skip_existing": false
  }'
```

**Response:**
```json
{
  "synced": 100,
  "created": 95,
  "updated": 5,
  "failed": 0,
  "duration_ms": 2450,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Sync Inventory

**Request:**
```bash
curl -X POST http://localhost:8000/sync/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": "warehouse-001",
    "reconcile": true
  }'
```

**Response:**
```json
{
  "location_id": "warehouse-001",
  "total_items": 500,
  "matched": 485,
  "discrepancies": 15,
  "adjustments": [
    {"sku": "SKU-001", "shopify": 100, "bc365": 95, "adjustment": 5}
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Process Order

**Request:**
```bash
curl -X POST http://localhost:8000/orders/process \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order-12345",
    "action": "fulfill"
  }'
```

**Response:**
```json
{
  "order_id": "order-12345",
  "status": "fulfilled",
  "fulfillment_id": "ful-67890",
  "tracking_number": "1Z999AA1234567890",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Health Check

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "shopify_api": "ok",
    "bc365_api": "ok"
  }
}
```

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/shopify_integration

# Redis
REDIS_URL=redis://localhost:6379/0

# Shopify (optional - mock mode works without these)
SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_PASSWORD=your_api_password

# Business Central 365 (optional)
BC365_TENANT_ID=your_tenant
BC365_CLIENT_ID=your_client_id
BC365_CLIENT_SECRET=your_secret
```

## Implemented vs Planned

| Implemented | Planned |
|-------------|---------|
| ✅ Core sync endpoints | 🔄 Webhook event streaming |
| ✅ Rate limiting | 🔄 Multi-tenant support |
| ✅ Mock adapters | 🔄 OAuth 2.0 integration |
| ✅ Batch processing | 🔄 Real-time dashboard |
| ✅ Health & metrics | 🔄 Grafana monitoring |
| ✅ Inventory reconciliation | 🔄 Automated stock alerts |
| ✅ Error handling | 🔄 Circuit breaker pattern |

## Development

```bash
# Run linting
ruff check src tests

# Format code
ruff format src tests

# Type checking
mypy src

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Start API server
uvicorn src.api.main:app --reload
```

## Docker

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Build production image
docker build -t shopify-integration .

# Run production container
docker run -p 8000:8000 --env-file .env shopify-integration
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_sync.py -v

# Run integration tests
pytest tests/integration/ -v
```

## License

MIT License
