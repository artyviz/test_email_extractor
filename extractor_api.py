"""
NEXOMATE SOLAR EMAIL EXTRACTOR WEB APP
======================================
Ultra-minimalistic 1-click Web UI & API dedicated to Solar Lead Extraction.
Run: python extractor_api.py
Web UI at: http://localhost:5000
"""

import sys
import io
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from pathlib import Path

# Import extractor engine
sys.path.insert(0, str(Path(__file__).parent))
from email_extractor import EmailExtractor

app = FastAPI(title="Nexomate Solar Email Extractor", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract-from-urls")
async def extract_from_urls(urls: List[str]):
    """Extract emails from a list of Solar URLs"""
    try:
        extractor = EmailExtractor(max_workers=10, delay_range=(0.5, 1.5))
        leads = extractor.process_batch(urls, industry="solar")

        return {
            "success": True,
            "urls_processed": len(urls),
            "leads_found": len(leads),
            "leads": [l.to_dict() for l in leads],
            "stats": extractor.get_statistics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "app": "Nexomate Solar Email Extractor"}


@app.get("/input/solar")
async def get_solar_input():
    p = Path(__file__).parent / "input" / "solar_companies.txt"
    if p.exists():
        return HTMLResponse(content=p.read_text(encoding="utf-8"), media_type="text/plain")
    return HTMLResponse(content="https://sunpower.com\nhttps://tesla.com/energy\nhttps://palmetto.com\nhttps://trismartsolar.com", media_type="text/plain")


@app.get("/", response_class=HTMLResponse)
async def minimal_solar_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexomate Solar Extractor</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #FAFAFA;
            --surface: #FFFFFF;
            --border: #E5E7EB;
            --text-primary: #111827;
            --text-secondary: #6B7280;
            --accent: #2563EB;
            --accent-hover: #1D4ED8;
            --success: #10B981;
            --radius: 12px;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #0B0F17;
                --surface: #151C28;
                --border: #263346;
                --text-primary: #F9FAFB;
                --text-secondary: #9CA3AF;
                --accent: #3B82F6;
                --accent-hover: #60A5FA;
                --success: #34D399;
            }
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', -apple-system, sans-serif; }
        body { background: var(--bg); color: var(--text-primary); min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 3rem 1.5rem; }
        
        .app-container { width: 100%; max-width: 820px; }
        
        header { text-align: center; margin-bottom: 2.5rem; }
        header h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.025em; margin-bottom: 0.4rem; }
        header p { color: var(--text-secondary); font-size: 1rem; }

        .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.75rem; box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05); margin-bottom: 2rem; }
        
        .preset-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
        .preset-bar label { font-weight: 600; font-size: 0.9rem; color: var(--text-primary); }
        .preset-btn { background: none; border: 1px solid var(--border); color: var(--accent); padding: 0.35rem 0.75rem; font-size: 0.8rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.15s; }
        .preset-btn:hover { background: rgba(59, 130, 246, 0.08); }

        textarea { width: 100%; height: 160px; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; color: var(--text-primary); font-size: 0.95rem; line-height: 1.5; outline: none; transition: border 0.2s; resize: vertical; }
        textarea:focus { border-color: var(--accent); }

        .btn-extract { width: 100%; margin-top: 1.25rem; background: var(--accent); color: #FFF; border: none; padding: 0.9rem; font-size: 1rem; font-weight: 600; border-radius: 8px; cursor: pointer; transition: background 0.2s; display: flex; justify-content: center; align-items: center; gap: 0.5rem; }
        .btn-extract:hover { background: var(--accent-hover); }
        .btn-extract:disabled { opacity: 0.6; cursor: not-allowed; }

        .spinner { width: 18px; height: 18px; border: 2.5px solid rgba(255,255,255,0.3); border-top-color: #FFF; border-radius: 50%; animation: spin 0.7s linear infinite; display: none; }
        @keyframes spin { to { transform: rotate(360deg); } }

        .stats-bar { display: flex; gap: 1.5rem; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 1rem; }
        .stat-item { display: flex; flex-direction: column; }
        .stat-val { font-size: 1.4rem; font-weight: 700; }
        .stat-lbl { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-top: 0.1rem; }

        .actions-bar { display: flex; gap: 0.75rem; }
        .btn-action { background: var(--bg); border: 1px solid var(--border); color: var(--text-primary); font-size: 0.85rem; font-weight: 600; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; transition: all 0.15s; }
        .btn-action:hover { border-color: var(--accent); color: var(--accent); }

        .table-wrap { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { font-size: 0.8rem; text-transform: uppercase; color: var(--text-secondary); padding: 0.75rem; border-bottom: 1px solid var(--border); font-weight: 600; }
        td { padding: 0.85rem 0.75rem; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
        tr:last-child td { border-bottom: none; }

        .badge { padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
        .badge-high { background: rgba(16, 185, 129, 0.15); color: var(--success); }
        .badge-med { background: rgba(245, 158, 11, 0.15); color: #F59E0B; }
        .badge-low { background: rgba(156, 163, 175, 0.15); color: var(--text-secondary); }
    </style>
</head>
<body>
    <div class="app-container">
        <header>
            <h1>☀️ Nexomate Solar Email Extractor</h1>
            <p>Paste Solar Company website URLs to extract prospect emails</p>
        </header>

        <div class="card">
            <div class="preset-bar">
                <label>Solar Website URLs</label>
                <div>
                    <button class="preset-btn" onclick="loadSolarSample()">☀️ Load 100 Solar Companies</button>
                    <button class="preset-btn" onclick="clearInput()" style="color: var(--text-secondary);">Clear</button>
                </div>
            </div>
            <textarea id="urls-input" placeholder="https://sunpower.com&#10;https://tesla.com/energy&#10;https://palmetto.com&#10;https://trismartsolar.com"></textarea>
            <button id="btn-extract" class="btn-extract" onclick="startExtraction()">
                <div class="spinner" id="spinner"></div>
                <span id="btn-txt">Extract Solar Emails</span>
            </button>
        </div>

        <div id="results-card" class="card" style="display: none;">
            <div class="stats-bar">
                <div style="display: flex; gap: 2rem;">
                    <div class="stat-item">
                        <span class="stat-val" id="stat-processed">0</span>
                        <span class="stat-lbl">Solar Websites</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-val" id="stat-found" style="color: var(--success);">0</span>
                        <span class="stat-lbl">Emails Found</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-val" id="stat-high" style="color: var(--accent);">0</span>
                        <span class="stat-lbl">High Quality</span>
                    </div>
                </div>
                <div class="actions-bar">
                    <button class="btn-action" onclick="copyAllEmails()">📋 Copy Emails</button>
                    <button class="btn-action" onclick="downloadCSV()" style="background: var(--accent); color: #FFF; border: none;">📥 Download CSV</button>
                </div>
            </div>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Solar Company</th>
                            <th>Email</th>
                            <th>Score</th>
                            <th>Source</th>
                            <th>Website</th>
                        </tr>
                    </thead>
                    <tbody id="leads-tbody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let currentLeads = [];

        async function startExtraction() {
            const raw = document.getElementById('urls-input').value.trim();
            if (!raw) { alert("Please paste at least one Solar website URL!"); return; }

            const urls = raw.split('\\n').map(u => u.trim()).filter(u => u.length > 0);
            
            setLoading(true);
            try {
                const res = await fetch('/extract-from-urls', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(urls)
                });
                const data = await res.json();
                if (data.success) {
                    renderLeads(data.leads, data.urls_processed);
                } else {
                    alert("Error: " + JSON.stringify(data));
                }
            } catch (e) {
                alert("Network error. Make sure server is running on http://localhost:5000");
            } finally {
                setLoading(false);
            }
        }

        function setLoading(loading) {
            const btn = document.getElementById('btn-extract');
            const spinner = document.getElementById('spinner');
            const txt = document.getElementById('btn-txt');
            
            if (loading) {
                btn.disabled = true;
                spinner.style.display = 'block';
                txt.innerText = 'Extracting Solar Emails...';
            } else {
                btn.disabled = false;
                spinner.style.display = 'none';
                txt.innerText = 'Extract Solar Emails';
            }
        }

        function renderLeads(leads, processedCount) {
            currentLeads = leads;
            document.getElementById('results-card').style.display = 'block';
            document.getElementById('stat-processed').innerText = processedCount;
            document.getElementById('stat-found').innerText = leads.length;
            document.getElementById('stat-high').innerText = leads.filter(l => l.email_score >= 80).length;

            const tbody = document.getElementById('leads-tbody');
            if (leads.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-secondary); padding: 2rem;">No emails found on the checked solar websites.</td></tr>`;
                return;
            }

            tbody.innerHTML = leads.map(l => {
                const badge = l.email_score >= 80 ? 'badge-high' : (l.email_score >= 50 ? 'badge-med' : 'badge-low');
                return `
                    <tr>
                        <td><strong>${escapeHtml(l.company_name || 'Solar Company')}</strong></td>
                        <td><strong style="color: var(--success);">${escapeHtml(l.email)}</strong></td>
                        <td><span class="badge ${badge}">${l.email_score}/100</span></td>
                        <td style="color: var(--text-secondary);">${escapeHtml(l.email_source || 'page')}</td>
                        <td><a href="${l.website}" target="_blank" style="color: var(--accent); text-decoration: none;">${escapeHtml(l.website.replace('https://','').replace('http://',''))}</a></td>
                    </tr>
                `;
            }).join('');
        }

        function copyAllEmails() {
            if (currentLeads.length === 0) return;
            const emails = currentLeads.map(l => l.email).join('\\n');
            navigator.clipboard.writeText(emails);
            alert(`Copied ${currentLeads.length} solar company emails to clipboard!`);
        }

        function downloadCSV() {
            if (currentLeads.length === 0) return;
            const headers = ["company_name", "website", "email", "email_score", "email_source", "phone"];
            let csv = headers.join(",") + "\\n";
            currentLeads.forEach(l => {
                csv += headers.map(h => `"${(l[h]||'').toString().replace(/"/g, '""')}"`).join(",") + "\\n";
            });
            const blob = new Blob([csv], { type: 'text/csv' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `solar_leads_${Date.now()}.csv`;
            link.click();
        }

        async function loadSolarSample() {
            const res = await fetch('/input/solar');
            if (res.ok) {
                document.getElementById('urls-input').value = await res.text();
            } else {
                document.getElementById('urls-input').value = "https://sunpower.com\\nhttps://tesla.com/energy\\nhttps://sunrun.com\\nhttps://palmetto.com\\nhttps://trismartsolar.com";
            }
        }

        function clearInput() {
            document.getElementById('urls-input').value = '';
        }

        function escapeHtml(str) {
            return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }
    </script>
</body>
</html>"""


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
