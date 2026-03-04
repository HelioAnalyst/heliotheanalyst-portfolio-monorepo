"""Business Central 365 API adapter."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

import httpx

from shopify_integration.adapters.base import APIError, BaseAdapter
from shopify_integration.config import Settings
from shopify_integration.domain.models import InventoryItem, Money, Product, ProductVariant


class BC365Adapter(BaseAdapter):
    """Real Business Central 365 API adapter."""

    def __init__(self, settings: Settings) -> None:
        """Initialize BC365 adapter.

        Args:
            settings: Application settings.
        """
        super().__init__(settings)
        self.base_url = (
            f"https://api.businesscentral.dynamics.com/v2.0/{settings.bc365_tenant_id}/"
            f"{settings.bc365_environment}/api/v2.0"
        )
        self._access_token: Optional[str] = None

    @property
    def name(self) -> str:
        """Return adapter name."""
        return "bc365"

    async def _get_access_token(self) -> str:
        """Get OAuth access token.

        Returns:
            Access token string.
        """
        if self._access_token:
            return self._access_token

        token_url = f"https://login.microsoftonline.com/{self.settings.bc365_tenant_id}/oauth2/v2.0/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.settings.bc365_client_id,
            "client_secret": self.settings.bc365_client_secret,
            "scope": "https://api.businesscentral.dynamics.com/.default",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            return self._access_token

    async def connect(self) -> None:
        """Establish connection to BC365 API."""
        token = await self._get_access_token()
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=self.settings.sync_timeout,
        )

    async def disconnect(self) -> None:
        """Close connection to BC365 API."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make API request.

        Args:
            method: HTTP method.
            endpoint: API endpoint.
            **kwargs: Additional request parameters.

        Returns:
            Response JSON.

        Raises:
            APIError: If API returns an error.
        """
        if not self._client:
            raise RuntimeError("Adapter not connected")

        response = await self._client.request(method, endpoint, **kwargs)

        if response.status_code >= 400:
            raise APIError(f"BC365 API error: {response.status_code} - {response.text}")

        return response.json()

    async def health_check(self) -> dict[str, Any]:
        """Check BC365 API health.

        Returns:
            Health status dictionary.
        """
        try:
            await self._make_request("GET", "/companies")
            return {"status": "healthy", "adapter": self.name}
        except Exception as e:
            return {"status": "unhealthy", "adapter": self.name, "error": str(e)}

    async def get_products(self) -> list[Product]:
        """Get products from BC365.

        Returns:
            List of products.
        """
        data = await self._make_request("GET", "/items")
        return [self._parse_product(item) for item in data.get("value", [])]

    async def get_inventory(self) -> list[InventoryItem]:
        """Get inventory from BC365.

        Returns:
            List of inventory items.
        """
        data = await self._make_request("GET", "/itemLedgerEntries")
        return [self._parse_inventory(item) for item in data.get("value", [])]

    async def update_inventory(
        self,
        item_id: str,
        quantity: int,
    ) -> bool:
        """Update inventory quantity.

        Args:
            item_id: Item ID.
            quantity: New quantity.

        Returns:
            True if successful.
        """
        data = {"inventory": quantity}
        await self._make_request("PATCH", f"/items({item_id})", json=data)
        return True

    def _parse_product(self, data: dict[str, Any]) -> Product:
        """Parse BC365 item to Product model."""
        variant = ProductVariant(
            id=str(data.get("id", "")),
            product_id=str(data.get("id", "")),
            sku=data.get("number", ""),
            title=data.get("displayName", ""),
            price=Money(
                amount=Decimal(str(data.get("unitPrice", 0))),
                currency_code=data.get("priceUnit", "USD"),
            ),
            inventory_quantity=int(data.get("inventory", 0)),
            weight=data.get("netWeight"),
        )

        return Product(
            id=str(data.get("id", "")),
            title=data.get("displayName", ""),
            description=data.get("description"),
            vendor=data.get("vendorName", ""),
            product_type=data.get("itemCategoryCode", ""),
            variants=[variant],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def _parse_inventory(self, data: dict[str, Any]) -> InventoryItem:
        """Parse BC365 ledger entry to InventoryItem model."""
        return InventoryItem(
            id=str(data.get("id", "")),
            variant_id=str(data.get("itemId", "")),
            sku=data.get("itemNumber", ""),
            location_id=str(data.get("locationId", "")),
            available=int(data.get("quantity", 0)),
        )


class MockBC365Adapter(BaseAdapter):
    """Mock BC365 adapter for testing without credentials."""

    def __init__(self, settings: Settings) -> None:
        """Initialize mock adapter.

        Args:
            settings: Application settings.
        """
        super().__init__(settings)
        self._products: list[Product] = []
        self._inventory: dict[str, int] = {}
        self._setup_mock_data()

    @property
    def name(self) -> str:
        """Return adapter name."""
        return "bc365_mock"

    def _setup_mock_data(self) -> None:
        """Set up mock data."""
        from datetime import timedelta

        base_time = datetime.utcnow()

        for i in range(1, 11):
            variant = ProductVariant(
                id=f"bc_item_{i}",
                product_id=f"bc_item_{i}",
                sku=f"SKU-{i:04d}",
                title=f"BC Product {i}",
                price=Money(amount=Decimal(str(10 * i))),
                inventory_quantity=95 - i * 5,  # Slightly different from Shopify
                created_at=base_time - timedelta(days=i),
                updated_at=base_time - timedelta(hours=i),
            )

            product = Product(
                id=f"bc_item_{i}",
                title=f"BC Product {i}",
                description=f"Business Central product {i}",
                vendor=f"Vendor {i % 3 + 1}",
                product_type=["Electronics", "Clothing", "Home"][i % 3],
                variants=[variant],
                created_at=base_time - timedelta(days=i),
                updated_at=base_time - timedelta(hours=i),
            )
            self._products.append(product)
            self._inventory[f"bc_item_{i}"] = 95 - i * 5

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
        }

    async def get_products(self) -> list[Product]:
        """Get mock products.

        Returns:
            List of mock products.
        """
        return self._products

    async def get_inventory(self) -> list[InventoryItem]:
        """Get mock inventory.

        Returns:
            List of mock inventory items.
        """
        return [
            InventoryItem(
                id=item.id,
                variant_id=variant.id,
                sku=variant.sku,
                location_id="MAIN",
                available=self._inventory.get(item.id, 0),
            )
            for item in self._products
            for variant in item.variants
        ]

    async def update_inventory(
        self,
        item_id: str,
        quantity: int,
    ) -> bool:
        """Update mock inventory.

        Args:
            item_id: Item ID.
            quantity: New quantity.

        Returns:
            True if successful.
        """
        self._inventory[item_id] = quantity
        return True
