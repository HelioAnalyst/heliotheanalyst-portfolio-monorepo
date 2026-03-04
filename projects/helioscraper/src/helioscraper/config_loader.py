"""Configuration loader for site scraping configs."""

import os
from pathlib import Path
from typing import Any

import yaml

from helioscraper.models import SiteConfig


class ConfigLoader:
    """Load site configurations from YAML files."""

    def __init__(self, config_dir: str = "configs/sites") -> None:
        """Initialize config loader.

        Args:
            config_dir: Directory containing site configs.
        """
        self.config_dir = Path(config_dir)

    def list_configs(self) -> list[str]:
        """List available config files.

        Returns:
            List of config file names.
        """
        if not self.config_dir.exists():
            return []

        return [
            f.stem
            for f in self.config_dir.glob("*.yml")
        ] + [
            f.stem
            for f in self.config_dir.glob("*.yaml")
        ]

    def load_config(self, name: str) -> SiteConfig:
        """Load site configuration.

        Args:
            name: Config name (without extension).

        Returns:
            Site configuration.

        Raises:
            FileNotFoundError: If config not found.
            ValueError: If config is invalid.
        """
        # Try yaml then yml
        config_path = self.config_dir / f"{name}.yaml"
        if not config_path.exists():
            config_path = self.config_dir / f"{name}.yml"

        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {name}")

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        return SiteConfig(**data)

    def load_all_configs(self) -> dict[str, SiteConfig]:
        """Load all available configs.

        Returns:
            Dictionary of config name to SiteConfig.
        """
        configs = {}
        for name in self.list_configs():
            try:
                configs[name] = self.load_config(name)
            except Exception as e:
                print(f"Failed to load config {name}: {e}")
        return configs

    def save_config(self, name: str, config: SiteConfig) -> None:
        """Save site configuration.

        Args:
            name: Config name.
            config: Configuration to save.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_path = self.config_dir / f"{name}.yaml"

        with open(config_path, "w") as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False)


def get_default_configs() -> dict[str, dict[str, Any]]:
    """Get default site configurations for demo.

    Returns:
        Dictionary of default configs.
    """
    return {
        "demo_ecommerce": {
            "name": "Demo E-commerce Site",
            "base_url": "https://example-ecommerce.com",
            "selectors": {
                "product_list": ".product-card",
                "title": ".product-title",
                "price": ".product-price",
                "image": ".product-image@src",
                "link": ".product-link@href",
                "description": ".product-description",
            },
            "pagination": {
                "enabled": True,
                "selector": ".pagination .next",
                "max_pages": 5,
            },
            "delays": {
                "min": 1.0,
                "max": 3.0,
            },
            "user_agent_rotation": True,
            "max_pages": 3,
        },
        "demo_news": {
            "name": "Demo News Site",
            "base_url": "https://example-news.com",
            "selectors": {
                "article_list": ".article-item",
                "title": ".article-title",
                "summary": ".article-summary",
                "link": ".article-link@href",
                "author": ".article-author",
                "date": ".article-date",
            },
            "pagination": {
                "enabled": True,
                "selector": ".load-more",
                "max_pages": 10,
            },
            "delays": {
                "min": 0.5,
                "max": 2.0,
            },
            "user_agent_rotation": True,
            "max_pages": 5,
        },
    }
