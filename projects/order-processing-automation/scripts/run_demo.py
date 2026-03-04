#!/usr/bin/env python3
"""Demo script for Order Processing Automation."""

import asyncio
import sys
import uuid
from decimal import Decimal

sys.path.insert(0, "src")

from order_processing.config import Settings
from order_processing.domain.models import (
    Order,
    OrderItem,
    OrderStatus,
    ShippingAddress,
)
from order_processing.services.order_service import OrderService
from order_processing.storage.database import DatabaseRepository


async def run_demo() -> None:
    """Run order processing demo."""
    print("=" * 60)
    print("Order Processing Automation - Demo")
    print("=" * 60)
    print()

    settings = Settings()

    # Initialize database
    db_repo = DatabaseRepository(settings)
    await db_repo.connect()

    # Initialize service
    service = OrderService(db_repo, settings)

    print("Creating sample orders...")
    print("-" * 40)

    # Create sample orders
    orders = []
    for i in range(5):
        order = Order(
            idempotency_key=str(uuid.uuid4()),
            customer_id=f"cust_{i+1}",
            customer_email=f"customer{i+1}@example.com",
            items=[
                OrderItem(
                    product_id=f"prod_{i+1}",
                    sku=f"SKU-{i+1:04d}",
                    name=f"Product {i+1}",
                    quantity=i + 1,
                    unit_price=Decimal(str(10 * (i + 1))),
                    total_price=Decimal(str(10 * (i + 1) * (i + 1))),
                ),
            ],
            shipping_address=ShippingAddress(
                name=f"Customer {i+1}",
                line1=f"{i+100} Main St",
                city="New York",
                state="NY",
                postal_code=f"100{i+1:02d}",
            ),
            subtotal=Decimal(str(10 * (i + 1) * (i + 1))),
            tax=Decimal(str(i + 1)),
            shipping_cost=Decimal("5.00"),
            total=Decimal(str(10 * (i + 1) * (i + 1) + i + 1 + 5)),
        )

        created = await service.create_order(order)
        orders.append(created)
        print(f"Created order: {created.id}")
        print(f"  Total: ${created.total}")
        print(f"  Status: {created.status.value}")
        print()

    # Wait for processing
    print("Waiting for order processing...")
    await asyncio.sleep(2)

    # Check order statuses
    print("-" * 40)
    print("Order Statuses:")
    print("-" * 40)

    for order in orders:
        updated = await service.get_order(order.id or "")
        if updated:
            print(f"Order {updated.id[:8]}...: {updated.status.value}")
            if updated.provider:
                print(f"  Provider: {updated.provider.value}")
            if updated.provider_order_id:
                print(f"  Provider Order ID: {updated.provider_order_id}")

    # Get metrics
    print()
    print("-" * 40)
    print("Dashboard Metrics:")
    print("-" * 40)

    metrics = await service.get_metrics()
    print(f"Total Orders: {metrics.total_orders}")
    print(f"Pending: {metrics.pending_orders}")
    print(f"Processing: {metrics.processing_orders}")
    print(f"Completed: {metrics.completed_orders}")
    print(f"Failed: {metrics.failed_orders}")
    print(f"Success Rate: {metrics.success_rate_percent:.1f}%")

    if metrics.provider_distribution:
        print("\nProvider Distribution:")
        for provider, count in metrics.provider_distribution.items():
            print(f"  {provider}: {count}")

    # Cleanup
    await db_repo.disconnect()

    print()
    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
