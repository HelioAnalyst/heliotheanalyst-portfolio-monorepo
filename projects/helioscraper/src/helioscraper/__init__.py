"""HelioScraper - Configurable web scraping framework."""

from helioscraper.scraper import Scraper
from helioscraper.models import ScrapedItem, ScrapeResult

__version__ = "1.0.0"
__all__ = ["Scraper", "ScrapedItem", "ScrapeResult"]
