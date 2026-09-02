
"""
NEXOMATE AUTOMATED EMAIL EXTRACTOR
====================================
Automates the entire email prospecting pipeline:
1. Takes website URLs (from Explee or any source)
2. Visits each website automatically
3. Extracts emails from all pages (contact, about, footer, etc.)
4. Validates and scores emails
5. Saves to CSV/JSON for import into CRM

Usage:
    python email_extractor.py --input websites.csv --output leads.csv
    python email_extractor.py --query "solar installation companies texas" --output leads.csv
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
from urllib.robotparser import RobotFileParser
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Set, Dict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Core dependencies - install with: pip install requests beautifulsoup4 lxml
import requests
from bs4 import BeautifulSoup


@dataclass
class ExtractedLead:
    """Standard lead format matching your PostgreSQL schema"""
    company_name: str = ""
    website: str = ""
    email: str = ""
    email_score: int = 0  # 0-100 validation score
    email_source: str = ""  # which page the email was found on
    phone: str = ""
    address: str = ""
    industry: str = ""
    location: str = ""
    contact_name: str = ""
    title: str = ""
    source: str = "email_extractor"
    status: str = "new"
    notes: str = ""
    extracted_at: str = ""

    def to_dict(self):
        return asdict(self)


class EmailExtractor:
    """
    Automated email extraction engine for Nexomate
    Replaces the manual: visit website → find email → copy → paste to sheet
    """

    # Email regex pattern - catches most common formats
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )

    # Pages to check for emails (in order of priority)
    CONTACT_PAGES = [
        '/contact',
        '/contact-us',
        '/about',
        '/about-us',
        '/team',
        '/our-team',
        '/staff',
        '/people',
        '/leadership',
        '/management',
        '/sales',
        '/support',
        '/help',
        '/get-in-touch',
        '/reach-us',
    ]

    # Common false positives to filter out
    FALSE_POSITIVES = {
        'example.com', 'test.com', 'domain.com', 'yourdomain.com',
        'email@example.com', 'info@example.com', 'admin@example.com',
        'noreply@', 'no-reply@', 'donotreply@', 'do-not-reply@',
        'support@wordpress.org', 'help@wordpress.org',
        'sentry@', 'bugsnag@', 'analytics@',
        'mail@', 'webmaster@', 'postmaster@',
    }

    def __init__(self, 
                 delay_range: tuple = (1, 3),
                 max_workers: int = 5,
                 timeout: int = 15,
                 respect_robots: bool = True,
                 user_agent: str = "Nexomate-EmailBot/1.0 (Lead Research Automation)"):
        """
        Args:
            delay_range: Random delay between requests (min, max) seconds
            max_workers: Number of parallel threads
            timeout: Request timeout in seconds
            respect_robots: Whether to check robots.txt
            user_agent: Custom user agent string
        """
        self.delay_range = delay_range
        self.max_workers = max_workers
        self.timeout = timeout
        self.respect_robots = respect_robots
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.results: List[ExtractedLead] = []

    def _can_fetch(self, url: str) -> bool:
        """Check robots.txt permission"""
        if not self.respect_robots:
            return True
        try:
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"

            if base_url not in self.robots_cache:
                rp = RobotFileParser()
                rp.set_url(f"{base_url}/robots.txt")
                rp.read()
                self.robots_cache[base_url] = rp

            return self.robots_cache[base_url].can_fetch(self.user_agent, url)
        except Exception:
            return True  # If robots.txt fails, proceed cautiously

    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage"""
        try:
            if not self._can_fetch(url):
                print(f"  ⛔ Robots.txt blocked: {url}")
                return None

            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            # Random delay to be polite
            time.sleep(random.uniform(*self.delay_range))

            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"  ❌ Failed to fetch {url}: {str(e)[:60]}")
            return None

    def _extract_emails_from_text(self, text: str, source_url: str = "") -> Set[str]:
        """Extract and clean emails from text"""
        found = set()
        for match in self.EMAIL_PATTERN.findall(text):
            email = match.lower().strip()

            # Filter false positives
            if any(fp in email for fp in self.FALSE_POSITIVES):
                continue

            # Filter image file names that look like emails
            if email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                continue

            # Basic validation
            if '.' in email.split('@')[1] and len(email) > 7:
                found.add(email)

        return found

    def _score_email(self, email: str, page_type: str = "homepage") -> int:
        """
        Score email quality (0-100)
        Higher = more likely to be a real business contact
        """
        score = 50  # Base score
        local, domain = email.split('@')

        # Domain quality
        if any(bad in domain for bad in ['gmail', 'yahoo', 'hotmail', 'outlook', 'aol', 'icloud']):
            score -= 20  # Personal email
        else:
            score += 15  # Business domain

        # Role-based emails (lower priority but still valid)
        role_emails = ['info', 'contact', 'hello', 'support', 'sales', 'admin', 'enquiries', 'enquiry']
        if any(role in local for role in role_emails):
            score += 5

        # Named emails (higher priority - e.g., john@company.com)
        if len(local) >= 3 and local[0].isalpha() and not any(role in local for role in role_emails):
            score += 20  # Likely a person's name

        # Page source bonus
        if page_type in ['contact', 'about', 'team']:
            score += 10

        return min(100, max(0, score))

    def _extract_company_name(self, soup: BeautifulSoup, url: str) -> str:
        """Try to find company name from page"""
        # Try title tag
        if soup.title:
            title = soup.title.string or ""
            # Clean up common title patterns
            title = re.sub(r'\s*[\|\-–—]\s*(Home|About|Contact|Welcome).*$', '', title, flags=re.I)
            title = title.strip()
            if len(title) > 2 and len(title) < 100:
                return title

        # Try logo alt text or h1
        for selector in ['.logo', '.brand', 'h1', '.company-name', '[class*="logo"]', '[class*="brand"]', 'header h1']:
            elem = soup.select_one(selector)
            if elem and elem.get_text(strip=True):
                return elem.get_text(strip=True)[:100]

        # Fallback to domain name
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.replace('www.', '').split('.')[0]
        return domain.replace('-', ' ').replace('_', ' ').title()

    def _extract_phone(self, soup: BeautifulSoup) -> str:
        """Extract phone number from page"""
        phone_patterns = [
            r'(?:tel|phone|call)[:\s]*([\d\s\-\(\)\+\.]{10,25})',
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US format
            r'\+?[0-9]{1,3}[-.\s]?\(?[0-9]{1,4}\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}',  # International
        ]

        text = soup.get_text()
        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = match.group(1) if match.groups() else match.group(0)
                return re.sub(r'\s+', ' ', phone).strip()[:50]
        return ""

    def _extract_address(self, soup: BeautifulSoup) -> str:
        """Extract address from page"""
        # Look for address tag or common address patterns
        address_elem = soup.find('address')
        if address_elem:
            return address_elem.get_text(strip=True, separator=", ")[:200]

        # Try common class names
        for cls in ['address', 'location', 'footer-address', 'contact-address']:
            elem = soup.find(class_=re.compile(cls, re.I))
            if elem:
                return elem.get_text(strip=True, separator=", ")[:200]
        return ""

    def extract_from_website(self, website_url: str, industry_hint: str = "", location_hint: str = "") -> List[ExtractedLead]:
        """
        Main extraction method for a single website
        Returns list of ExtractedLead objects
        """
        print(f"\n🔍 Processing: {website_url}")

        # Normalize URL
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url

        leads = []
        all_emails: Dict[str, dict] = {}  # email -> {score, source}

        # 1. Scrape homepage
        print(f"  📄 Checking homepage...")
        soup = self._get_page(website_url)
        if not soup:
            return leads

        company_name = self._extract_company_name(soup, website_url)
        phone = self._extract_phone(soup)
        address = self._extract_address(soup)

        # Extract emails from homepage
        homepage_emails = self._extract_emails_from_text(soup.get_text(), website_url)
        for email in homepage_emails:
            score = self._score_email(email, "homepage")
            all_emails[email] = {'score': score, 'source': 'homepage'}

        # 2. Scrape contact/about pages
        parsed = urllib.parse.urlparse(website_url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for page_path in self.CONTACT_PAGES:
            page_url = base + page_path
            print(f"  📄 Checking {page_path}...")

            page_soup = self._get_page(page_url)
            if page_soup:
                page_emails = self._extract_emails_from_text(page_soup.get_text(), page_url)
                for email in page_emails:
                    if email not in all_emails:
                        score = self._score_email(email, page_path.strip('/'))
                        all_emails[email] = {
                            'score': score, 
                            'source': page_path.strip('/')
                        }
                    else:
                        # Boost score if found on multiple pages
                        all_emails[email]['score'] = min(100, all_emails[email]['score'] + 5)

        # 3. Create lead records
        for email, data in all_emails.items():
            lead = ExtractedLead(
                company_name=company_name,
                website=website_url,
                email=email,
                email_score=data['score'],
                email_source=data['source'],
                phone=phone,
                address=address,
                industry=industry_hint,
                location=location_hint,
                source="email_extractor",
                status="new",
                extracted_at=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            leads.append(lead)
            print(f"  ✅ Found: {email} (score: {data['score']})")

        if not leads:
            print(f"  ⚠️  No emails found on {website_url}")

        return leads

    def process_batch(self, 
                      websites: List[str], 
                      industry: str = "", 
                      location: str = "") -> List[ExtractedLead]:
        """
        Process multiple websites in parallel
        """
        print(f"\n🚀 Starting batch extraction of {len(websites)} websites")
        print(f"   Industry: {industry or 'Any'}")
        print(f"   Location: {location or 'Any'}")
        print("=" * 60)

        all_leads = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.extract_from_website, url, industry, location): url 
                for url in websites
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    leads = future.result()
                    all_leads.extend(leads)
                except Exception as e:
                    print(f"  💥 Error processing {url}: {e}")

        # Remove duplicates (same email)
        seen_emails = set()
        unique_leads = []
        for lead in sorted(all_leads, key=lambda x: x.email_score, reverse=True):
            if lead.email not in seen_emails:
                seen_emails.add(lead.email)
                unique_leads.append(lead)

        print(f"\n📊 EXTRACTION COMPLETE")
        print(f"   Total websites checked: {len(websites)}")
        print(f"   Total unique emails found: {len(unique_leads)}")
        print(f"   Average email score: {sum(l.email_score for l in unique_leads)//max(len(unique_leads),1)}")

        self.results = unique_leads
        return unique_leads

    def save_to_csv(self, filepath: str, leads: List[ExtractedLead] = None):
        """Save results to CSV - ready for import into any CRM"""
        leads = leads or self.results
        if not leads:
            print("⚠️  No leads to save")
            return

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            'company_name', 'website', 'email', 'email_score', 'email_source',
            'phone', 'address', 'industry', 'location', 'contact_name', 'title',
            'source', 'status', 'notes', 'extracted_at'
        ]

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead.to_dict())

        print(f"\n💾 Saved {len(leads)} leads to: {filepath}")

    def save_to_json(self, filepath: str, leads: List[ExtractedLead] = None):
        """Save results to JSON - ready for API import"""
        leads = leads or self.results
        if not leads:
            print("⚠️  No leads to save")
            return

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([lead.to_dict() for lead in leads], f, indent=2, ensure_ascii=False)

        print(f"💾 Saved {len(leads)} leads to: {filepath}")

    def get_statistics(self) -> dict:
        """Get extraction statistics"""
        if not self.results:
            return {}

        scores = [l.email_score for l in self.results]
        return {
            'total_leads': len(self.results),
            'avg_score': sum(scores) / len(scores),
            'high_score_count': sum(1 for s in scores if s >= 80),
            'medium_score_count': sum(1 for s in scores if 50 <= s < 80),
            'low_score_count': sum(1 for s in scores if s < 50),
            'unique_domains': len(set(l.email.split('@')[1] for l in self.results)),
        }


