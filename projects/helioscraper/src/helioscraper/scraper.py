"""Main scraper implementation."""

import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from bs4 import BeautifulSoup

from helioscraper.browser import BrowserManager, MockBrowserManager
from helioscraper.config_loader import ConfigLoader
from helioscraper.models import ScrapedItem, ScrapeResult, SiteConfig
from helioscraper.report_generator import ReportGenerator


class Scraper:
    """Web scraper with configurable site rules."""

    def __init__(
        self,
        config: SiteConfig,
        browser_manager: Optional[BrowserManager] = None,
        mock_mode: bool = False,
    ) -> None:
        """Initialize scraper.

        Args:
            config: Site configuration.
            browser_manager: Custom browser manager.
            mock_mode: Use mock browser for testing.
        """
        self.config = config
        self.mock_mode = mock_mode

        if mock_mode:
            self.browser = MockBrowserManager(
                delay_min=config.delays.get("min", 0.1),
                delay_max=config.delays.get("max", 0.3),
            )
        else:
            self.browser = browser_manager or BrowserManager(
                headless=True,
                user_agent_rotation=config.user_agent_rotation,
                delay_min=config.delays.get("min", 1.0),
                delay_max=config.delays.get("max", 3.0),
                timeout=config.timeout,
            )

        self._results: list[ScrapedItem] = []
        self._errors: list[str] = []

    @classmethod
    def from_config(cls, config_path: str, mock_mode: bool = False) -> "Scraper":
        """Create scraper from config file.

        Args:
            config_path: Path to config file or config name.
            mock_mode: Use mock browser.

        Returns:
            Configured scraper.
        """
        loader = ConfigLoader()

        # If it's a path, extract name
        if "/" in config_path or "\\" in config_path:
            name = Path(config_path).stem
        else:
            name = config_path

        config = loader.load_config(name)
        return cls(config, mock_mode=mock_mode)

    def _extract_data(
        self,
        soup: BeautifulSoup,
        url: str,
    ) -> Optional[ScrapedItem]:
        """Extract data from page soup.

        Args:
            soup: Parsed HTML.
            url: Page URL.

        Returns:
            Scraped item or None.
        """
        selectors = self.config.selectors

        # Extract fields
        title_elem = soup.select_one(selectors.get("title", ""))
        price_elem = soup.select_one(selectors.get("price", ""))
        desc_elem = soup.select_one(selectors.get("description", ""))
        image_elem = soup.select_one(selectors.get("image", ""))

        # Parse price
        price = None
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Extract numeric price
            import re
            match = re.search(r'[\d,]+\.?\d*', price_text)
            if match:
                price = float(match.group().replace(',', ''))

        # Get image URL (handle @src attribute selector)
        image_url = None
        if image_elem:
            image_selector = selectors.get("image", "")
            if "@" in image_selector:
                attr = image_selector.split("@")[1]
                image_url = image_elem.get(attr)
            else:
                image_url = image_elem.get("src")

        return ScrapedItem(
            url=url,
            title=title_elem.get_text(strip=True) if title_elem else None,
            price=price,
            description=desc_elem.get_text(strip=True) if desc_elem else None,
            image_url=image_url,
            scraped_at=datetime.utcnow(),
        )

    def _scrape_page(self, url: str) -> list[ScrapedItem]:
        """Scrape single page.

        Args:
            url: Page URL.

        Returns:
            List of scraped items.
        """
        items = []

        try:
            driver = self.browser.get_driver()
            driver.get(url)
            self.browser.random_delay()

            # Get page source
            if self.mock_mode:
                html = self._generate_mock_html(url)
            else:
                html = driver.page_source

            soup = BeautifulSoup(html, "lxml")

            # Find product/ article containers
            list_selector = self.config.selectors.get("product_list", ".item")
            containers = soup.select(list_selector)

            if not containers:
                # Try single item extraction
                item = self._extract_data(soup, url)
                if item:
                    items.append(item)
            else:
                for container in containers:
                    # Extract link if available
                    link_selector = self.config.selectors.get("link", "a")
                    link_elem = container.select_one(link_selector)
                    item_url = url
                    if link_elem:
                        href = link_elem.get("href")
                        if href:
                            from urllib.parse import urljoin
                            item_url = urljoin(url, href)

                    item = self._extract_data(container, item_url)
                    if item:
                        items.append(item)

        except Exception as e:
            self._errors.append(f"Error scraping {url}: {str(e)}")

        return items

    def _generate_mock_html(self, url: str) -> str:
        """Generate mock HTML for demo.

        Args:
            url: URL being scraped.

        Returns:
            Mock HTML content.
        """
        import hashlib
        # Generate consistent items based on URL
        url_hash = int(hashlib.md5(url.encode()).hexdigest(), 16)

        items = []
        num_items = 5 + (url_hash % 5)  # 5-10 items per page

        for i in range(num_items):
            item_id = (url_hash + i) % 1000
            items.append(f"""
                <div class="product-card">
                    <h3 class="product-title">Mock Product {item_id}</h3>
                    <p class="product-price">${10 + (item_id % 100)}.99</p>
                    <p class="product-description">Description for product {item_id}</p>
                    <img class="product-image" src="https://example.com/image{item_id}.jpg">
                    <a class="product-link" href="/product/{item_id}">View</a>
                </div>
            """)

        return f"""
        <html>
        <body>
            <div class="product-list">
                {''.join(items)}
            </div>
            <div class="pagination">
                <a class="next" href="{url}?page=2">Next</a>
            </div>
        </body>
        </html>
        """

    def _get_next_page_url(self, current_url: str, page_num: int) -> Optional[str]:
        """Get URL for next page.

        Args:
            current_url: Current page URL.
            page_num: Next page number.

        Returns:
            Next page URL or None.
        """
        if not self.config.pagination.get("enabled", False):
            return None

        if page_num > self.config.max_pages:
            return None

        if page_num > self.config.pagination.get("max_pages", 10):
            return None

        # Simple pagination with query param
        from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

        parsed = urlparse(current_url)
        params = parse_qs(parsed.query)
        params['page'] = [str(page_num)]

        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    def scrape(self, start_url: Optional[str] = None) -> ScrapeResult:
        """Run scraping operation.

        Args:
            start_url: Starting URL (defaults to config base_url).

        Returns:
            Scraping result.
        """
        started_at = datetime.utcnow()
        self._results = []
        self._errors = []

        url = start_url or self.config.base_url
        page_num = 1

        try:
            self.browser.start()

            while url and page_num <= self.config.max_pages:
                items = self._scrape_page(url)
                self._results.extend(items)

                # Get next page
                page_num += 1
                url = self._get_next_page_url(url, page_num)

        finally:
            self.browser.stop()

        return ScrapeResult(
            site_name=self.config.name,
            total_items=len(self._results),
            total_pages=page_num - 1,
            items=self._results,
            errors=self._errors,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            config=self.config.model_dump(),
        )

    def export_csv(self, filepath: str) -> None:
        """Export results to CSV.

        Args:
            filepath: Output file path.
        """
        if not self._results:
            return

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            if self._results:
                writer = csv.DictWriter(f, fieldnames=self._results[0].to_dict().keys())
                writer.writeheader()
                for item in self._results:
                    writer.writerow(item.to_dict())

    def export_sqlite(self, filepath: str, table_name: str = "scraped_items") -> None:
        """Export results to SQLite.

        Args:
            filepath: Database file path.
            table_name: Table name.
        """
        if not self._results:
            return

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(filepath)
        cursor = conn.cursor()

        # Create table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                description TEXT,
                price REAL,
                currency TEXT,
                image_url TEXT,
                category TEXT,
                brand TEXT,
                sku TEXT,
                availability TEXT,
                rating REAL,
                review_count INTEGER,
                scraped_at TEXT,
                metadata TEXT
            )
        """)

        # Insert data
        for item in self._results:
            cursor.execute(f"""
                INSERT INTO {table_name}
                (url, title, description, price, currency, image_url, category,
                 brand, sku, availability, rating, review_count, scraped_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.url, item.title, item.description, item.price, item.currency,
                item.image_url, item.category, item.brand, item.sku,
                item.availability, item.rating, item.review_count,
                item.scraped_at.isoformat(), str(item.metadata)
            ))

        conn.commit()
        conn.close()

    def generate_report(self, filepath: str, format: str = "html") -> None:
        """Generate scraping report.

        Args:
            filepath: Output file path.
            format: Report format (html or md).
        """
        result = ScrapeResult(
            site_name=self.config.name,
            total_items=len(self._results),
            total_pages=0,
            items=self._results,
            errors=self._errors,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            config=self.config.model_dump(),
        )

        generator = ReportGenerator(result)

        if format == "html":
            generator.generate_html(filepath)
        elif format == "md":
            generator.generate_markdown(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
