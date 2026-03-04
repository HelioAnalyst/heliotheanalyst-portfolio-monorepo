"""Pytest configuration and fixtures."""

import pytest
import pytest_asyncio

from shopify_integration.adapters.bc365 import MockBC365Adapter
from shopify_integration.adapters.shopify import MockShopifyAdapter
from shopify_integration.config import Settings
from shopify_integration.services.sync_service import SyncService


@pytest.fixture
def settings() -> Settings:
    """Create test settings."""
    return Settings(
        mock_mode=True,
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/15",  # Test DB
    )


@pytest_asyncio.fixture
async def shopify_adapter(settings: Settings) -> MockShopifyAdapter:
    """Create mock Shopify adapter."""
    adapter = MockShopifyAdapter(settings)
    await adapter.connect()
    yield adapter
    await adapter.disconnect()


@pytest_asyncio.fixture
async def bc365_adapter(settings: Settings) -> MockBC365Adapter:
    """Create mock BC365 adapter."""
    adapter = MockBC365Adapter(settings)
    await adapter.connect()
    yield adapter
    await adapter.disconnect()


@pytest_asyncio.fixture
async def sync_service(
    shopify_adapter: MockShopifyAdapter,
    bc365_adapter: MockBC365Adapter,
    settings: Settings,
) -> SyncService:
    """Create sync service with mock adapters."""
    return SyncService(shopify_adapter, bc365_adapter, settings)
