#!/bin/bash
# Nexomate Email Extractor - Mac 1-Click Launcher
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==================================================="
echo "     NEXOMATE EMAIL EXTRACTOR - MAC 1-CLICK"
echo "==================================================="
echo ""
echo "Checking dependencies..."
python3 -m pip install -q -r requirements.txt

echo "Launching Web Dashboard..."
(sleep 2 && open "http://localhost:5000") &
python3 extractor_api.py
