@echo off
cd /d C:\leemay_project
echo [2026-02-21  2:51:38.98] 🚀 STARTING TRADING BOT...
start /b python upbit-smart-bot-v8.0-ULTIMATE.py --port 5000 > logs\bot_5000_run.log 2>&1
