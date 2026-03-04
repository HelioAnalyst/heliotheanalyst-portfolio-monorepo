#!/usr/bin/env python3
"""Demo script for HelioScraper.

Runs scraper in mock mode - no Chrome browser needed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from helioscraper.config_loader import ConfigLoader
from helioscraper.scraper import Scraper


def main() -> None:
    """Run demo scraping."""
    print("=" * 60)
    print("HelioScraper - Demo")
    print("=" * 60)
    print("Mode: MOCK (no Chrome browser needed)")
    print()

    # List available configs
    loader = ConfigLoader()
    configs = loader.list_configs()

    print("Available configs:")
    for config in configs:
        print(f"  - {config}")
    print()

    # Load and run demo config
    config_name = "demo_ecommerce"
    print(f"Loading config: {config_name}")

    try:
        config = loader.load_config(config_name)
    except FileNotFoundError:
        print(f"Config not found: {config_name}")
        print("Creating default config...")
        from helioscraper.config_loader import get_default_configs
        import yaml

        defaults = get_default_configs()
        Path("configs/sites").mkdir(parents=True, exist_ok=True)
        with open("configs/sites/demo_ecommerce.yml", "w") as f:
            yaml.dump(defaults["demo_ecommerce"], f)
        config = loader.load_config(config_name)

    print(f"Site: {config.name}")
    print(f"Base URL: {config.base_url}")
    print(f"Max pages: {config.max_pages}")
    print(f"User agent rotation: {config.user_agent_rotation}")
    print()

    # Create scraper in mock mode
    scraper = Scraper(config, mock_mode=True)

    print("Starting scrape...")
    print("-" * 40)

    result = scraper.scrape()

    print("-" * 40)
    print("Scraping complete!")
    print()
    print(f"Items scraped: {result.total_items}")
    print(f"Pages processed: {result.total_pages}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Success rate: {result.success_rate:.1f}%")
    print(f"Errors: {len(result.errors)}")
    print()

    # Show sample items
    if result.items:
        print("Sample items:")
        for item in result.items[:3]:
            print(f"  - {item.title}: ${item.price}")
        print()

    # Export to CSV
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "scraped_demo.csv"
    scraper.export_csv(str(csv_path))
    print(f"Exported to CSV: {csv_path}")

    # Export to SQLite
    db_path = output_dir / "scraped_demo.db"
    scraper.export_sqlite(str(db_path))
    print(f"Exported to SQLite: {db_path}")

    # Generate HTML report
    report_path = output_dir / "scraping_report.html"
    scraper.generate_report(str(report_path), format="html")
    print(f"Generated HTML report: {report_path}")

    # Generate Markdown report
    md_path = output_dir / "scraping_report.md"
    scraper.generate_report(str(md_path), format="md")
    print(f"Generated Markdown report: {md_path}")

    print()
    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
