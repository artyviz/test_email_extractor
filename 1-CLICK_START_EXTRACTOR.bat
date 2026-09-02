@echo off
title Nexomate Email Extractor
echo ===================================================
echo     NEXOMATE EMAIL EXTRACTOR - 1-CLICK LAUNCHER
echo ===================================================
echo.
echo Starting email extractor web app...
start http://localhost:5000
python extractor_api.py
pause
