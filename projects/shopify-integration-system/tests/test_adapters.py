"""Tests for API adapters."""

import pytest

from shopify_integration.adapters.bc365 import MockBC365Adapter
from shopify_integration.adapters.shopify import MockShopifyAdapter


@pytest.mark.asyncio
async def test_shopify_health_check(shopify_adapter: MockShopifyAdapter) -> None:
    """Test Shopify adapter health check."""
    health = await shopify_adapter.health_check()
    assert health["status"] == "healthy"
    assert health["adapter"] == "shopify_mock"
    assert health["mock"] is True


@pytest.mark.asyncio
async def test_shopify_get_products(shopify_adapter: MockShopifyAdapter) -> None:
    """Test getting products from Shopify."""
    products = await shopify_adapter.get_products(limit=5)
    assert len(products) == 5

    product = products[0]
    assert product.id.startswith("product_")
    assert product.title.startswith("Mock Product")
    assert len(product.variants) > 0


@pytest.mark.asyncio
async def test_shopify_get_inventory(shopify_adapter: MockShopifyAdapter) -> None:
    """Test getting inventory from Shopify."""
    inventory = await shopify_adapter.get_inventory_items("location_1")
    assert len(inventory) > 0

    item = inventory[0]
    assert item.sku.startswith("SKU-")
    assert item.available >= 0


@pytest.mark.asyncio
async def test_shopify_get_orders(shopify_adapter: MockShopifyAdapter) -> None:
    """Test getting orders from Shopify."""
    orders = await shopify_adapter.get_orders(limit=3)
    assert len(orders) == 3

    order = orders[0]
    assert order.id.startswith("order_")
    assert len(order.line_items) > 0


@pytest.mark.asyncio
async def test_bc365_health_check(bc365_adapter: MockBC365Adapter) -> None:
    """Test BC365 adapter health check."""
    health = await bc365_adapter.health_check()
    assert health["status"] == "healthy"
    assert health["adapter"] == "bc365_mock"
    assert health["mock"] is True


@pytest.mark.asyncio
async def test_bc365_get_products(bc365_adapter: MockBC365Adapter) -> None:
    """Test getting products from BC365."""
    products = await bc365_adapter.get_products()
    assert len(products) > 0

    product = products[0]
    assert product.id.startswith("bc_item_")


@pytest.mark.asyncio
async def test_bc365_get_inventory(bc365_adapter: MockBC365Adapter) -> None:
    """Test getting inventory from BC365."""
    inventory = await bc365_adapter.get_inventory()
    assert len(inventory) > 0


@pytest.mark.asyncio
async def test_bc365_update_inventory(bc365_adapter: MockBC365Adapter) -> None:
    """Test updating inventory in BC365."""
    result = await bc365_adapter.update_inventory("bc_item_1", 50)
    assert result is True

    # Verify update
    inventory = await bc365_adapter.get_inventory()
    item = next((i for i in inventory if i.id == "bc_item_1"), None)
    assert item is not None
    assert item.available == 50
