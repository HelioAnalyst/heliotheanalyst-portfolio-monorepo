"""Health check endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from shopify_integration.api.main import sync_service
from shopify_integration.config import Settings, get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    mock_mode: bool
    adapters: dict


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Get service health status.

    Returns:
        Health status response.
    """
    adapter_health = {"shopify": "unknown", "bc365": "unknown"}

    if sync_service:
        health = await sync_service.health_check()
        adapter_health = health.get("adapters", adapter_health)

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        mock_mode=settings.mock_mode,
        adapters=adapter_health,
    )


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness probe for Kubernetes.

    Returns:
        Readiness status.
    """
    if not sync_service:
        return {"ready": False, "reason": "Service not initialized"}

    health = await sync_service.health_check()
    is_ready = health.get("status") == "healthy"

    return {
        "ready": is_ready,
        "adapters": health.get("adapters", {}),
    }
