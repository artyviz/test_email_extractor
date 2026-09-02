<<<<<<< HEAD
# 🔍 NEXOMATE AUTOMATED EMAIL EXTRACTOR

**Problem Solved:** Your founder was using Explee's free version which only gives website URLs. He had to manually visit each website, find the email, copy it, and paste it into a sheet. This tool automates ALL of that.

**What This Does:**
- ✅ Finds business websites automatically (Google Search)
- ✅ Visits each website automatically
- ✅ Extracts emails from contact pages, about pages, footers
- ✅ Scores email quality (0-100)
- ✅ Removes duplicates and false positives
- ✅ Saves to CSV/JSON ready for CRM import
- ✅ Integrates with your existing n8n + PostgreSQL stack

---

## 📁 Files Included

| File | Purpose |
|------|---------|
| `email_extractor.py` | Core engine - extracts emails from any website |
| `website_finder.py` | Combo tool - searches Google + extracts emails |
| `extractor_api.py` | FastAPI server for n8n integration |
| `n8n_email_extractor_workflow.json` | Ready-to-import n8n automation workflow |
| `requirements.txt` | Python dependencies |
| `setup.sh` | One-command setup script |

## 🚀 1-CLICK LAUNCHER (For Non-Techie Founder)

### macOS Setup (Mac):
1. Double-click [`1-CLICK_START_EXTRACTOR.command`](file:///c:/Users/Farhan/Desktop/nexomate/nexomate-email-extractor/1-CLICK_START_EXTRACTOR.command).
   *(Note: If Mac blocks it first time, right-click -> Open, or run `chmod +x 1-CLICK_START_EXTRACTOR.command` in Terminal once).*
2. The Web App automatically opens in Safari / Chrome!
3. Paste Explee URLs -> Click **Extract Emails Now** -> Click **Download CSV**.

### Windows Setup:
1. Double-click [`1-CLICK_START_EXTRACTOR.bat`](file:///c:/Users/Farhan/Desktop/nexomate/nexomate-email-extractor/1-CLICK_START_EXTRACTOR.bat).

---

## 🚀 QUICK START (CLI Usage)

### Option 1: Extract from websites you already have (from Explee)

```bash
# 1. Create a file with websites (one per line)
echo "sunpower.com" > input/websites.txt
echo "tesla.com/energy" >> input/websites.txt
echo "vivintsolar.com" >> input/websites.txt

# 2. Run the extractor
python email_extractor.py --input input/websites.txt --industry solar --location texas --output output/solar_leads.csv

# 3. Open output/solar_leads.csv - all emails are there!
```

### Option 2: Find + Extract in one command (No Explee needed)

```bash
# Find solar companies in Texas AND extract their emails
python website_finder.py --query "solar installation companies texas" --max-results 30 --output output/solar_tx_leads.csv

# Find interior designers in London
python website_finder.py --query "interior design firms london" --max-results 30 --output output/design_uk_leads.csv
```

---

## 📊 Output Format

The CSV output matches your PostgreSQL `leads` table schema:

| Column | Example | Description |
|--------|---------|-------------|
| company_name | SunPower Texas | Business name |
| website | https://sunpower.com | Source website |
| email | john@sunpower.com | Extracted email |
| email_score | 95 | Quality score (0-100) |
| email_source | contact | Which page had the email |
| phone | +1-512-555-0123 | Found phone number |
| address | Austin, TX | Business address |
| industry | solar | Your specified industry |
| location | texas | Your specified location |
| source | email_extractor | Tracking source |
| status | new | Lead status for CRM |

---

## 🎯 Email Quality Scoring

| Score | Meaning | Action |
|-------|---------|--------|
| 80-100 | **HIGH** - Named email (john@company.com) or verified contact | Priority outreach |
| 50-79 | **MEDIUM** - Role email (info@, sales@) | Good for initial contact |
| 0-49 | **LOW** - Generic or uncertain | Verify before sending |

---

## 🤖 N8N AUTOMATION (Full Integration)

### Step 1: Start the API Server
```bash
python extractor_api.py
# Runs on http://localhost:5000
```

### Step 2: Import the Workflow
1. Open n8n
2. Click "Import from File"
3. Select `n8n_email_extractor_workflow.json`
4. Configure your PostgreSQL credentials
5. Set Slack webhook URL for alerts

### Step 3: Schedule It
The workflow runs **daily at 9 AM** automatically:
- Searches for new prospects
- Extracts emails
- Saves to PostgreSQL
- Sends Slack alert to founder

---

## 💰 Cost Comparison

| Tool | What You Get | Monthly Cost |
|------|-------------|--------------|
| **Explee Free** | Only website URLs | $0 |
| **Explee Paid** | Full automation | $100-500 |
| **Apollo.io** | Emails + outreach | $59-200 |
| **Hunter.io** | Email finder only | $49-200 |
| **This Tool** | URLs + Emails + Scoring + CRM Integration | **$0** |

---

## 🔒 Compliance & Safety

- ✅ Respects `robots.txt` on all websites
- ✅ Random delays between requests (polite scraping)
- ✅ Custom user agent identifies as automation
- ✅ Rate limiting built-in
- ✅ No bulk spam - extracts publicly listed emails only

---

## 🛠️ Advanced Usage

### Extract from specific pages only
```python
from email_extractor import EmailExtractor

extractor = EmailExtractor(max_workers=10, delay_range=(0.5, 1.5))
leads = extractor.extract_from_website("https://example.com")
```

### Batch process with custom scoring
```python
websites = ["site1.com", "site2.com", "site3.com"]
leads = extractor.process_batch(websites, industry="solar", location="florida")
extractor.save_to_csv("florida_solar.csv", leads)
```

### API Integration
```bash
curl -X POST http://localhost:5000/extract \
  -H "Content-Type: application/json" \
  -d '{
    "query": "solar companies california",
    "industry": "solar",
    "location": "california",
    "max_results": 50
  }'
```

---

## 📝 Next Steps for Your Founder

1. **Today:** Run Option 1 with your existing Explee URLs → get instant CSV
2. **This Week:** Test Option 2 for new markets → find + extract automatically  
3. **Next Week:** Deploy n8n workflow → fully automated daily extraction
4. **Ongoing:** Import CSV into your CRM → start outreach immediately

---

**Built for Nexomate** | Replaces manual copy-paste with full automation
=======
# test_email_extractor-
testing automated py 
>>>>>>> b83cff2e129174cf4f8050a155219746438158f0
