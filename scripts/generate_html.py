#!/usr/bin/env python3
"""
Generate HTML page with updated Scholar metrics.

This script reads the scholar_metrics.json file and updates the HTML page
with the latest metrics. It's designed to be run after fetch_scholar.py
as part of the GitHub Actions workflow.

Usage:
    python generate_html.py

The script modifies the index.html file in place, updating:
- Citation count
- h-index
- i10-index  
- Last updated date
- Top publications (if dynamic content is enabled)
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path


# Configuration
METRICS_FILE = Path(__file__).parent.parent / "src" / "data" / "scholar_metrics.json"
HTML_FILE = Path(__file__).parent.parent / "src" / "index.php" / "Prof._Dr._Alberto_Ferreira_De_Souza" / "index.html"


def load_metrics() -> dict:
    """Load metrics from JSON file."""
    if not METRICS_FILE.exists():
        print(f"Error: Metrics file not found: {METRICS_FILE}")
        sys.exit(1)
    
    with open(METRICS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_number(num: int) -> str:
    """Format number with comma separators."""
    return f"{num:,}"


def update_html(html_content: str, metrics: dict) -> str:
    """
    Update HTML content with new metrics.
    
    Args:
        html_content: Original HTML content
        metrics: Metrics dictionary from JSON
        
    Returns:
        Updated HTML content
    """
    citations = metrics['metrics']['citations']
    h_index = metrics['metrics']['h_index']
    i10_index = metrics['metrics']['i10_index']
    
    # Update data-value attributes and displayed values
    # Citations
    html_content = re.sub(
        r'id="citations-count"[^>]*data-value="\d+"[^>]*>\d[\d,]*',
        f'id="citations-count" class="metric-value" data-value="{citations}">{format_number(citations)}',
        html_content
    )
    
    # h-index
    html_content = re.sub(
        r'id="h-index"[^>]*data-value="\d+"[^>]*>\d+',
        f'id="h-index" class="metric-value" data-value="{h_index}">{h_index}',
        html_content
    )
    
    # i10-index
    html_content = re.sub(
        r'id="i10-index"[^>]*data-value="\d+"[^>]*>\d+',
        f'id="i10-index" class="metric-value" data-value="{i10_index}">{i10_index}',
        html_content
    )
    
    # Update last updated date
    last_updated = datetime.fromisoformat(metrics['last_updated'].replace('Z', '+00:00'))
    formatted_date = last_updated.strftime('%B %Y')
    html_content = re.sub(
        r'Last updated: [^<]+',
        f'Last updated: {formatted_date}',
        html_content
    )
    
    # Update publication citation counts
    for pub in metrics.get('top_publications', []):
        title_escaped = re.escape(pub['title'][:30])
        citations = pub['citations']
        
        # Find and update citation badge for this publication
        pattern = rf'({title_escaped}.*?)\d[\d,]* citations'
        replacement = rf'\g<1>{format_number(citations)} citations'
        html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    return html_content


def main():
    """Main function to update HTML with metrics."""
    print("=" * 60)
    print("HTML Generator - Updating page with Scholar metrics")
    print("=" * 60)
    print()
    
    # Load metrics
    print(f"Loading metrics from: {METRICS_FILE}")
    metrics = load_metrics()
    
    print(f"Metrics loaded:")
    print(f"  - Citations: {metrics['metrics']['citations']:,}")
    print(f"  - h-index: {metrics['metrics']['h_index']}")
    print(f"  - i10-index: {metrics['metrics']['i10_index']}")
    print(f"  - Last updated: {metrics['last_updated']}")
    print()
    
    # Check if HTML file exists
    if not HTML_FILE.exists():
        print(f"Error: HTML file not found: {HTML_FILE}")
        sys.exit(1)
    
    # Read HTML
    print(f"Reading HTML from: {HTML_FILE}")
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update HTML
    print("Updating HTML with new metrics...")
    updated_html = update_html(html_content, metrics)
    
    # Write updated HTML
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    print(f"HTML updated successfully: {HTML_FILE}")
    print()
    print("=" * 60)
    print("SUCCESS: Page updated with latest metrics!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
