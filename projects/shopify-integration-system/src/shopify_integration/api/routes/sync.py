"""Synchronization endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from shopify_integration.api.main import db_repo, sync_service
from shopify_integration.domain.models import ReconciliationResult, SyncResult

router = APIRouter()


class BulkSyncRequest(BaseModel):
    """Bulk sync request."""

    batch_size: int = Field(default=100, ge=1, le=1000)


class InventorySyncRequest(BaseModel):
    """Inventory sync request."""

    location_id: str = Field(default="location_1")


@router.post("/products/bulk", response_model=SyncResult)
async def sync_products_bulk(request: BulkSyncRequest) -> SyncResult:
    """Synchronize products in bulk from Shopify to BC365.

    Args:
        request: Sync request with batch size.

    Returns:
        Sync result with statistics.
    """
    if not sync_service:
        raise HTTPException(status_code=503, detail="Service not available")

    result = await sync_service.sync_products_bulk()

    # Log to database
    if db_repo:
        await db_repo.log_sync(
            operation="products_bulk_sync",
            status=result.status.value,
            items_processed=result.items_processed,
            items_succeeded=result.items_succeeded,
            items_failed=result.items_failed,
            errors=result.errors,
            started_at=result.started_at,
            completed_at=result.completed_at,
        )

    return result


@router.post("/inventory", response_model=ReconciliationResult)
async def sync_inventory(request: InventorySyncRequest) -> ReconciliationResult:
    """Synchronize and reconcile inventory.

    Args:
        request: Inventory sync request.

    Returns:
        Reconciliation result with discrepancies.
    """
    if not sync_service:
        raise HTTPException(status_code=503, detail="Service not available")

    result = await sync_service.sync_inventory(request.location_id)

    # Log to database
    if db_repo:
        await db_repo.log_sync(
            operation="inventory_sync",
            status=result.status.value,
            items_processed=result.discrepancies_found,
            items_succeeded=result.discrepancies_resolved,
            items_failed=result.discrepancies_found - result.discrepancies_resolved,
            details={
                "discrepancies_found": result.discrepancies_found,
                "shopify_total": result.shopify_total,
                "bc365_total": result.bc365_total,
            },
            started_at=result.started_at,
            completed_at=result.completed_at,
        )

    return result


@router.get("/logs")
async def get_sync_logs(
    operation: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Get synchronization logs.

    Args:
        operation: Filter by operation name.
        limit: Maximum number of logs.

    Returns:
        List of sync log entries.
    """
    if not db_repo:
        return []

    return await db_repo.get_sync_logs(operation=operation, limit=limit)
