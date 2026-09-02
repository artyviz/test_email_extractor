
"""
NEXOMATE WEBSITE FINDER + EMAIL EXTRACTOR COMBO
================================================
This tool finds business websites AND extracts emails in one run.
Replaces the manual workflow:
  ❌ Old: Explee → get URLs → manually visit each → find email → copy to sheet
  ✅ New: Run this script → get complete leads with emails → auto-save to CSV

Usage:
    # Find solar companies in Texas and extract their emails
    python website_finder.py --query "solar installation companies texas" --output solar_leads.csv

    # Find interior designers in London
    python website_finder.py --query "interior design firms london" --max-results 50 --output design_leads.csv
"""

import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import re
import csv
import json
import time
import random
import argparse
import urllib.parse
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup


@dataclass 
class BusinessResult:
    """Combined website + email result"""
    company_name: str = ""
    website: str = ""
    email: str = ""
    email_score: int = 0
    phone: str = ""
    address: str = ""
    industry: str = ""
    location: str = ""
    source_url: str = ""  # Where we found this business
    search_query: str = ""
    extracted_at: str = ""

    def to_dict(self):
        return asdict(self)


class GoogleMapsFinder:
    """
    Finds business websites from Google Maps / Google Search
    Note: For production scale, use Google Places API ($5 per 1000 requests)
    This version uses search scraping for free operation
    """

    def __init__(self, delay_range=(2, 4)):
        self.delay_range = delay_range
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def search_google(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search Google for business websites
        Returns list of {title, url, snippet}
        """
        print(f"\n🔎 Searching Google for: '{query}'")

        # Construct search URL
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={max_results}"

        try:
            time.sleep(random.uniform(*self.delay_range))
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')
            results = []

            # Parse search results
            for g in soup.find_all('div', class_=re.compile('g|tF2Cxc|Ww4Fm')):
                # Title
                title_elem = g.find('h3')
                title = title_elem.text if title_elem else ""

                # URL
                link_elem = g.find('a')
                url = link_elem['href'] if link_elem and link_elem.has_attr('href') else ""

                # Skip non-website results
                if not url or 'google.com' in url or url.startswith('/'):
                    continue

                # Snippet
                snippet_elem = g.find('div', class_=re.compile('VwiC3b|s3v94d|LyiZd'))
                snippet = snippet_elem.text if snippet_elem else ""

                if url and title:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })

            print(f"   Found {len(results)} search results")
            return results[:max_results]

        except Exception as e:
            print(f"   ❌ Search failed: {e}")
            return []

    def extract_from_search_results(self, results: List[Dict], industry: str = "", location: str = "") -> List[BusinessResult]:
        """
        Takes search results, visits each website, extracts emails
        """
        from email_extractor import EmailExtractor, ExtractedLead

        extractor = EmailExtractor(delay_range=(1, 3), max_workers=3)
        all_results = []

        for idx, result in enumerate(results, 1):
            print(f"\n[{idx}/{len(results)}] Processing: {result['title']}")

            # Extract emails from this website
            leads = extractor.extract_from_website(
                result['url'], 
                industry_hint=industry,
                location_hint=location
            )

            for lead in leads:
                biz = BusinessResult(
                    company_name=lead.company_name or result['title'],
                    website=lead.website,
                    email=lead.email,
                    email_score=lead.email_score,
                    phone=lead.phone,
                    address=lead.address,
                    industry=industry,
                    location=location,
                    source_url=result['url'],
                    search_query=result.get('snippet', ''),
                    extracted_at=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                all_results.append(biz)
                print(f"   ✅ {lead.email} (score: {lead.email_score})")

        return all_results


def main():
    parser = argparse.ArgumentParser(
        description='Nexomate Website Finder + Email Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find solar companies in Texas
  python website_finder.py --query "solar panel installation companies texas" --output solar_tx.csv

  # Find interior designers in London  
  python website_finder.py --query "interior design firms london uk" --max-results 30 --output design_uk.csv

  # Find with specific industry tag
  python website_finder.py --query "roofing contractors miami" --industry "construction" --output roofing_miami.csv
        """
    )

    parser.add_argument('--query', '-q', required=True, help='Search query (e.g., "solar companies texas")')
    parser.add_argument('--output', '-o', default='found_leads.csv', help='Output CSV file')
    parser.add_argument('--max-results', '-m', type=int, default=20, help='Max websites to check')
    parser.add_argument('--industry', help='Industry tag for leads')
    parser.add_argument('--location', help='Location tag for leads')

    args = parser.parse_args()

    print("=" * 70)
    print("  NEXOMATE WEBSITE FINDER + EMAIL EXTRACTOR")
    print("  Automates: Search → Find Website → Extract Email → Save")
    print("=" * 70)

    # Step 1: Find websites
    finder = GoogleMapsFinder()
    search_results = finder.search_google(args.query, args.max_results)

    if not search_results:
        print("\n❌ No results found. Try a different query.")
        return

    # Step 2: Extract emails from each website
    results = finder.extract_from_search_results(
        search_results, 
        industry=args.industry or args.query.split()[0],
        location=args.location or ' '.join(args.query.split()[-2:])
    )

    # Step 3: Save
    if results:
        # Remove duplicates
        seen = set()
        unique = []
        for r in sorted(results, key=lambda x: x.email_score, reverse=True):
            if r.email not in seen:
                seen.add(r.email)
                unique.append(r)

        # Save to CSV
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'company_name', 'website', 'email', 'email_score', 'phone',
                'address', 'industry', 'location', 'source_url', 'search_query', 'extracted_at'
            ])
            writer.writeheader()
            for r in unique:
                writer.writerow(r.to_dict())

        print(f"\n" + "=" * 70)
        print(f"  ✅ EXTRACTION COMPLETE!")
        print(f"  📁 Saved {len(unique)} unique leads to: {output_path}")
        print(f"  📊 High quality (80+): {sum(1 for r in unique if r.email_score >= 80)}")
        print(f"  📊 Medium (50-79): {sum(1 for r in unique if 50 <= r.email_score < 80)}")
        print("=" * 70)
    else:
        print("\n⚠️  No emails found in any of the websites.")


if __name__ == '__main__':
    main()
