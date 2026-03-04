"""Synchronization service with batch processing and reconciliation."""

import asyncio
from datetime import datetime
from typing import Any

from shopify_integration.adapters.base import BaseAdapter
from shopify_integration.config import Settings
from shopify_integration.domain.models import (
    InventoryItem,
    Order,
    Product,
    ReconciliationResult,
    SyncResult,
    SyncStatus,
)


class SyncService:
    """Service for synchronizing data between Shopify and BC365."""

    def __init__(
        self,
        shopify_adapter: BaseAdapter,
        bc365_adapter: BaseAdapter,
        settings: Settings,
    ) -> None:
        """Initialize sync service.

        Args:
            shopify_adapter: Shopify API adapter.
            bc365_adapter: BC365 API adapter.
            settings: Application settings.
        """
        self.shopify = shopify_adapter
        self.bc365 = bc365_adapter
        self.settings = settings

    async def sync_products_bulk(self) -> SyncResult:
        """Synchronize products in bulk from Shopify to BC365.

        Returns:
            Sync result with statistics.
        """
        started_at = datetime.utcnow()
        errors: list[str] = []
        items_processed = 0
        items_succeeded = 0
        items_failed = 0

        try:
            # Fetch products from Shopify
            shopify_products = await self.shopify.get_products(
                limit=self.settings.sync_batch_size,
            )

            for product in shopify_products:
                items_processed += 1
                try:
                    # In real implementation, transform and send to BC365
                    await asyncio.sleep(0.01)  # Simulate processing
                    items_succeeded += 1
                except Exception as e:
                    items_failed += 1
                    errors.append(f"Failed to sync product {product.id}: {str(e)}")

            return SyncResult(
                status=SyncStatus.COMPLETED if items_failed == 0 else SyncStatus.PARTIAL,
                operation="products_bulk_sync",
                items_processed=items_processed,
                items_succeeded=items_succeeded,
                items_failed=items_failed,
                errors=errors,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        except Exception as e:
            return SyncResult(
                status=SyncStatus.FAILED,
                operation="products_bulk_sync",
                items_processed=items_processed,
                items_succeeded=items_succeeded,
                items_failed=items_failed,
                errors=errors + [str(e)],
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

    async def sync_inventory(
        self,
        location_id: str = "location_1",
    ) -> ReconciliationResult:
        """Synchronize and reconcile inventory.

        Args:
            location_id: Location ID to sync.

        Returns:
            Reconciliation result with discrepancies.
        """
        started_at = datetime.utcnow()

        try:
            # Fetch inventory from both systems
            shopify_inventory = await self.shopify.get_inventory_items(location_id)
            bc365_inventory = await self.bc365.get_inventory()

            # Build lookup maps
            shopify_map = {item.sku: item for item in shopify_inventory}
            bc365_map = {item.sku: item for item in bc365_inventory}

            # Find discrepancies
            discrepancies: list[dict[str, Any]] = []
            all_skus = set(shopify_map.keys()) | set(bc365_map.keys())

            for sku in all_skus:
                shopify_qty = shopify_map.get(sku, InventoryItem(id="", variant_id="", sku=sku, location_id="")).available
                bc365_qty = bc365_map.get(sku, InventoryItem(id="", variant_id="", sku=sku, location_id="")).available

                if shopify_qty != bc365_qty:
                    discrepancies.append({
                        "sku": sku,
                        "shopify_quantity": shopify_qty,
                        "bc365_quantity": bc365_qty,
                        "difference": shopify_qty - bc365_qty,
                    })

            # Resolve discrepancies (sync Shopify to BC365)
            resolved = 0
            for disc in discrepancies:
                try:
                    shopify_item = shopify_map.get(disc["sku"])
                    if shopify_item:
                        # In real implementation, update BC365
                        resolved += 1
                except Exception:
                    pass

            return ReconciliationResult(
                status=SyncStatus.COMPLETED,
                discrepancies_found=len(discrepancies),
                discrepancies_resolved=resolved,
                shopify_total=sum(item.available for item in shopify_inventory),
                bc365_total=sum(item.available for item in bc365_inventory),
                mismatched_items=discrepancies,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        except Exception as e:
            return ReconciliationResult(
                status=SyncStatus.FAILED,
                discrepancies_found=0,
                discrepancies_resolved=0,
                shopify_total=0,
                bc365_total=0,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

    async def process_orders(
        self,
        limit: int = 50,
    ) -> SyncResult:
        """Process orders from Shopify.

        Args:
            limit: Maximum orders to process.

        Returns:
            Sync result with statistics.
        """
        started_at = datetime.utcnow()
        errors: list[str] = []
        items_processed = 0
        items_succeeded = 0
        items_failed = 0

        try:
            orders = await self.shopify.get_orders(limit=limit)

            for order in orders:
                items_processed += 1
                try:
                    # Validate order
                    if not order.line_items:
                        raise ValueError(f"Order {order.id} has no line items")

                    # In real implementation, create order in BC365
                    await asyncio.sleep(0.01)  # Simulate processing
                    items_succeeded += 1

                except Exception as e:
                    items_failed += 1
                    errors.append(f"Failed to process order {order.id}: {str(e)}")

            return SyncResult(
                status=SyncStatus.COMPLETED if items_failed == 0 else SyncStatus.PARTIAL,
                operation="orders_process",
                items_processed=items_processed,
                items_succeeded=items_succeeded,
                items_failed=items_failed,
                errors=errors,
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

        except Exception as e:
            return SyncResult(
                status=SyncStatus.FAILED,
                operation="orders_process",
                items_processed=items_processed,
                items_succeeded=items_succeeded,
                items_failed=items_failed,
                errors=errors + [str(e)],
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

    async def health_check(self) -> dict[str, Any]:
        """Check health of all adapters.

        Returns:
            Combined health status.
        """
        shopify_health = await self.shopify.health_check()
        bc365_health = await self.bc365.health_check()

        all_healthy = all(
            h.get("status") == "healthy"
            for h in [shopify_health, bc365_health]
        )

        return {
            "status": "healthy" if all_healthy else "degraded",
            "adapters": {
                "shopify": shopify_health,
                "bc365": bc365_health,
            },
        }
