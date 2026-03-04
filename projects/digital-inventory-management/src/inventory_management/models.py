"""Models for inventory management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class InventoryItem:
    """Inventory item model."""

    sku: str
    name: str
    category: str = "General"
    quantity: int = 0
    unit: str = "pcs"
    reorder_level: int = 10
    unit_cost: float = 0.0
    location: str = ""
    expiry_date: Optional[datetime] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def is_low_stock(self) -> bool:
        """Check if item is low on stock."""
        return self.quantity <= self.reorder_level

    @property
    def total_value(self) -> float:
        """Calculate total value."""
        return self.quantity * self.unit_cost


@dataclass
class StockMovement:
    """Stock movement transaction."""

    id: Optional[int] = None
    item_sku: str = ""
    movement_type: str = "in"  # in, out, adjustment
    quantity: int = 0
    reference: str = ""  # PO number, invoice, etc.
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""


@dataclass
class WasteRecord:
    """Waste/loss record."""

    id: Optional[int] = None
    item_sku: str = ""
    quantity: int = 0
    reason: str = ""  # expired, damaged, spoiled
    notes: str = ""
    recorded_at: datetime = field(default_factory=datetime.now)
    recorded_by: str = ""


@dataclass
class InventoryStats:
    """Inventory statistics."""

    total_items: int = 0
    total_quantity: int = 0
    total_value: float = 0.0
    low_stock_count: int = 0
    category_count: int = 0
    expiring_count: int = 0
