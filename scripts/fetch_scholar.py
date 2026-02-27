#!/usr/bin/env python3
"""
Fetch Google Scholar metrics for Prof. Alberto Ferreira De Souza.

This script fetches publication metrics from Google Scholar.
It first tries using the scholarly library, and falls back to
direct HTTP scraping if scholarly fails (e.g., due to CAPTCHA).

Usage:
    python fetch_scholar.py

Output:
    ../src/data/scholar_metrics.json
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCHOLAR_ID = "gvb7W0IAAAAJ"
OUTPUT_FILE = Path(__file__).parent.parent / "src" / "data" / "scholar_metrics.json"
TOP_N_PUBLICATIONS = 10
MAX_RETRIES = 3
RETRY_DELAY = 5


def fetch_with_scholarly():
    """Try fetching data using the scholarly library."""
    try:
        from scholarly import scholarly
    except ImportError:
        print("  scholarly library not installed, skipping")
        return None

    print("  Trying scholarly library...")
    try:
        author = scholarly.search_author_id(SCHOLAR_ID)
        if author is None:
            print("  scholarly returned None")
            return None
        author = scholarly.fill(author, sections=['basics', 'indices', 'publications'])
        
        citations = author.get('citedby', 0)
        h_index = author.get('hindex', 0)
        i10_index = author.get('i10index', 0)
        
        publications = author.get('publications', [])
        sorted_pubs = sorted(publications, key=lambda x: x.get('num_citations', 0), reverse=True)
        
        top_pubs = []
        for pub in sorted_pubs[:TOP_N_PUBLICATIONS]:
            try:
                filled_pub = scholarly.fill(pub)
            except:
                filled_pub = pub
            
            bib = filled_pub.get('bib', {})
            top_pubs.append({
                'title': bib.get('title', 'Unknown Title'),
                'authors': bib.get('author', 'Unknown Authors'),
                'venue': bib.get('venue', bib.get('journal', bib.get('booktitle', 'Unknown Venue'))),
                'year': int(bib.get('pub_year', 0)) if bib.get('pub_year') else None,
                'citations': filled_pub.get('num_citations', 0),
                'url': filled_pub.get('pub_url', f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_ID}")
            })
        
        return {
            'name': author.get('name', 'Alberto Ferreira De Souza'),
            'affiliation': author.get('affiliation', 'Universidade Federal do Espírito Santo'),
            'citations': citations,
            'h_index': h_index,
            'i10_index': i10_index,
            'top_publications': top_pubs
        }
    except Exception as e:
        print(f"  scholarly failed: {e}")
        return None


def fetch_with_selenium():
    """Fetch data using Selenium with Chrome browser (visible, using user profile)."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from bs4 import BeautifulSoup
    except ImportError:
        print("  selenium/beautifulsoup4 not installed, skipping")
        return None

    print("  Trying Selenium with Chrome (visible browser)...")
    print("  A Chrome window will open briefly to fetch Scholar data.")
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--lang=en-US')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        url = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
        driver.get(url)
        time.sleep(3)
        
        page_source = driver.page_source
        
        if 'captcha' in page_source.lower() or 'unusual traffic' in page_source.lower():
            print("  CAPTCHA detected. Please solve it in the browser window...")
            print("  Waiting up to 60 seconds for you to solve the CAPTCHA...")
            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.ID, 'gsc_prf_in'))
                )
                page_source = driver.page_source
                print("  CAPTCHA solved! Continuing...")
            except:
                print("  Timeout waiting for CAPTCHA. Skipping.")
                return None
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract name
        name_el = soup.select_one('#gsc_prf_in')
        name = name_el.text.strip() if name_el else 'Alberto Ferreira De Souza'
        
        # Extract affiliation
        aff_el = soup.select_one('.gsc_prf_il')
        affiliation = aff_el.text.strip() if aff_el else 'Universidade Federal do Espírito Santo'
        
        # Extract metrics
        index_cells = soup.select('#gsc_rsb_st td.gsc_rsb_std')
        citations = int(index_cells[0].text) if len(index_cells) > 0 else 0
        h_index = int(index_cells[2].text) if len(index_cells) > 2 else 0
        i10_index = int(index_cells[4].text) if len(index_cells) > 4 else 0
        
        if citations == 0 and h_index == 0:
            print("  Could not extract metrics from page")
            return None
        
        # Now fetch sorted by citations
        url_sorted = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en&sortby=cited&cstart=0&pagesize=100"
        time.sleep(2)
        driver.get(url_sorted)
        time.sleep(3)
        
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')
        pub_rows = soup2.select('#gsc_a_b .gsc_a_tr')
        
        # If sorted page didn't work, use original page
        if not pub_rows:
            pub_rows = soup.select('#gsc_a_b .gsc_a_tr')
        
        pubs = []
        for row in pub_rows:
            title_el = row.select_one('.gsc_a_at')
            cite_el = row.select_one('.gsc_a_ac')
            year_el = row.select_one('.gsc_a_y span')
            gray_els = row.select('.gs_gray')
            
            if title_el:
                title = title_el.text.strip()
                pub_url_rel = title_el.get('href', '')
                pub_url = f"https://scholar.google.com{pub_url_rel}" if pub_url_rel else ''
                cite_count = int(cite_el.text) if cite_el and cite_el.text.strip().isdigit() else 0
                year = int(year_el.text) if year_el and year_el.text.strip().isdigit() else None
                authors = gray_els[0].text.strip() if len(gray_els) > 0 else ''
                venue = gray_els[1].text.strip() if len(gray_els) > 1 else ''
                
                pubs.append({
                    'title': title,
                    'authors': authors,
                    'venue': venue,
                    'year': year,
                    'citations': cite_count,
                    'url': pub_url
                })
        
        pubs.sort(key=lambda x: x['citations'], reverse=True)
        top_pubs = pubs[:TOP_N_PUBLICATIONS]
        
        return {
            'name': name,
            'affiliation': affiliation,
            'citations': citations,
            'h_index': h_index,
            'i10_index': i10_index,
            'top_publications': top_pubs
        }
    except Exception as e:
        print(f"  Selenium failed: {e}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def fetch_with_requests():
    """Fallback: fetch data directly from Google Scholar using requests + BeautifulSoup."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("  requests/beautifulsoup4 not installed, skipping")
        return None

    print("  Trying direct HTTP scraping...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Fetch the author page
    url = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
    
    session = requests.Session()
    session.headers.update(headers)
    
    resp = session.get(url, timeout=30)
    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code}")
        return None
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Check for CAPTCHA
    if 'captcha' in resp.text.lower() or 'unusual traffic' in resp.text.lower():
        print("  Google Scholar returned a CAPTCHA page")
        return None
    
    # Extract name
    name_el = soup.select_one('#gsc_prf_in')
    name = name_el.text.strip() if name_el else 'Alberto Ferreira De Souza'
    
    # Extract affiliation
    aff_el = soup.select_one('.gsc_prf_il')
    affiliation = aff_el.text.strip() if aff_el else 'Universidade Federal do Espírito Santo'
    
    # Extract metrics from the table
    index_cells = soup.select('#gsc_rsb_st td.gsc_rsb_std')
    citations = int(index_cells[0].text) if len(index_cells) > 0 else 0
    h_index = int(index_cells[2].text) if len(index_cells) > 2 else 0
    i10_index = int(index_cells[4].text) if len(index_cells) > 4 else 0
    
    if citations == 0 and h_index == 0:
        print("  Could not extract metrics (page may be blocked)")
        return None
    
    # Extract publications from the page
    top_pubs = []
    pub_rows = soup.select('#gsc_a_b .gsc_a_tr')
    
    pubs_with_citations = []
    for row in pub_rows:
        title_el = row.select_one('.gsc_a_at')
        cite_el = row.select_one('.gsc_a_ac')
        year_el = row.select_one('.gsc_a_y span')
        gray_els = row.select('.gs_gray')
        
        if title_el:
            title = title_el.text.strip()
            pub_url_relative = title_el.get('href', '')
            pub_url = f"https://scholar.google.com{pub_url_relative}" if pub_url_relative else ''
            cite_count = int(cite_el.text) if cite_el and cite_el.text.strip().isdigit() else 0
            year = int(year_el.text) if year_el and year_el.text.strip().isdigit() else None
            authors = gray_els[0].text.strip() if len(gray_els) > 0 else ''
            venue = gray_els[1].text.strip() if len(gray_els) > 1 else ''
            
            pubs_with_citations.append({
                'title': title,
                'authors': authors,
                'venue': venue,
                'year': year,
                'citations': cite_count,
                'url': pub_url
            })
    
    # Sort by citations and take top N
    pubs_with_citations.sort(key=lambda x: x['citations'], reverse=True)
    top_pubs = pubs_with_citations[:TOP_N_PUBLICATIONS]
    
    # The default page may not show all publications sorted by citations
    # Try fetching sorted by citations
    if len(top_pubs) < TOP_N_PUBLICATIONS:
        print(f"  Found only {len(top_pubs)} publications on main page")
    
    # Also try to fetch with sortby=pubdate to get more publications
    url_sorted = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en&sortby=cited&cstart=0&pagesize=100"
    try:
        time.sleep(2)
        resp2 = session.get(url_sorted, timeout=30)
        if resp2.status_code == 200 and 'captcha' not in resp2.text.lower():
            soup2 = BeautifulSoup(resp2.text, 'html.parser')
            pub_rows2 = soup2.select('#gsc_a_b .gsc_a_tr')
            
            for row in pub_rows2:
                title_el = row.select_one('.gsc_a_at')
                cite_el = row.select_one('.gsc_a_ac')
                year_el = row.select_one('.gsc_a_y span')
                gray_els = row.select('.gs_gray')
                
                if title_el:
                    title = title_el.text.strip()
                    pub_url_relative = title_el.get('href', '')
                    pub_url = f"https://scholar.google.com{pub_url_relative}" if pub_url_relative else ''
                    cite_count = int(cite_el.text) if cite_el and cite_el.text.strip().isdigit() else 0
                    year = int(year_el.text) if year_el and year_el.text.strip().isdigit() else None
                    authors = gray_els[0].text.strip() if len(gray_els) > 0 else ''
                    venue = gray_els[1].text.strip() if len(gray_els) > 1 else ''
                    
                    # Avoid duplicates
                    existing_titles = {p['title'] for p in pubs_with_citations}
                    if title not in existing_titles:
                        pubs_with_citations.append({
                            'title': title,
                            'authors': authors,
                            'venue': venue,
                            'year': year,
                            'citations': cite_count,
                            'url': pub_url
                        })
            
            pubs_with_citations.sort(key=lambda x: x['citations'], reverse=True)
            top_pubs = pubs_with_citations[:TOP_N_PUBLICATIONS]
    except Exception as e:
        print(f"  Warning: Could not fetch sorted publications: {e}")
    
    return {
        'name': name,
        'affiliation': affiliation,
        'citations': citations,
        'h_index': h_index,
        'i10_index': i10_index,
        'top_publications': top_pubs
    }


def load_existing_metrics(output_path):
    """Load existing metrics file if it exists."""
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_metrics(data, output_path):
    """Save metrics data to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Metrics saved to: {output_path}")


def main():
    """Main function to fetch and save Scholar metrics."""
    print("=" * 60)
    print("Google Scholar Metrics Fetcher")
    print("=" * 60)
    
    result = None
    
    # Strategy 1: Try scholarly library (quick, 1 attempt)
    print(f"\nStrategy 1: scholarly library")
    result = fetch_with_scholarly()
    
    # Strategy 2: Try Selenium with visible Chrome (can handle CAPTCHA)
    if result is None:
        print(f"\nStrategy 2: Selenium Chrome (visible browser)")
        result = fetch_with_selenium()
    
    # Strategy 3: Fallback to direct HTTP scraping
    if result is None:
        print(f"\nStrategy 3: direct HTTP scraping")
        result = fetch_with_requests()
    
    # Process results
    if result is not None:
        print(f"\nMetrics found:")
        print(f"  - Citations: {result['citations']:,}")
        print(f"  - h-index: {result['h_index']}")
        print(f"  - i10-index: {result['i10_index']}")
        print(f"  - Publications: {len(result['top_publications'])}")
        
        if result['top_publications']:
            print(f"\nTop publications:")
            for i, pub in enumerate(result['top_publications'], 1):
                title = pub['title'][:60]
                print(f"  {i}. {title}... ({pub['citations']:,} citations)")
        
        output_data = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'author': {
                'name': result['name'],
                'affiliation': result['affiliation'],
                'scholar_id': SCHOLAR_ID
            },
            'metrics': {
                'citations': result['citations'],
                'h_index': result['h_index'],
                'i10_index': result['i10_index']
            },
            'top_publications': result['top_publications']
        }
        
        save_metrics(output_data, OUTPUT_FILE)
        
        print("\n" + "=" * 60)
        print("SUCCESS: Metrics updated!")
        print("=" * 60)
        return 0
    
    # All strategies failed
    print(f"\nERROR: All strategies failed")
    print("Falling back to existing data...")
    
    existing = load_existing_metrics(OUTPUT_FILE)
    if existing:
        last = existing.get('last_updated', 'unknown')
        print(f"Using cached data from: {last}")
        return 0
    else:
        print("No existing data found.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