def main():
    parser = argparse.ArgumentParser(
        description='Nexomate Automated Email Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from a list of websites
  python email_extractor.py --input websites.csv --output leads.csv

  # Extract with industry/location context
  python email_extractor.py --input sites.txt --industry "solar" --location "texas" --output solar_tx_leads.csv

  # Single website extraction
  python email_extractor.py --url https://example.com --output lead.json --format json
        """
    )

    parser.add_argument('--input', '-i', help='Input file with website URLs (one per line or CSV)')
    parser.add_argument('--url', '-u', help='Single website URL to extract')
    parser.add_argument('--output', '-o', default='extracted_leads.csv', help='Output file path')
    parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv', help='Output format')
    parser.add_argument('--industry', help='Industry hint for scoring (e.g., solar, interior_design)')
    parser.add_argument('--location', help='Location hint (e.g., "texas", "london")')
    parser.add_argument('--workers', '-w', type=int, default=5, help='Number of parallel workers')
    parser.add_argument('--delay-min', type=float, default=1.0, help='Min delay between requests')
    parser.add_argument('--delay-max', type=float, default=3.0, help='Max delay between requests')

    args = parser.parse_args()

    # Initialize extractor
    extractor = EmailExtractor(
        max_workers=args.workers,
        delay_range=(args.delay_min, args.delay_max)
    )

    # Get website list
    websites = []
    if args.url:
        websites = [args.url]
    elif args.input:
        input_path = Path(args.input)
        if input_path.suffix == '.csv':
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                # Try common column names
                for row in reader:
                    for col in ['website', 'url', 'site', 'domain', 'company_website', 'Website']:
                        if col in row and row[col]:
                            websites.append(row[col])
                            break
        else:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                websites = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        parser.print_help()
        return

    if not websites:
        print("❌ No websites found in input!")
        return

    # Process
    leads = extractor.process_batch(websites, args.industry, args.location)

    # Save
    if args.format == 'csv':
        extractor.save_to_csv(args.output, leads)
    else:
        extractor.save_to_json(args.output, leads)

    # Stats
    stats = extractor.get_statistics()
    if stats:
        print(f"\n📈 STATISTICS:")
        print(f"   High quality emails (80+): {stats['high_score_count']}")
        print(f"   Medium quality (50-79): {stats['medium_score_count']}")
        print(f"   Needs review (<50): {stats['low_score_count']}")
        print(f"   Unique domains: {stats['unique_domains']}")


if __name__ == '__main__':
    main()
