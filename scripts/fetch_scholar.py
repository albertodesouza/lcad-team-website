#!/usr/bin/env python3
"""
Fetch Google Scholar metrics for Prof. Alberto Ferreira De Souza.

This script uses the scholarly library to fetch publication metrics
from Google Scholar and saves them to a JSON file.

Usage:
    python fetch_scholar.py

Output:
    ../src/data/scholar_metrics.json
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from scholarly import scholarly, ProxyGenerator
except ImportError:
    print("Error: scholarly library not found.")
    print("Please install it with: pip install scholarly")
    sys.exit(1)


# Configuration
SCHOLAR_ID = "gvb7W0IAAAAJ"  # Prof. Alberto's Google Scholar ID
OUTPUT_FILE = Path(__file__).parent.parent / "src" / "data" / "scholar_metrics.json"
TOP_N_PUBLICATIONS = 5
USE_PROXY = False  # Set to True if you're getting blocked by Google


def setup_proxy():
    """Set up a proxy to avoid being blocked by Google Scholar."""
    if USE_PROXY:
        print("Setting up proxy...")
        pg = ProxyGenerator()
        success = pg.FreeProxies()
        if success:
            scholarly.use_proxy(pg)
            print("Proxy configured successfully")
        else:
            print("Warning: Could not set up proxy, proceeding without it")


def fetch_author_data(scholar_id: str) -> dict:
    """
    Fetch author data from Google Scholar.
    
    Args:
        scholar_id: Google Scholar author ID
        
    Returns:
        Dictionary containing author information and metrics
    """
    print(f"Fetching data for author ID: {scholar_id}")
    
    try:
        # Search for author by ID
        author = scholarly.search_author_id(scholar_id)
        
        # Fill in all available information
        author = scholarly.fill(author, sections=['basics', 'indices', 'publications'])
        
        return author
    except Exception as e:
        print(f"Error fetching author data: {e}")
        raise


def extract_metrics(author: dict) -> dict:
    """
    Extract relevant metrics from author data.
    
    Args:
        author: Author dictionary from scholarly
        
    Returns:
        Dictionary with extracted metrics
    """
    # Get citation indices
    citations = author.get('citedby', 0)
    h_index = author.get('hindex', 0)
    i10_index = author.get('i10index', 0)
    
    return {
        'citations': citations,
        'h_index': h_index,
        'i10_index': i10_index
    }


def extract_top_publications(author: dict, top_n: int = 5) -> list:
    """
    Extract top publications sorted by citation count.
    
    Args:
        author: Author dictionary from scholarly
        top_n: Number of top publications to extract
        
    Returns:
        List of publication dictionaries
    """
    publications = author.get('publications', [])
    
    # Sort by citation count (descending)
    sorted_pubs = sorted(
        publications,
        key=lambda x: x.get('num_citations', 0),
        reverse=True
    )
    
    top_pubs = []
    for pub in sorted_pubs[:top_n]:
        # Try to fill publication details
        try:
            filled_pub = scholarly.fill(pub)
        except:
            filled_pub = pub
        
        bib = filled_pub.get('bib', {})
        
        pub_data = {
            'title': bib.get('title', 'Unknown Title'),
            'authors': bib.get('author', 'Unknown Authors'),
            'venue': bib.get('venue', bib.get('journal', bib.get('booktitle', 'Unknown Venue'))),
            'year': int(bib.get('pub_year', 0)) if bib.get('pub_year') else None,
            'citations': filled_pub.get('num_citations', 0),
            'url': filled_pub.get('pub_url', f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_ID}")
        }
        
        top_pubs.append(pub_data)
    
    return top_pubs


def save_metrics(data: dict, output_path: Path):
    """
    Save metrics data to JSON file.
    
    Args:
        data: Dictionary containing all metrics data
        output_path: Path to output JSON file
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON with nice formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Metrics saved to: {output_path}")


def load_existing_metrics(output_path: Path) -> dict:
    """
    Load existing metrics file if it exists.
    
    Args:
        output_path: Path to metrics JSON file
        
    Returns:
        Existing metrics dictionary or empty dict
    """
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def main():
    """Main function to fetch and save Scholar metrics."""
    print("=" * 60)
    print("Google Scholar Metrics Fetcher")
    print("=" * 60)
    print()
    
    # Set up proxy if needed
    setup_proxy()
    
    try:
        # Fetch author data
        author = fetch_author_data(SCHOLAR_ID)
        
        # Extract metrics
        metrics = extract_metrics(author)
        print(f"\nMetrics found:")
        print(f"  - Citations: {metrics['citations']:,}")
        print(f"  - h-index: {metrics['h_index']}")
        print(f"  - i10-index: {metrics['i10_index']}")
        
        # Extract top publications
        print(f"\nFetching top {TOP_N_PUBLICATIONS} publications...")
        top_pubs = extract_top_publications(author, TOP_N_PUBLICATIONS)
        
        print("Top publications:")
        for i, pub in enumerate(top_pubs, 1):
            print(f"  {i}. {pub['title'][:60]}... ({pub['citations']:,} citations)")
        
        # Prepare output data
        output_data = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'author': {
                'name': author.get('name', 'Alberto Ferreira De Souza'),
                'affiliation': author.get('affiliation', 'Universidade Federal do Espírito Santo'),
                'scholar_id': SCHOLAR_ID
            },
            'metrics': metrics,
            'top_publications': top_pubs
        }
        
        # Save to file
        save_metrics(output_data, OUTPUT_FILE)
        
        print("\n" + "=" * 60)
        print("SUCCESS: Metrics updated successfully!")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: Failed to fetch metrics: {e}")
        print("\nFalling back to existing data if available...")
        
        existing = load_existing_metrics(OUTPUT_FILE)
        if existing:
            print("Existing metrics file found, keeping current data.")
            return 0
        else:
            print("No existing metrics file found.")
            return 1


if __name__ == '__main__':
    sys.exit(main())
