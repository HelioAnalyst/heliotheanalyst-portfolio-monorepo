#!/usr/bin/env python3
"""Demo script for Digital Inventory Management."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from inventory_management.database import Database
from inventory_management.models import InventoryItem
from inventory_management.forecaster import DemandForecaster


def main() -> None:
    """Run inventory management demo."""
    print("=" * 60)
    print("Digital Inventory Management - Demo")
    print("=" * 60)
    print()

    # Initialize database
    print("1. Initializing database...")
    db = Database("demo_inventory.db")
    db.initialize()
    print("   Database initialized with sample data")
    print()

    # Get inventory stats
    print("2. Inventory Statistics")
    print("-" * 40)
    stats = db.get_inventory_stats()
    print(f"   Total Items: {stats['total_items']}")
    print(f"   Total Quantity: {stats['total_quantity']}")
    print(f"   Total Value: ${stats['total_value']:.2f}")
    print(f"   Low Stock Items: {stats['low_stock_count']}")
    print(f"   Categories: {stats['category_count']}")
    print()

    # List all items
    print("3. Inventory Items")
    print("-" * 40)
    items = db.get_all_items()
    for item in items[:5]:
        status = "LOW" if item.is_low_stock else "OK"
        print(f"   {item.sku}: {item.name}")
        print(f"      Qty: {item.quantity} {item.unit} | Status: {status}")
    print(f"   ... and {len(items) - 5} more items")
    print()

    # Low stock items
    print("4. Low Stock Alert")
    print("-" * 40)
    low_stock = db.get_low_stock_items()
    if low_stock:
        for item in low_stock:
            print(f"   ⚠️  {item.name}: {item.quantity} remaining (reorder: {item.reorder_level})")
    else:
        print("   No low stock items")
    print()

    # Demand forecasting
    print("5. Demand Forecasting")
    print("-" * 40)
    forecaster = DemandForecaster()

    # Generate sample history
    history = forecaster.generate_sample_history(days=90, base_demand=15)

    # Generate forecast
    forecast = forecaster.forecast(history, periods=14)

    print("   14-Day Demand Forecast:")
    total_forecast = 0
    for _, row in forecast.head(7).iterrows():
        date_str = row['date'].strftime('%Y-%m-%d')
        print(f"      {date_str}: {row['forecast']:.1f} units")
        total_forecast += row['forecast']

    print(f"\n   Total forecast (7 days): {total_forecast:.1f} units")
    print()

    # Reorder point calculation
    print("6. Reorder Point Calculation")
    print("-" * 40)
    reorder_calc = forecaster.calculate_reorder_point(history, lead_time_days=7)
    print(f"   Average daily demand: {reorder_calc['avg_daily_demand']} units")
    print(f"   Demand std dev: {reorder_calc['demand_std']}")
    print(f"   Lead time demand: {reorder_calc['lead_time_demand']} units")
    print(f"   Safety stock: {reorder_calc['safety_stock']} units")
    print(f"   Recommended reorder point: {reorder_calc['reorder_point']} units")
    print()

    # Search functionality
    print("7. Search Functionality")
    print("-" * 40)
    search_results = db.search_items("chicken")
    print(f"   Search 'chicken': {len(search_results)} result(s)")
    for item in search_results:
        print(f"      - {item.name}: {item.quantity} {item.unit}")
    print()

    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print()
    print("To run the GUI:")
    print("  python src/main.py")
    print()
    print("Sample barcodes for testing:")
    for item in items[:3]:
        print(f"  {item.sku} -> {item.name}")


if __name__ == "__main__":
    main()
