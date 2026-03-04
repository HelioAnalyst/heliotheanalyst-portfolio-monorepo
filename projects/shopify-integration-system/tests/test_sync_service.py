"""Tests for sync service."""

import pytest

from shopify_integration.domain.models import SyncStatus
from shopify_integration.services.sync_service import SyncService


@pytest.mark.asyncio
async def test_health_check(sync_service: SyncService) -> None:
    """Test health check."""
    health = await sync_service.health_check()
    assert health["status"] in ["healthy", "degraded"]
    assert "adapters" in health
    assert "shopify" in health["adapters"]
    assert "bc365" in health["adapters"]


@pytest.mark.asyncio
async def test_sync_products_bulk(sync_service: SyncService) -> None:
    """Test bulk product sync."""
    result = await sync_service.sync_products_bulk()

    assert result.operation == "products_bulk_sync"
    assert result.status in [SyncStatus.COMPLETED, SyncStatus.PARTIAL, SyncStatus.FAILED]
    assert result.items_processed >= 0
    assert result.items_succeeded >= 0
    assert result.items_failed >= 0
    assert result.items_processed == result.items_succeeded + result.items_failed
    assert result.started_at is not None


@pytest.mark.asyncio
async def test_sync_inventory(sync_service: SyncService) -> None:
    """Test inventory sync and reconciliation."""
    result = await sync_service.sync_inventory("location_1")

    assert result.status in [SyncStatus.COMPLETED, SyncStatus.FAILED]
    assert result.discrepancies_found >= 0
    assert result.discrepancies_resolved >= 0
    assert result.discrepancies_resolved <= result.discrepancies_found
    assert result.shopify_total >= 0
    assert result.bc365_total >= 0


@pytest.mark.asyncio
async def test_process_orders(sync_service: SyncService) -> None:
    """Test order processing."""
    result = await sync_service.process_orders(limit=5)

    assert result.operation == "orders_process"
    assert result.status in [SyncStatus.COMPLETED, SyncStatus.PARTIAL, SyncStatus.FAILED]
    assert result.items_processed >= 0
    assert result.items_succeeded >= 0
    assert result.items_failed >= 0
    assert result.items_processed == result.items_succeeded + result.items_failed


@pytest.mark.asyncio
async def test_sync_result_success_rate(sync_service: SyncService) -> None:
    """Test sync result success rate calculation."""
    result = await sync_service.sync_products_bulk()

    if result.items_processed > 0:
        expected_rate = (result.items_succeeded / result.items_processed) * 100
        assert result.success_rate == expected_rate
    else:
        assert result.success_rate == 100.0


@pytest.mark.asyncio
async def test_sync_result_duration(sync_service: SyncService) -> None:
    """Test sync result duration calculation."""
    result = await sync_service.sync_products_bulk()

    if result.completed_at:
        assert result.duration_seconds is not None
        assert result.duration_seconds >= 0
