"""Tests for scraper."""

import tempfile
from pathlib import Path

from helioscraper.models import SiteConfig
from helioscraper.scraper import Scraper


def test_scraper_creation() -> None:
    """Test creating scraper."""
    config = SiteConfig(
        name="Test Site",
        base_url="https://example.com",
        selectors={"product_list": ".product"},
    )

    scraper = Scraper(config, mock_mode=True)
    assert scraper.config == config
    assert scraper.mock_mode is True


def test_mock_scraper_run() -> None:
    """Test mock scraper execution."""
    config = SiteConfig(
        name="Test Site",
        base_url="https://example.com",
        selectors={
            "product_list": ".product-card",
            "title": ".product-title",
            "price": ".product-price",
        },
        max_pages=2,
        delays={"min": 0.01, "max": 0.02},
    )

    scraper = Scraper(config, mock_mode=True)
    result = scraper.scrape()

    assert result.site_name == "Test Site"
    assert result.total_items > 0
    assert result.total_pages > 0
    assert result.duration_seconds is not None
    assert result.success_rate == 100.0


def test_scraper_export_csv() -> None:
    """Test CSV export."""
    config = SiteConfig(
        name="Test Site",
        base_url="https://example.com",
        selectors={"product_list": ".product"},
        max_pages=1,
        delays={"min": 0.01, "max": 0.02},
    )

    scraper = Scraper(config, mock_mode=True)
    scraper.scrape()

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        csv_path = f.name

    scraper.export_csv(csv_path)

    assert Path(csv_path).exists()
    content = Path(csv_path).read_text()
    assert "url" in content
    assert "title" in content

    Path(csv_path).unlink()


def test_scraper_export_sqlite() -> None:
    """Test SQLite export."""
    config = SiteConfig(
        name="Test Site",
        base_url="https://example.com",
        selectors={"product_list": ".product"},
        max_pages=1,
        delays={"min": 0.01, "max": 0.02},
    )

    scraper = Scraper(config, mock_mode=True)
    scraper.scrape()

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    scraper.export_sqlite(db_path)

    assert Path(db_path).exists()

    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scraped_items")
    count = cursor.fetchone()[0]
    conn.close()

    assert count > 0
    Path(db_path).unlink()


def test_scraper_generate_report() -> None:
    """Test report generation."""
    config = SiteConfig(
        name="Test Site",
        base_url="https://example.com",
        selectors={"product_list": ".product"},
        max_pages=1,
        delays={"min": 0.01, "max": 0.02},
    )

    scraper = Scraper(config, mock_mode=True)
    scraper.scrape()

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        html_path = f.name

    scraper.generate_report(html_path, format="html")

    assert Path(html_path).exists()
    content = Path(html_path).read_text()
    assert "Scraping Report" in content
    assert "Test Site" in content

    Path(html_path).unlink()
