"""Command-line interface for HelioScraper."""

import argparse
import sys

from helioscraper.config_loader import ConfigLoader, get_default_configs
from helioscraper.scraper import Scraper


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HelioScraper - Configurable web scraping framework",
    )
    parser.add_argument(
        "--config",
        "-c",
        required=True,
        help="Config name or path",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="outputs/scraped_data.csv",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["csv", "sqlite", "both"],
        default="csv",
        help="Output format",
    )
    parser.add_argument(
        "--report",
        "-r",
        help="Generate report (HTML or MD)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock browser (no Chrome needed)",
    )
    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="List available configs",
    )

    args = parser.parse_args()

    if args.list_configs:
        loader = ConfigLoader()
        configs = loader.list_configs()
        print("Available configs:")
        for config in configs:
            print(f"  - {config}")
        return

    # Run scraper
    print(f"Loading config: {args.config}")
    scraper = Scraper.from_config(args.config, mock_mode=args.mock)

    print(f"Starting scrape of: {scraper.config.base_url}")
    result = scraper.scrape()

    print(f"\nScraping complete!")
    print(f"  Items scraped: {result.total_items}")
    print(f"  Pages processed: {result.total_pages}")
    print(f"  Duration: {result.duration_seconds:.2f}s")
    print(f"  Errors: {len(result.errors)}")

    # Export
    if args.format in ("csv", "both"):
        csv_path = args.output if args.output.endswith(".csv") else args.output + ".csv"
        scraper.export_csv(csv_path)
        print(f"  CSV exported: {csv_path}")

    if args.format in ("sqlite", "both"):
        db_path = args.output.replace(".csv", ".db") if args.output.endswith(".csv") else args.output + ".db"
        scraper.export_sqlite(db_path)
        print(f"  SQLite exported: {db_path}")

    # Generate report
    if args.report:
        format = "html" if args.report.endswith(".html") else "md"
        scraper.generate_report(args.report, format=format)
        print(f"  Report generated: {args.report}")


if __name__ == "__main__":
    main()
