#!/usr/bin/env python3
"""Demo script for Shopify Integration System.

Runs all sync operations in mock mode - no real credentials needed.
"""

import argparse
import asyncio
import sys

sys.path.insert(0, "src")

from shopify_integration.adapters.bc365 import BC365Adapter, MockBC365Adapter
from shopify_integration.adapters.shopify import MockShopifyAdapter, ShopifyAdapter
from shopify_integration.config import Settings
from shopify_integration.services.sync_service import SyncService


async def run_demo(use_real_mode: bool = False) -> None:
    """Run demo operations.

    Args:
        use_real_mode: Use real adapters if credentials configured.
    """
    settings = Settings()

    if not use_real_mode:
        settings.mock_mode = True

    print("=" * 60)
    print("Shopify Integration System - Demo")
    print("=" * 60)
    print(f"Mode: {'REAL' if use_real_mode else 'MOCK (no credentials needed)'}")
    print()

    # Initialize adapters
    if settings.mock_mode or not settings.shopify_credentials_configured:
        print("Using Mock Shopify Adapter")
        shopify = MockShopifyAdapter(settings)
    else:
        print("Using Real Shopify Adapter")
        shopify = ShopifyAdapter(settings)

    if settings.mock_mode or not settings.bc365_credentials_configured:
        print("Using Mock BC365 Adapter")
        bc365 = MockBC365Adapter(settings)
    else:
        print("Using Real BC365 Adapter")
        bc365 = BC365Adapter(settings)

    # Connect adapters
    await shopify.connect()
    await bc365.connect()

    # Initialize sync service
    sync = SyncService(shopify, bc365, settings)

    # Health check
    print("\n" + "-" * 40)
    print("1. Health Check")
    print("-" * 40)
    health = await sync.health_check()
    print(f"Status: {health['status']}")
    for name, status in health['adapters'].items():
        print(f"  {name}: {status}")

    # Product sync
    print("\n" + "-" * 40)
    print("2. Bulk Product Sync")
    print("-" * 40)
    product_result = await sync.sync_products_bulk()
    print(f"Status: {product_result.status.value}")
    print(f"Items processed: {product_result.items_processed}")
    print(f"Items succeeded: {product_result.items_succeeded}")
    print(f"Items failed: {product_result.items_failed}")
    print(f"Duration: {product_result.duration_seconds:.2f}s")
    print(f"Success rate: {product_result.success_rate:.1f}%")

    # Inventory sync
    print("\n" + "-" * 40)
    print("3. Inventory Sync & Reconciliation")
    print("-" * 40)
    inventory_result = await sync.sync_inventory()
    print(f"Status: {inventory_result.status.value}")
    print(f"Discrepancies found: {inventory_result.discrepancies_found}")
    print(f"Discrepancies resolved: {inventory_result.discrepancies_resolved}")
    print(f"Shopify total: {inventory_result.shopify_total}")
    print(f"BC365 total: {inventory_result.bc365_total}")

    if inventory_result.mismatched_items:
        print("\nMismatched items (sample):")
        for item in inventory_result.mismatched_items[:3]:
            print(f"  SKU: {item['sku']}")
            print(f"    Shopify: {item['shopify_quantity']}, BC365: {item['bc365_quantity']}")

    # Order processing
    print("\n" + "-" * 40)
    print("4. Order Processing")
    print("-" * 40)
    order_result = await sync.process_orders(limit=10)
    print(f"Status: {order_result.status.value}")
    print(f"Orders processed: {order_result.items_processed}")
    print(f"Orders succeeded: {order_result.items_succeeded}")
    print(f"Orders failed: {order_result.items_failed}")
    print(f"Duration: {order_result.duration_seconds:.2f}s")

    # Cleanup
    await shopify.disconnect()
    await bc365.disconnect()

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Shopify Integration System Demo",
    )
    parser.add_argument(
        "--real-mode",
        action="store_true",
        help="Use real adapters (requires credentials in .env)",
    )
    args = parser.parse_args()

    try:
        asyncio.run(run_demo(use_real_mode=args.real_mode))
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nDemo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
