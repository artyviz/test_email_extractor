#!/bin/bash
# Nexomate Email Extractor - Mac 1-Click Launcher
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==================================================="
echo "     NEXOMATE EMAIL EXTRACTOR - MAC 1-CLICK"
echo "==================================================="
echo ""
echo "Starting Nexomate Minimalist Web App..."

# Open local web URL automatically in Safari / Chrome
(sleep 2 && open "http://localhost:5000") &

# Run local web server
python3 extractor_api.py
