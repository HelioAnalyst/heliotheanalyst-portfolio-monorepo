"""Database operations for inventory management."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from inventory_management.models import InventoryItem, InventoryStats, StockMovement


class Database:
    """SQLite database for inventory management."""

    def __init__(self, db_path: str = "inventory.db") -> None:
        """Initialize database.

        Args:
            db_path: Path to database file.
        """
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def initialize(self) -> None:
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                quantity INTEGER DEFAULT 0,
                unit TEXT DEFAULT 'pcs',
                reorder_level INTEGER DEFAULT 10,
                unit_cost REAL DEFAULT 0.0,
                location TEXT DEFAULT '',
                expiry_date TEXT,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Stock movements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_sku TEXT NOT NULL,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                reference TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                FOREIGN KEY (item_sku) REFERENCES items(sku)
            )
        """)

        # Waste records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                reason TEXT NOT NULL,
                notes TEXT,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                recorded_by TEXT,
                FOREIGN KEY (item_sku) REFERENCES items(sku)
            )
        """)

        conn.commit()

        # Add sample data if empty
        self._add_sample_data()

    def _add_sample_data(self) -> None:
        """Add sample data if database is empty."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM items")
        if cursor.fetchone()[0] == 0:
            sample_items = [
                ("FLOUR001", "All-Purpose Flour", "Baking", 50, "kg", 20, 2.50),
                ("SUGAR001", "Granulated Sugar", "Baking", 30, "kg", 15, 1.80),
                ("OIL001", "Vegetable Oil", "Cooking", 20, "L", 10, 4.50),
                ("RICE001", "Basmati Rice", "Grains", 40, "kg", 20, 3.20),
                ("PASTA001", "Spaghetti", "Pasta", 25, "kg", 15, 2.00),
                ("TOM001", "Canned Tomatoes", "Canned", 60, "cans", 30, 1.20),
                ("CHEESE001", "Mozzarella Cheese", "Dairy", 15, "kg", 8, 8.50),
                ("CHICKEN001", "Chicken Breast", "Meat", 20, "kg", 10, 12.00),
                ("BEEF001", "Ground Beef", "Meat", 18, "kg", 10, 10.50),
                ("SALT001", "Sea Salt", "Spices", 10, "kg", 5, 1.50),
            ]

            cursor.executemany("""
                INSERT INTO items (sku, name, category, quantity, unit, reorder_level, unit_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_items)

            conn.commit()

    def add_item(self, item: InventoryItem) -> None:
        """Add new item.

        Args:
            item: Item to add.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO items (sku, name, category, quantity, unit, reorder_level, unit_cost, location, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.sku, item.name, item.category, item.quantity, item.unit,
            item.reorder_level, item.unit_cost, item.location, item.notes
        ))

        conn.commit()

    def get_item(self, sku: str) -> Optional[InventoryItem]:
        """Get item by SKU.

        Args:
            sku: Item SKU.

        Returns:
            Item or None.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items WHERE sku = ?", (sku,))
        row = cursor.fetchone()

        if row:
            return InventoryItem(
                sku=row["sku"],
                name=row["name"],
                category=row["category"],
                quantity=row["quantity"],
                unit=row["unit"],
                reorder_level=row["reorder_level"],
                unit_cost=row["unit_cost"],
                location=row["location"],
                notes=row["notes"],
            )
        return None

    def get_item_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """Get item by SKU (alias)."""
        return self.get_item(sku)

    def get_all_items(self) -> list[InventoryItem]:
        """Get all items.

        Returns:
            List of items.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items ORDER BY name")
        rows = cursor.fetchall()

        return [
            InventoryItem(
                sku=row["sku"],
                name=row["name"],
                category=row["category"],
                quantity=row["quantity"],
                unit=row["unit"],
                reorder_level=row["reorder_level"],
                unit_cost=row["unit_cost"],
                location=row["location"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def search_items(self, query: str) -> list[InventoryItem]:
        """Search items.

        Args:
            query: Search query.

        Returns:
            List of matching items.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM items
            WHERE sku LIKE ? OR name LIKE ? OR category LIKE ?
            ORDER BY name
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))

        rows = cursor.fetchall()

        return [
            InventoryItem(
                sku=row["sku"],
                name=row["name"],
                category=row["category"],
                quantity=row["quantity"],
                unit=row["unit"],
                reorder_level=row["reorder_level"],
                unit_cost=row["unit_cost"],
                location=row["location"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def update_quantity(self, sku: str, quantity: int) -> None:
        """Update item quantity.

        Args:
            sku: Item SKU.
            quantity: New quantity.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE items SET quantity = ?, updated_at = ? WHERE sku = ?
        """, (quantity, datetime.now().isoformat(), sku))

        conn.commit()

    def add_stock_movement(self, movement: StockMovement) -> None:
        """Record stock movement.

        Args:
            movement: Movement to record.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO stock_movements (item_sku, movement_type, quantity, reference, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            movement.item_sku, movement.movement_type, movement.quantity,
            movement.reference, movement.notes, movement.created_by
        ))

        conn.commit()

    def get_low_stock_items(self) -> list[InventoryItem]:
        """Get items below reorder level.

        Returns:
            List of low stock items.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items WHERE quantity <= reorder_level")
        rows = cursor.fetchall()

        return [
            InventoryItem(
                sku=row["sku"],
                name=row["name"],
                category=row["category"],
                quantity=row["quantity"],
                unit=row["unit"],
                reorder_level=row["reorder_level"],
                unit_cost=row["unit_cost"],
            )
            for row in rows
        ]

    def get_inventory_stats(self) -> dict:
        """Get inventory statistics.

        Returns:
            Statistics dictionary.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM items")
        total_items = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(quantity) FROM items")
        total_quantity = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(quantity * unit_cost) FROM items")
        total_value = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM items WHERE quantity <= reorder_level")
        low_stock = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT category) FROM items")
        categories = cursor.fetchone()[0]

        return {
            "total_items": total_items,
            "total_quantity": total_quantity,
            "total_value": total_value,
            "low_stock_count": low_stock,
            "category_count": categories,
        }
