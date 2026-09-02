#!/bin/bash
# NEXOMATE EMAIL EXTRACTOR - SETUP SCRIPT
# Run this to install everything automatically

echo "🚀 Setting up Nexomate Email Extractor..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create output directory
mkdir -p output
mkdir -p input

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 QUICK START:"
echo "   1. Add website URLs to: input/websites.txt (one per line)"
echo "   2. Run: python email_extractor.py --input input/websites.txt --output output/leads.csv"
echo "   3. Or run the full finder: python website_finder.py --query 'solar companies texas' --output output/solar_tx.csv"
echo ""
echo "🤖 FOR N8N AUTOMATION:"
echo "   1. Start API: python extractor_api.py"
echo "   2. Import workflow: n8n_email_extractor_workflow.json"
echo "   3. Configure PostgreSQL credentials in n8n"
echo ""
