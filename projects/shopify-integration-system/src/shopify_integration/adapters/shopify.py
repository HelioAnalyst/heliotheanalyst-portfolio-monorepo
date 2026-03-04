"""Shopify API adapter with rate limiting and retry logic."""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

import httpx

from shopify_integration.adapters.base import APIError, BaseAdapter, RateLimitError
from shopify_integration.config import Settings
from shopify_integration.domain.models import (
    InventoryItem,
    Money,
    Order,
    OrderItem,
    Product,
    ProductVariant,
)


class ShopifyAdapter(BaseAdapter):
    """Real Shopify API adapter."""

    def __init__(self, settings: Settings) -> None:
        """Initialize Shopify adapter.

        Args:
            settings: Application settings.
        """
        super().__init__(settings)
        self.base_url = f"https://{settings.shopify_shop_domain}/admin/api/{settings.shopify_api_version}"
        self.auth = (settings.shopify_api_key, settings.shopify_api_password)
        self._rate_limit_semaphore = asyncio.Semaphore(settings.shopify_rate_limit_requests)
        self._last_request_time: Optional[datetime] = None

    @property
    def name(self) -> str:
        """Return adapter name."""
        return "shopify"

    async def connect(self) -> None:
        """Establish connection to Shopify API."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            timeout=self.settings.sync_timeout,
        )

    async def disconnect(self) -> None:
        """Close connection to Shopify API."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make rate-limited API request.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            **kwargs: Additional request parameters.

        Returns:
            Response JSON.

        Raises:
            RateLimitError: If rate limit exceeded.
            APIError: If API returns an error.
        """
        if not self._client:
            raise RuntimeError("Adapter not connected")

        async with self._rate_limit_semaphore:
            # Rate limiting delay
            if self._last_request_time:
                elapsed = (datetime.utcnow() - self._last_request_time).total_seconds()
                delay = self.settings.shopify_rate_limit_window / self.settings.shopify_rate_limit_requests
                if elapsed < delay:
                    await asyncio.sleep(delay - elapsed)

            response = await self._client.request(method, endpoint, **kwargs)
            self._last_request_time = datetime.utcnow()

            if response.status_code == 429:
                raise RateLimitError("Shopify rate limit exceeded")

            if response.status_code >= 400:
                raise APIError(f"Shopify API error: {response.status_code} - {response.text}")

            return response.json()

    async def health_check(self) -> dict[str, Any]:
        """Check Shopify API health.

        Returns:
            Health status dictionary.
        """
        try:
            await self._make_request("GET", "/shop.json")
            return {"status": "healthy", "adapter": self.name}
        except Exception as e:
            return {"status": "unhealthy", "adapter": self.name, "error": str(e)}

    async def get_products(
        self,
        limit: int = 100,
        since_id: Optional[str] = None,
    ) -> list[Product]:
        """Get products from Shopify.

        Args:
            limit: Maximum number of products to fetch.
            since_id: Fetch products after this ID.

        Returns:
            List of products.
        """
        params: dict[str, Any] = {"limit": limit}
        if since_id:
            params["since_id"] = since_id

        data = await self._make_request("GET", "/products.json", params=params)
        return [self._parse_product(p) for p in data.get("products", [])]

    async def get_inventory_items(
        self,
        location_id: str,
    ) -> list[InventoryItem]:
        """Get inventory items for a location.

        Args:
            location_id: Location ID.

        Returns:
            List of inventory items.
        """
        data = await self._make_request(
            "GET",
            f"/locations/{location_id}/inventory_levels.json",
        )
        return [self._parse_inventory_item(i) for i in data.get("inventory_levels", [])]

    async def get_orders(
        self,
        status: str = "any",
        limit: int = 50,
        created_at_min: Optional[datetime] = None,
    ) -> list[Order]:
        """Get orders from Shopify.

        Args:
            status: Order status filter.
            limit: Maximum number of orders.
            created_at_min: Minimum creation date.

        Returns:
            List of orders.
        """
        params: dict[str, Any] = {"status": status, "limit": limit}
        if created_at_min:
            params["created_at_min"] = created_at_min.isoformat()

        data = await self._make_request("GET", "/orders.json", params=params)
        return [self._parse_order(o) for o in data.get("orders", [])]

    def _parse_product(self, data: dict[str, Any]) -> Product:
        """Parse Shopify product JSON to Product model."""
        variants = [
            ProductVariant(
                id=str(v["id"]),
                product_id=str(data["id"]),
                sku=v.get("sku", ""),
                title=v.get("title", ""),
                price=Money(
                    amount=Decimal(str(v.get("price", "0"))),
                    currency_code="USD",
                ),
                compare_at_price=Money(
                    amount=Decimal(str(v.get("compare_at_price", "0"))),
                    currency_code="USD",
                ) if v.get("compare_at_price") else None,
                inventory_quantity=v.get("inventory_quantity", 0),
                weight=v.get("weight"),
                weight_unit=v.get("weight_unit", "kg"),
                barcode=v.get("barcode"),
                position=v.get("position", 1),
                created_at=datetime.fromisoformat(v["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(v["updated_at"].replace("Z", "+00:00")),
            )
            for v in data.get("variants", [])
        ]

        return Product(
            id=str(data["id"]),
            title=data["title"],
            description=data.get("body_html"),
            vendor=data.get("vendor", ""),
            product_type=data.get("product_type", ""),
            tags=data.get("tags", []),
            status=data.get("status", "active"),
            variants=variants,
            options=data.get("options", []),
            images=[img["src"] for img in data.get("images", [])],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
        )

    def _parse_inventory_item(self, data: dict[str, Any]) -> InventoryItem:
        """Parse Shopify inventory JSON to InventoryItem model."""
        return InventoryItem(
            id=str(data["inventory_item_id"]),
            variant_id=str(data["inventory_item_id"]),
            sku=data.get("sku", ""),
            location_id=str(data["location_id"]),
            available=data.get("available", 0),
            incoming=data.get("incoming", 0),
        )

    def _parse_order(self, data: dict[str, Any]) -> Order:
        """Parse Shopify order JSON to Order model."""
        line_items = [
            OrderItem(
                id=str(item["id"]),
                variant_id=str(item.get("variant_id", "")),
                product_id=str(item.get("product_id", "")),
                sku=item.get("sku", ""),
                title=item["title"],
                quantity=item["quantity"],
                price=Money(
                    amount=Decimal(str(item.get("price", "0"))),
                    currency_code="USD",
                ),
            )
            for item in data.get("line_items", [])
        ]

        return Order(
            id=str(data["id"]),
            order_number=str(data.get("order_number", "")),
            name=data.get("name", ""),
            line_items=line_items,
            subtotal_price=Money(
                amount=Decimal(str(data.get("subtotal_price", "0"))),
                currency_code="USD",
            ),
            total_tax=Money(
                amount=Decimal(str(data.get("total_tax", "0"))),
                currency_code="USD",
            ),
            total_price=Money(
                amount=Decimal(str(data.get("total_price", "0"))),
                currency_code="USD",
            ),
            financial_status=data.get("financial_status", "pending"),
            fulfillment_status=data.get("fulfillment_status"),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
        )


class MockShopifyAdapter(BaseAdapter):
    """Mock Shopify adapter for testing without credentials."""

    def __init__(self, settings: Settings) -> None:
        """Initialize mock adapter.

        Args:
            settings: Application settings.
        """
        super().__init__(settings)
        self._products: list[Product] = []
        self._inventory: list[InventoryItem] = []
        self._orders: list[Order] = []
        self._setup_mock_data()

    @property
    def name(self) -> str:
        """Return adapter name."""
        return "shopify_mock"

    def _setup_mock_data(self) -> None:
        """Set up mock product data."""
        from datetime import timedelta

        base_time = datetime.utcnow()

        # Create mock products
        for i in range(1, 11):
            variant = ProductVariant(
                id=f"variant_{i}",
                product_id=f"product_{i}",
                sku=f"SKU-{i:04d}",
                title=f"Variant {i}",
                price=Money(amount=Decimal(str(10 * i))),
                inventory_quantity=100 - i * 5,
                barcode=f"BARCODE{i:06d}",
                created_at=base_time - timedelta(days=i),
                updated_at=base_time - timedelta(hours=i),
            )

            product = Product(
                id=f"product_{i}",
                title=f"Mock Product {i}",
                description=f"This is a mock product {i} for testing",
                vendor=f"Vendor {i % 3 + 1}",
                product_type=["Electronics", "Clothing", "Home"][i % 3],
                tags=["mock", "test", f"category-{i % 3}"],
                variants=[variant],
                images=[f"https://example.com/image{i}.jpg"],
                created_at=base_time - timedelta(days=i),
                updated_at=base_time - timedelta(hours=i),
            )
            self._products.append(product)

            # Create mock inventory
            inventory = InventoryItem(
                id=f"inventory_{i}",
                variant_id=f"variant_{i}",
                sku=f"SKU-{i:04d}",
                location_id="location_1",
                available=100 - i * 5,
                incoming=20 if i % 2 == 0 else 0,
            )
            self._inventory.append(inventory)

            # Create mock orders
            if i <= 5:
                order_item = OrderItem(
                    id=f"order_item_{i}",
                    variant_id=f"variant_{i}",
                    product_id=f"product_{i}",
                    sku=f"SKU-{i:04d}",
                    title=f"Mock Product {i}",
                    quantity=i,
                    price=Money(amount=Decimal(str(10 * i))),
                )

                order = Order(
                    id=f"order_{i}",
                    order_number=str(1000 + i),
                    name=f"#{1000 + i}",
                    line_items=[order_item],
                    subtotal_price=Money(amount=Decimal(str(10 * i * i))),
                    total_tax=Money(amount=Decimal(str(i))),
                    total_price=Money(amount=Decimal(str(10 * i * i + i))),
                    financial_status=["paid", "pending", "refunded"][i % 3],
                    created_at=base_time - timedelta(hours=i * 2),
                    updated_at=base_time - timedelta(hours=i),
                )
                self._orders.append(order)

    async def connect(self) -> None:
        """Mock connect - no action needed."""
        pass

    async def disconnect(self) -> None:
        """Mock disconnect - no action needed."""
        pass

    async def health_check(self) -> dict[str, Any]:
        """Return mock health status.

        Returns:
            Health status dictionary.
        """
        return {
            "status": "healthy",
            "adapter": self.name,
            "mock": True,
            "products": len(self._products),
            "inventory": len(self._inventory),
            "orders": len(self._orders),
        }

    async def get_products(
        self,
        limit: int = 100,
        since_id: Optional[str] = None,
    ) -> list[Product]:
        """Get mock products.

        Args:
            limit: Maximum number of products.
            since_id: Fetch products after this ID.

        Returns:
            List of mock products.
        """
        products = self._products
        if since_id:
            products = [p for p in products if p.id > since_id]
        return products[:limit]

    async def get_inventory_items(
        self,
        location_id: str,
    ) -> list[InventoryItem]:
        """Get mock inventory items.

        Args:
            location_id: Location ID.

        Returns:
            List of mock inventory items.
        """
        return [i for i in self._inventory if i.location_id == location_id]

    async def get_orders(
        self,
        status: str = "any",
        limit: int = 50,
        created_at_min: Optional[datetime] = None,
    ) -> list[Order]:
        """Get mock orders.

        Args:
            status: Order status filter.
            limit: Maximum number of orders.
            created_at_min: Minimum creation date.

        Returns:
            List of mock orders.
        """
        orders = self._orders
        if created_at_min:
            orders = [o for o in orders if o.created_at >= created_at_min]
        return orders[:limit]
