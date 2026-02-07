#!/usr/bin/env python3
"""
Generate HTML page with updated Scholar metrics.

This script reads the scholar_metrics.json file and updates the HTML page
with the latest metrics. It's designed to be run after fetch_scholar.py
as part of the GitHub Actions workflow or before deploy.

Usage:
    python generate_html.py

The script modifies the index.html file in place, updating:
- Citation count
- h-index
- i10-index  
- Last updated date
- Top 10 publications with links
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from html import escape


# Configuration
METRICS_FILE = Path(__file__).parent.parent / "src" / "data" / "scholar_metrics.json"
HTML_FILE = Path(__file__).parent.parent / "src" / "alberto" / "index.html"


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


def generate_publication_html(pub: dict) -> str:
    """
    Generate HTML for a single publication.
    
    Args:
        pub: Publication dictionary with title, authors, venue, year, citations, url
        
    Returns:
        HTML string for the publication card
    """
    title = escape(pub.get('title', 'Unknown Title'))
    authors = escape(pub.get('authors', 'Unknown Authors'))
    venue = escape(pub.get('venue', 'Unknown Venue'))
    year = pub.get('year', '')
    citations = pub.get('citations', 0)
    url = pub.get('url', '#')
    
    # Format venue with year
    venue_text = f"{venue}, {year}" if year else venue
    
    return f'''        <div class="publication-item p-6 bg-white rounded-xl shadow-sm border hover:shadow-md transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 mb-2">
                <a href="{url}" target="_blank" rel="noopener" class="hover:text-blue-600 transition-colors">
                  {title}
                </a>
              </h3>
              <p class="text-sm text-gray-600 mb-1">{authors}</p>
              <p class="text-sm text-gray-500">{venue_text}</p>
            </div>
            <div class="ml-4 text-right flex-shrink-0">
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {format_number(citations)} citations
              </span>
            </div>
          </div>
        </div>'''


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
    
    # Generate publications HTML
    publications = metrics.get('top_publications', [])
    if publications:
        pubs_html = '\n        \n'.join(generate_publication_html(pub) for pub in publications)
        
        # Replace the publications list content
        # Match from <div id="publications-list" ...> to the closing </div> before <!-- Publication Profiles -->
        pattern = r'(<div id="publications-list"[^>]*>)\s*(?:.*?)(</div>\s*\n\s*<!-- Publication Profiles -->)'
        replacement = rf'\1\n{pubs_html}\n      \2'
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
    print(f"  - Publications: {len(metrics.get('top_publications', []))}")
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
