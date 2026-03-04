#!/usr/bin/env python3
"""Digital Inventory Management - Tkinter GUI Application."""

import tkinter as tk
from tkinter import messagebox, ttk

from inventory_management.database import Database
from inventory_management.models import InventoryItem
from inventory_management.forecaster import DemandForecaster


class InventoryApp:
    """Main inventory management application."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the application.

        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.root.title("Digital Inventory Management")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Initialize database
        self.db = Database()
        self.db.initialize()

        # Initialize forecaster
        self.forecaster = DemandForecaster()

        # Setup UI
        self._setup_styles()
        self._create_menu()
        self._create_main_frame()
        self._create_sidebar()
        self._create_content_area()

        # Load initial data
        self.refresh_items()

    def _setup_styles(self) -> None:
        """Setup ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure styles
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Action.TButton", font=("Helvetica", 10))

    def _create_menu(self) -> None:
        """Create application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Data", command=self._export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Inventory menu
        inv_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Inventory", menu=inv_menu)
        inv_menu.add_command(label="Add Item", command=self._show_add_item)
        inv_menu.add_command(label="Stock In", command=self._show_stock_in)
        inv_menu.add_command(label="Stock Out", command=self._show_stock_out)

        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Low Stock", command=self._show_low_stock)
        reports_menu.add_command(label="Expiring Soon", command=self._show_expiring)
        reports_menu.add_command(label="Waste Report", command=self._show_waste_report)

    def _create_main_frame(self) -> None:
        """Create main frame."""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def _create_sidebar(self) -> None:
        """Create sidebar with actions."""
        sidebar = ttk.LabelFrame(self.main_frame, text="Actions", padding="10")
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # Action buttons
        ttk.Button(
            sidebar,
            text="Add Item",
            command=self._show_add_item,
        ).pack(fill="x", pady=2)

        ttk.Button(
            sidebar,
            text="Stock In",
            command=self._show_stock_in,
        ).pack(fill="x", pady=2)

        ttk.Button(
            sidebar,
            text="Stock Out",
            command=self._show_stock_out,
        ).pack(fill="x", pady=2)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=10)

        ttk.Button(
            sidebar,
            text="Forecast",
            command=self._show_forecast,
        ).pack(fill="x", pady=2)

        ttk.Button(
            sidebar,
            text="Reports",
            command=self._show_reports,
        ).pack(fill="x", pady=2)

        # Barcode scanner simulation
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(sidebar, text="Barcode Scanner:").pack(anchor="w")
        self.barcode_entry = ttk.Entry(sidebar)
        self.barcode_entry.pack(fill="x", pady=2)
        self.barcode_entry.bind("<Return>", self._on_barcode_scan)

    def _create_content_area(self) -> None:
        """Create main content area."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=1, sticky="nsew")

        # Inventory tab
        self.inventory_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.inventory_frame, text="Inventory")

        # Search bar
        search_frame = ttk.Frame(self.inventory_frame)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.refresh_items())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(
            side="left", fill="x", expand=True, padx=5
        )

        # Items treeview
        columns = ("sku", "name", "category", "quantity", "unit", "reorder_level", "status")
        self.items_tree = ttk.Treeview(
            self.inventory_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        # Configure columns
        self.items_tree.heading("sku", text="SKU")
        self.items_tree.heading("name", text="Name")
        self.items_tree.heading("category", text="Category")
        self.items_tree.heading("quantity", text="Qty")
        self.items_tree.heading("unit", text="Unit")
        self.items_tree.heading("reorder_level", text="Reorder")
        self.items_tree.heading("status", text="Status")

        self.items_tree.column("sku", width=100)
        self.items_tree.column("name", width=200)
        self.items_tree.column("category", width=100)
        self.items_tree.column("quantity", width=60)
        self.items_tree.column("unit", width=60)
        self.items_tree.column("reorder_level", width=70)
        self.items_tree.column("status", width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.inventory_frame,
            orient="vertical",
            command=self.items_tree.yview
        )
        self.items_tree.configure(yscrollcommand=scrollbar.set)

        self.items_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind double-click
        self.items_tree.bind("<Double-1>", self._on_item_double_click)

        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.dashboard_frame, text="Dashboard")

        self._update_dashboard()

    def _update_dashboard(self) -> None:
        """Update dashboard with stats."""
        # Clear existing widgets
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

        # Get stats
        stats = self.db.get_inventory_stats()

        # Stats grid
        ttk.Label(
            self.dashboard_frame,
            text="Dashboard",
            style="Title.TLabel",
        ).pack(anchor="w", pady=(0, 20))

        stats_frame = ttk.Frame(self.dashboard_frame)
        stats_frame.pack(fill="x")

        # Total items
        self._create_stat_card(
            stats_frame,
            "Total Items",
            str(stats.get("total_items", 0)),
            0, 0,
        )

        # Low stock
        self._create_stat_card(
            stats_frame,
            "Low Stock",
            str(stats.get("low_stock_count", 0)),
            0, 1,
            "red" if stats.get("low_stock_count", 0) > 0 else "black",
        )

        # Total value
        self._create_stat_card(
            stats_frame,
            "Total Value",
            f"${stats.get('total_value', 0):.2f}",
            0, 2,
        )

        # Categories
        self._create_stat_card(
            stats_frame,
            "Categories",
            str(stats.get("category_count", 0)),
            1, 0,
        )

    def _create_stat_card(
        self,
        parent: ttk.Frame,
        title: str,
        value: str,
        row: int,
        col: int,
        color: str = "black",
    ) -> None:
        """Create a stat card."""
        card = ttk.LabelFrame(parent, text=title, padding="10")
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        label = ttk.Label(card, text=value, font=("Helvetica", 24, "bold"))
        label.pack()
        label.configure(foreground=color)

    def refresh_items(self) -> None:
        """Refresh items list."""
        # Clear existing
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)

        # Get items
        search = self.search_var.get()
        items = self.db.search_items(search) if search else self.db.get_all_items()

        # Add to tree
        for item in items:
            status = "OK" if item.quantity > item.reorder_level else "LOW"
            self.items_tree.insert(
                "",
                "end",
                values=(
                    item.sku,
                    item.name,
                    item.category,
                    item.quantity,
                    item.unit,
                    item.reorder_level,
                    status,
                ),
            )

    def _show_add_item(self) -> None:
        """Show add item dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Item")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Form fields
        ttk.Label(dialog, text="SKU:").pack(anchor="w", padx=10, pady=(10, 0))
        sku_entry = ttk.Entry(dialog)
        sku_entry.pack(fill="x", padx=10)

        ttk.Label(dialog, text="Name:").pack(anchor="w", padx=10, pady=(10, 0))
        name_entry = ttk.Entry(dialog)
        name_entry.pack(fill="x", padx=10)

        ttk.Label(dialog, text="Category:").pack(anchor="w", padx=10, pady=(10, 0))
        category_entry = ttk.Entry(dialog)
        category_entry.pack(fill="x", padx=10)

        ttk.Label(dialog, text="Unit:").pack(anchor="w", padx=10, pady=(10, 0))
        unit_entry = ttk.Entry(dialog)
        unit_entry.insert(0, "pcs")
        unit_entry.pack(fill="x", padx=10)

        ttk.Label(dialog, text="Reorder Level:").pack(anchor="w", padx=10, pady=(10, 0))
        reorder_entry = ttk.Entry(dialog)
        reorder_entry.insert(0, "10")
        reorder_entry.pack(fill="x", padx=10)

        def save():
            item = InventoryItem(
                sku=sku_entry.get(),
                name=name_entry.get(),
                category=category_entry.get(),
                unit=unit_entry.get(),
                reorder_level=int(reorder_entry.get()),
            )
            self.db.add_item(item)
            self.refresh_items()
            self._update_dashboard()
            dialog.destroy()
            messagebox.showinfo("Success", "Item added successfully!")

        ttk.Button(dialog, text="Save", command=save).pack(pady=20)

    def _show_stock_in(self) -> None:
        """Show stock in dialog."""
        messagebox.showinfo("Stock In", "Stock In dialog - To be implemented")

    def _show_stock_out(self) -> None:
        """Show stock out dialog."""
        messagebox.showinfo("Stock Out", "Stock Out dialog - To be implemented")

    def _show_forecast(self) -> None:
        """Show forecast dialog."""
        messagebox.showinfo("Forecast", "Forecast dialog - To be implemented")

    def _show_reports(self) -> None:
        """Show reports dialog."""
        messagebox.showinfo("Reports", "Reports dialog - To be implemented")

    def _show_low_stock(self) -> None:
        """Show low stock report."""
        items = self.db.get_low_stock_items()
        messagebox.showinfo(
            "Low Stock Report",
            f"Items below reorder level: {len(items)}\n" +
            "\n".join([f"- {item.name} ({item.quantity} remaining)" for item in items[:10]])
        )

    def _show_expiring(self) -> None:
        """Show expiring items report."""
        messagebox.showinfo("Expiring Soon", "Expiring items report - To be implemented")

    def _show_waste_report(self) -> None:
        """Show waste report."""
        messagebox.showinfo("Waste Report", "Waste report - To be implemented")

    def _export_data(self) -> None:
        """Export data to CSV."""
        import csv
        from datetime import datetime

        filename = f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        items = self.db.get_all_items()

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["SKU", "Name", "Category", "Quantity", "Unit"])
            for item in items:
                writer.writerow([item.sku, item.name, item.category, item.quantity, item.unit])

        messagebox.showinfo("Export", f"Data exported to {filename}")

    def _on_barcode_scan(self, event) -> None:
        """Handle barcode scan."""
        barcode = self.barcode_entry.get().strip()
        if barcode:
            item = self.db.get_item_by_sku(barcode)
            if item:
                messagebox.showinfo("Barcode Scan", f"Found: {item.name}\nQuantity: {item.quantity}")
            else:
                messagebox.showwarning("Barcode Scan", f"Item not found: {barcode}")
            self.barcode_entry.delete(0, tk.END)

    def _on_item_double_click(self, event) -> None:
        """Handle item double click."""
        selection = self.items_tree.selection()
        if selection:
            item = self.items_tree.item(selection[0])
            sku = item["values"][0]
            messagebox.showinfo("Item Details", f"SKU: {sku}\nDetails view - To be implemented")


def main() -> None:
    """Main entry point."""
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
