"""Tests for models."""

from datetime import datetime

from helioscraper.models import ScrapedItem, ScrapeResult, SiteConfig


def test_scraped_item_creation() -> None:
    """Test creating a scraped item."""
    item = ScrapedItem(
        url="https://example.com/product/1",
        title="Test Product",
        price=29.99,
    )

    assert item.url == "https://example.com/product/1"
    assert item.title == "Test Product"
    assert item.price == 29.99
    assert item.currency == "USD"
    assert item.scraped_at is not None


def test_scraped_item_to_dict() -> None:
    """Test converting item to dict."""
    item = ScrapedItem(
        url="https://example.com/product/1",
        title="Test Product",
        price=29.99,
    )

    data = item.to_dict()
    assert data["url"] == "https://example.com/product/1"
    assert data["title"] == "Test Product"
    assert data["price"] == 29.99


def test_scrape_result_stats() -> None:
    """Test scrape result statistics."""
    items = [
        ScrapedItem(url=f"https://example.com/{i}", title=f"Item {i}")
        for i in range(10)
    ]

    result = ScrapeResult(
        site_name="Test Site",
        total_items=10,
        items=items,
        errors=["error1"],
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )

    assert result.total_items == 10
    assert len(result.items) == 10
    assert len(result.errors) == 1
    assert result.success_rate == (10 / 11) * 100


def test_scrape_result_unique_items() -> None:
    """Test getting unique items."""
    items = [
        ScrapedItem(url="https://example.com/1", title="Item 1"),
        ScrapedItem(url="https://example.com/1", title="Item 1 Duplicate"),
        ScrapedItem(url="https://example.com/2", title="Item 2"),
    ]

    result = ScrapeResult(
        site_name="Test Site",
        total_items=3,
        items=items,
        started_at=datetime.utcnow(),
    )

    unique = result.get_unique_items()
    assert len(unique) == 2


def test_site_config_creation() -> None:
    """Test creating site config."""
    config = SiteConfig(
        name="Test Site",
        base_url="https://example.com",
        selectors={
            "product_list": ".product",
            "title": ".title",
        },
        max_pages=5,
    )

    assert config.name == "Test Site"
    assert config.base_url == "https://example.com"
    assert config.selectors["product_list"] == ".product"
    assert config.max_pages == 5
    assert config.user_agent_rotation is True
