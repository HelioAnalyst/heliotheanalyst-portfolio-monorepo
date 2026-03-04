"""Tests for API endpoints."""

import pytest
from httpx import AsyncClient

from shopify_integration.api.main import create_app


@pytest.fixture
def app():
    """Create test app."""
    return create_app()


@pytest.mark.asyncio
async def test_health_endpoint(app) -> None:
    """Test health endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "adapters" in data


@pytest.mark.asyncio
async def test_ready_endpoint(app) -> None:
    """Test readiness endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 200
    data = response.json()
    assert "ready" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(app) -> None:
    """Test metrics endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "shopify_integration" in response.text


@pytest.mark.asyncio
async def test_sync_products_bulk(app) -> None:
    """Test product sync endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/sync/products/bulk", json={"batch_size": 10})

    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "products_bulk_sync"
    assert "status" in data
    assert "items_processed" in data


@pytest.mark.asyncio
async def test_sync_inventory(app) -> None:
    """Test inventory sync endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/sync/inventory", json={"location_id": "location_1"})

    assert response.status_code == 200
    data = response.json()
    assert "discrepancies_found" in data
    assert "discrepancies_resolved" in data


@pytest.mark.asyncio
async def test_process_orders(app) -> None:
    """Test order processing endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/orders/process", json={"limit": 5})

    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "orders_process"
    assert "status" in data
    assert "items_processed" in data


@pytest.mark.asyncio
async def test_sync_logs_endpoint(app) -> None:
    """Test sync logs endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/sync/logs?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
