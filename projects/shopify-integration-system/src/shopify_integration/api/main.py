"""FastAPI application for Shopify Integration System."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest

from shopify_integration.adapters.bc365 import BC365Adapter, MockBC365Adapter
from shopify_integration.adapters.shopify import MockShopifyAdapter, ShopifyAdapter
from shopify_integration.config import get_settings
from shopify_integration.services.sync_service import SyncService
from shopify_integration.storage.cache import CacheRepository
from shopify_integration.storage.database import DatabaseRepository

# Metrics
REQUEST_COUNT = Counter(
    "shopify_integration_requests_total",
    "Total requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "shopify_integration_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

# Global service instances
sync_service: SyncService | None = None
cache_repo: CacheRepository | None = None
db_repo: DatabaseRepository | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    global sync_service, cache_repo, db_repo

    settings = get_settings()

    # Initialize adapters based on mock mode
    if settings.mock_mode or not settings.shopify_credentials_configured:
        shopify_adapter = MockShopifyAdapter(settings)
    else:
        shopify_adapter = ShopifyAdapter(settings)

    if settings.mock_mode or not settings.bc365_credentials_configured:
        bc365_adapter = MockBC365Adapter(settings)
    else:
        bc365_adapter = BC365Adapter(settings)

    # Connect adapters
    await shopify_adapter.connect()
    await bc365_adapter.connect()

    # Initialize repositories
    cache_repo = CacheRepository(settings)
    db_repo = DatabaseRepository(settings)

    try:
        await cache_repo.connect()
        await db_repo.connect()
    except Exception:
        # Cache/DB optional for demo
        pass

    # Initialize sync service
    sync_service = SyncService(shopify_adapter, bc365_adapter, settings)

    yield

    # Cleanup
    await shopify_adapter.disconnect()
    await bc365_adapter.disconnect()
    if cache_repo:
        await cache_repo.disconnect()
    if db_repo:
        await db_repo.disconnect()


def create_app() -> FastAPI:
    """Create FastAPI application.

    Returns:
        Configured FastAPI app.
    """
    app = FastAPI(
        title="Shopify Integration System",
        description="Enterprise-grade e-commerce synchronization platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request timing middleware
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        """Track request metrics."""
        import time

        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        method = request.method
        endpoint = request.url.path
        status = str(response.status_code)

        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        return response

    # Include routers
    from shopify_integration.api.routes import health, metrics, orders, sync

    app.include_router(health.router, tags=["Health"])
    app.include_router(metrics.router, tags=["Metrics"])
    app.include_router(sync.router, prefix="/sync", tags=["Sync"])
    app.include_router(orders.router, prefix="/orders", tags=["Orders"])

    return app


app = create_app()
