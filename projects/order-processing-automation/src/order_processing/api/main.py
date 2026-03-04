"""FastAPI application for order processing."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest

from order_processing.config import get_settings
from order_processing.domain.models import (
    DashboardMetrics,
    Order,
    OrderStatus,
    ProcessingResult,
)
from order_processing.services.order_service import OrderService
from order_processing.storage.database import DatabaseRepository

# Metrics
REQUEST_COUNT = Counter(
    "order_processing_requests_total",
    "Total requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "order_processing_request_duration_seconds",
    "Request duration",
    ["method", "endpoint"],
)

# Global instances
order_service: OrderService | None = None
db_repo: DatabaseRepository | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    global order_service, db_repo

    settings = get_settings()
    db_repo = DatabaseRepository(settings)
    await db_repo.connect()

    order_service = OrderService(db_repo, settings)

    yield

    await db_repo.disconnect()


app = FastAPI(
    title="Order Processing Automation",
    description="Async order pipeline with idempotency guarantees",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def root():
    return {"service": "order-api", "status": "ok"}

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "order-processing"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response
    from prometheus_client import CONTENT_TYPE_LATEST
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/orders", response_model=dict)
async def create_order(order: Order) -> dict:
    """Submit new order for processing.

    Args:
        order: Order to process.

    Returns:
        Created order with ID.
    """
    if not order_service:
        raise HTTPException(status_code=503, detail="Service unavailable")

    result = await order_service.create_order(order)
    return {
        "order_id": result.id,
        "idempotency_key": result.idempotency_key,
        "status": result.status.value,
        "message": "Order submitted for processing",
    }


@app.get("/orders/{order_id}")
async def get_order(order_id: str) -> dict:
    """Get order by ID.

    Args:
        order_id: Order ID.

    Returns:
        Order details.
    """
    if not order_service:
        raise HTTPException(status_code=503, detail="Service unavailable")

    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": order.id,
        "status": order.status.value,
        "provider": order.provider.value if order.provider else None,
        "total": str(order.total),
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }


@app.post("/orders/{order_id}/process")
async def process_order(order_id: str) -> dict:
    """Manually process an order.

    Args:
        order_id: Order ID to process.

    Returns:
        Processing result.
    """
    if not order_service:
        raise HTTPException(status_code=503, detail="Service unavailable")

    result = await order_service.process_order(order_id)
    return {
        "order_id": result.order_id,
        "success": result.success,
        "status": result.status.value,
        "provider": result.provider.value if result.provider else None,
        "message": result.message,
    }


@app.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_metrics() -> DashboardMetrics:
    """Get dashboard metrics.

    Returns:
        Processing metrics.
    """
    if not order_service:
        raise HTTPException(status_code=503, detail="Service unavailable")

    return await order_service.get_metrics()


@app.post("/webhooks/provider-status")
async def provider_webhook(payload: dict) -> dict:
    """Handle provider status webhook.

    Args:
        payload: Webhook payload.

    Returns:
        Acknowledgment.
    """
    if not order_service:
        raise HTTPException(status_code=503, detail="Service unavailable")

    await order_service.handle_provider_webhook(payload)
    return {"received": True}


@app.post("/orders/{order_id}/retry")
async def retry_order(order_id: str) -> dict:
    """Retry failed order.

    Args:
        order_id: Order ID to retry.

    Returns:
        Retry result.
    """
    if not order_service:
        raise HTTPException(status_code=503, detail="Service unavailable")

    result = await order_service.retry_order(order_id)
    return {
        "order_id": result.order_id,
        "success": result.success,
        "status": result.status.value,
        "message": result.message,
    }
