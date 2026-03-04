"""Pydantic models for HelioScraper."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ScrapedItem(BaseModel):
    """Single scraped item."""

    model_config = ConfigDict(frozen=True)

    id: Optional[str] = None
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    image_url: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    availability: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()


class ScrapedPage(BaseModel):
    """Scraped page with multiple items."""

    model_config = ConfigDict(frozen=True)

    url: str
    items: list[ScrapedItem] = Field(default_factory=list)
    page_number: int = 1
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    html_snapshot: Optional[str] = None


class ScrapeResult(BaseModel):
    """Result of a scraping operation."""

    model_config = ConfigDict(frozen=True)

    site_name: str
    total_items: int = 0
    total_pages: int = 0
    items: list[ScrapedItem] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    config: dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate operation duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = len(self.items) + len(self.errors)
        if total == 0:
            return 100.0
        return (len(self.items) / total) * 100

    def get_unique_items(self) -> list[ScrapedItem]:
        """Get unique items by URL."""
        seen = set()
        unique = []
        for item in self.items:
            if item.url not in seen:
                seen.add(item.url)
                unique.append(item)
        return unique


class SiteConfig(BaseModel):
    """Site scraping configuration."""

    model_config = ConfigDict(frozen=True)

    name: str
    base_url: str
    selectors: dict[str, str]
    pagination: dict[str, Any] = Field(default_factory=dict)
    delays: dict[str, float] = Field(default_factory=lambda: {"min": 1.0, "max": 3.0})
    user_agent_rotation: bool = True
    respect_robots_txt: bool = True
    max_pages: int = 10
    timeout: int = 30
    headers: dict[str, str] = Field(default_factory=dict)
    cookies: dict[str, str] = Field(default_factory=dict)


class ReportData(BaseModel):
    """Data for generating reports."""

    model_config = ConfigDict(frozen=True)

    result: ScrapeResult
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    template: str = "default"
