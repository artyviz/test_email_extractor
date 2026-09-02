
"""
NEXOMATE EMAIL EXTRACTOR - DEMO
=================================
This demo shows exactly how the tool works with sample data.
Run this to see the output format before processing real websites.
"""

import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from email_extractor import EmailExtractor, ExtractedLead
from datetime import datetime

def demo_extraction():
    print("=" * 70)
    print("  NEXOMATE EMAIL EXTRACTOR - LIVE DEMO")
    print("=" * 70)
    print()
    print("This demo simulates extracting emails from 3 solar company websites.")
    print("In real usage, the tool visits actual websites automatically.")
    print()

    # Simulate extracted results (what the tool produces)
    sample_results = [
        ExtractedLead(
            company_name="SunPower Texas",
            website="https://sunpowertexas.com",
            email="john.martinez@sunpowertexas.com",
            email_score=95,
            email_source="contact page",
            phone="+1-512-555-0142",
            address="Austin, TX 78701",
            industry="solar",
            location="texas",
            contact_name="John Martinez",
            title="Owner",
            source="email_extractor",
            status="new",
            extracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        ExtractedLead(
            company_name="SunPower Texas",
            website="https://sunpowertexas.com",
            email="sales@sunpowertexas.com",
            email_score=70,
            email_source="footer",
            phone="+1-512-555-0142",
            address="Austin, TX 78701",
            industry="solar",
            location="texas",
            source="email_extractor",
            status="new",
            extracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        ExtractedLead(
            company_name="GreenHome Solar",
            website="https://greenhomesolar.com",
            email="sarah.chen@greenhomesolar.com",
            email_score=92,
            email_source="about page",
            phone="+1-713-555-0198",
            address="Houston, TX 77001",
            industry="solar",
            location="texas",
            contact_name="Sarah Chen",
            title="Sales Director",
            source="email_extractor",
            status="new",
            extracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        ExtractedLead(
            company_name="Lone Star Panels",
            website="https://lonestarpanels.com",
            email="info@lonestarpanels.com",
            email_score=65,
            email_source="contact page",
            phone="+1-214-555-0176",
            address="Dallas, TX 75201",
            industry="solar",
            location="texas",
            source="email_extractor",
            status="new",
            extracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        ExtractedLead(
            company_name="Lone Star Panels",
            website="https://lonestarpanels.com",
            email="mike.rodriguez@lonestarpanels.com",
            email_score=88,
            email_source="team page",
            phone="+1-214-555-0176",
            address="Dallas, TX 75201",
            industry="solar",
            location="texas",
            contact_name="Mike Rodriguez",
            title="Founder",
            source="email_extractor",
            status="new",
            extracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
    ]

    # Show extraction process simulation
    websites = [
        "sunpowertexas.com",
        "greenhomesolar.com", 
        "lonestarpanels.com"
    ]

    for i, site in enumerate(websites, 1):
        print(f"🔍 [{i}/3] Processing: {site}")
        print(f"   📄 Checking homepage...")
        print(f"   📄 Checking /contact...")
        print(f"   📄 Checking /about...")
        print(f"   ✅ Emails found!")
        print()

    # Show results table
    print("=" * 70)
    print("  EXTRACTION RESULTS")
    print("=" * 70)
    print()
    print(f"{'Company':<20} {'Email':<30} {'Score':<8} {'Source':<15}")
    print("-" * 70)

    for lead in sample_results:
        print(f"{lead.company_name:<20} {lead.email:<30} {lead.email_score:<8} {lead.email_source:<15}")

    print()
    print("=" * 70)
    print("  STATISTICS")
    print("=" * 70)
    print(f"   Total websites checked: 3")
    print(f"   Total emails found: {len(sample_results)}")
    print(f"   Unique emails: 5")
    print(f"   High quality (80+): 3")
    print(f"   Medium quality (50-79): 2")
    print()

    # Show what your founder gets
    print("=" * 70)
    print("  WHAT YOUR FOUNDER GETS")
    print("=" * 70)
    print()
    print("✅ BEFORE (Manual Process):")
    print("   1. Explee gives: sunpowertexas.com")
    print("   2. Open browser → visit website")
    print("   3. Click Contact → find email")
    print("   4. Copy email → open Google Sheets")
    print("   5. Paste → format → save")
    print("   6. Repeat for EVERY website...")
    print("   ⏱️  Time per lead: ~3-5 minutes")
    print()
    print("✅ AFTER (This Tool):")
    print("   1. Run: python website_finder.py --query 'solar texas' --output leads.csv")
    print("   2. Wait 2-3 minutes")
    print("   3. Open leads.csv → ALL emails ready!")
    print("   ⏱️  Time per lead: ~0 seconds (fully automated)")
    print()
    print("💾 Output saved to: output/demo_leads.csv")
    print()

    # Save demo CSV
    import csv
    from pathlib import Path

    Path("output").mkdir(exist_ok=True)
    with open("output/demo_leads.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "company_name", "website", "email", "email_score", "email_source",
            "phone", "address", "industry", "location", "contact_name", "title",
            "source", "status", "notes", "extracted_at"
        ], extrasaction='ignore')
        writer.writeheader()
        for lead in sample_results:
            writer.writerow(lead.to_dict())

    return sample_results


if __name__ == "__main__":
    demo_extraction()
