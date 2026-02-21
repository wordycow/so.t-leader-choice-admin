@echo off
cd /d "C:\leemay_project"
echo [RUN] "python" -u "upbit-smart-bot-v8.0-ULTIMATE.py" >> "C:\leemay_project\logs\ai_trading_5000_20260221_212846_143_31764.log" 2>&1
"python" -u "upbit-smart-bot-v8.0-ULTIMATE.py" >> "C:\leemay_project\logs\ai_trading_5000_20260221_212846_143_31764.log" 2>&1
echo [EXITCODE]  >> "C:\leemay_project\logs\ai_trading_5000_20260221_212846_143_31764.log"
pause
