"""Order processing endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from shopify_integration.api.main import db_repo, sync_service
from shopify_integration.domain.models import SyncResult

router = APIRouter()


class ProcessOrdersRequest(BaseModel):
    """Process orders request."""

    limit: int = Field(default=50, ge=1, le=250)


@router.post("/process", response_model=SyncResult)
async def process_orders(request: ProcessOrdersRequest) -> SyncResult:
    """Process orders from Shopify.

    Args:
        request: Process request with limit.

    Returns:
        Processing result with statistics.
    """
    if not sync_service:
        raise HTTPException(status_code=503, detail="Service not available")

    result = await sync_service.process_orders(limit=request.limit)

    # Log to database
    if db_repo:
        await db_repo.log_sync(
            operation="orders_process",
            status=result.status.value,
            items_processed=result.items_processed,
            items_succeeded=result.items_succeeded,
            items_failed=result.items_failed,
            errors=result.errors,
            started_at=result.started_at,
            completed_at=result.completed_at,
        )

    return result
