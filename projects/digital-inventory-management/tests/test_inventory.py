"""Tests for inventory management."""

import tempfile
from pathlib import Path

import pytest

from inventory_management.database import Database
from inventory_management.forecaster import DemandForecaster
from inventory_management.models import InventoryItem


@pytest.fixture
def temp_db():
    """Create temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    db.initialize()
    yield db

    Path(db_path).unlink(missing_ok=True)


def test_add_item(temp_db):
    """Test adding an item."""
    item = InventoryItem(
        sku="TEST001",
        name="Test Item",
        category="Test",
        quantity=100,
        unit="pcs",
        reorder_level=20,
    )

    temp_db.add_item(item)

    fetched = temp_db.get_item("TEST001")
    assert fetched is not None
    assert fetched.name == "Test Item"
    assert fetched.quantity == 100


def test_get_all_items(temp_db):
    """Test getting all items."""
    # Add test items
    for i in range(3):
        item = InventoryItem(
            sku=f"TEST{i:03d}",
            name=f"Test Item {i}",
            quantity=10 * i,
        )
        temp_db.add_item(item)

    items = temp_db.get_all_items()
    assert len(items) >= 3


def test_search_items(temp_db):
    """Test searching items."""
    item = InventoryItem(
        sku="SEARCH001",
        name="Searchable Item",
        category="Search",
    )
    temp_db.add_item(item)

    results = temp_db.search_items("search")
    assert len(results) > 0
    assert any(i.name == "Searchable Item" for i in results)


def test_update_quantity(temp_db):
    """Test updating quantity."""
    item = InventoryItem(
        sku="QTY001",
        name="Quantity Test",
        quantity=10,
    )
    temp_db.add_item(item)

    temp_db.update_quantity("QTY001", 50)

    updated = temp_db.get_item("QTY001")
    assert updated.quantity == 50


def test_low_stock_items(temp_db):
    """Test getting low stock items."""
    # Add low stock item
    item = InventoryItem(
        sku="LOW001",
        name="Low Stock Item",
        quantity=5,
        reorder_level=10,
    )
    temp_db.add_item(item)

    low_stock = temp_db.get_low_stock_items()
    assert any(i.sku == "LOW001" for i in low_stock)


def test_inventory_stats(temp_db):
    """Test inventory statistics."""
    stats = temp_db.get_inventory_stats()

    assert "total_items" in stats
    assert "total_quantity" in stats
    assert "total_value" in stats
    assert "low_stock_count" in stats


def test_item_is_low_stock():
    """Test low stock detection."""
    item = InventoryItem(
        sku="TEST",
        name="Test",
        quantity=5,
        reorder_level=10,
    )
    assert item.is_low_stock is True

    item2 = InventoryItem(
        sku="TEST2",
        name="Test 2",
        quantity=15,
        reorder_level=10,
    )
    assert item2.is_low_stock is False


def test_item_total_value():
    """Test total value calculation."""
    item = InventoryItem(
        sku="TEST",
        name="Test",
        quantity=10,
        unit_cost=5.0,
    )
    assert item.total_value == 50.0


def test_forecaster_generate_history():
    """Test generating sample history."""
    forecaster = DemandForecaster()
    history = forecaster.generate_sample_history(days=30)

    assert len(history) == 30
    assert "date" in history.columns
    assert "demand" in history.columns


def test_forecaster_forecast():
    """Test demand forecasting."""
    forecaster = DemandForecaster()
    history = forecaster.generate_sample_history(days=60)

    forecast = forecaster.forecast(history, periods=7)

    assert len(forecast) == 7
    assert "forecast" in forecast.columns
    assert "lower_bound" in forecast.columns
    assert "upper_bound" in forecast.columns


def test_forecaster_reorder_point():
    """Test reorder point calculation."""
    forecaster = DemandForecaster()
    history = forecaster.generate_sample_history(days=60)

    calc = forecaster.calculate_reorder_point(history, lead_time_days=7)

    assert "avg_daily_demand" in calc
    assert "lead_time_demand" in calc
    assert "safety_stock" in calc
    assert "reorder_point" in calc
    assert calc["reorder_point"] > 0
