"""Report generator for scraping results."""

from datetime import datetime
from pathlib import Path
from typing import Any

from helioscraper.models import ScrapeResult


class ReportGenerator:
    """Generate HTML and Markdown reports from scraping results."""

    def __init__(self, result: ScrapeResult) -> None:
        """Initialize report generator.

        Args:
            result: Scraping result.
        """
        self.result = result

    def generate_html(self, filepath: str) -> None:
        """Generate HTML report.

        Args:
            filepath: Output file path.
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        html = self._render_html_template()

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

    def generate_markdown(self, filepath: str) -> None:
        """Generate Markdown report.

        Args:
            filepath: Output file path.
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        md = self._render_markdown_template()

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

    def _render_html_template(self) -> str:
        """Render HTML template.

        Returns:
            HTML content.
        """
        items_html = ""
        for item in self.result.items[:50]:  # Show first 50
            items_html += f"""
            <tr>
                <td>{item.title or 'N/A'}</td>
                <td>{item.price or 'N/A'}</td>
                <td><a href="{item.url}" target="_blank">Link</a></td>
                <td>{item.scraped_at.strftime('%Y-%m-%d %H:%M')}</td>
            </tr>
            """

        errors_html = ""
        for error in self.result.errors[:10]:  # Show first 10
            errors_html += f"<li>{error}</li>"

        duration = self.result.duration_seconds
        duration_str = f"{duration:.2f}s" if duration else "N/A"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scraping Report - {self.result.site_name}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{ color: #2c3e50; margin-bottom: 10px; }}
        h2 {{ color: #34495e; margin: 30px 0 15px; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        .stat-card.error {{ border-left-color: #e74c3c; }}
        .stat-card.success {{ border-left-color: #27ae60; }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{ background: #f8f9fa; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .error-list {{
            background: #fdf2f2;
            border: 1px solid #fecaca;
            border-radius: 6px;
            padding: 15px;
            color: #991b1b;
        }}
        .error-list li {{ margin: 5px 0; }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Scraping Report</h1>
        <p class="timestamp">Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>

        <h2>Site Information</h2>
        <p><strong>Site:</strong> {self.result.site_name}</p>
        <p><strong>Started:</strong> {self.result.started_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Completed:</strong> {self.result.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.result.completed_at else 'N/A'}</p>

        <h2>Summary</h2>
        <div class="summary">
            <div class="stat-card success">
                <div class="stat-value">{self.result.total_items}</div>
                <div class="stat-label">Items Scraped</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{self.result.total_pages}</div>
                <div class="stat-label">Pages Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{duration_str}</div>
                <div class="stat-label">Duration</div>
            </div>
            <div class="stat-card {'error' if self.result.errors else ''}">
                <div class="stat-value">{len(self.result.errors)}</div>
                <div class="stat-label">Errors</div>
            </div>
        </div>

        <h2>Scraped Items</h2>
        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Price</th>
                    <th>URL</th>
                    <th>Scraped At</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>

        {'<h2>Errors</h2><ul class="error-list">' + errors_html + '</ul>' if self.result.errors else ''}
    </div>
</body>
</html>"""

    def _render_markdown_template(self) -> str:
        """Render Markdown template.

        Returns:
            Markdown content.
        """
        duration = self.result.duration_seconds
        duration_str = f"{duration:.2f}s" if duration else "N/A"

        items_md = ""
        for item in self.result.items[:30]:
            items_md += f"| {item.title or 'N/A'} | {item.price or 'N/A'} | [Link]({item.url}) |\n"

        errors_md = ""
        for error in self.result.errors[:10]:
            errors_md += f"- {error}\n"

        return f"""# Scraping Report

## Site Information

- **Site:** {self.result.site_name}
- **Started:** {self.result.started_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Completed:** {self.result.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.result.completed_at else 'N/A'}

## Summary

| Metric | Value |
|--------|-------|
| Items Scraped | {self.result.total_items} |
| Pages Processed | {self.result.total_pages} |
| Duration | {duration_str} |
| Errors | {len(self.result.errors)} |

## Scraped Items

| Title | Price | URL |
|-------|-------|-----|
{items_md}

{'## Errors\n\n' + errors_md if self.result.errors else ''}

---

*Report generated by HelioScraper*
"""
