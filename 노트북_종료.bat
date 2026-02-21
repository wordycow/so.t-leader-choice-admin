@echo off
chcp 65001 > nul
echo ========================================
echo 🛑 Upbit Trading Bot 종료
echo ========================================
echo.

REM Python 프로세스 종료
taskkill /F /IM python.exe /FI "WINDOWTITLE eq upbit-smart-bot-v8.0-ULTIMATE.py" > nul 2>&1
taskkill /F /IM python.exe /FI "MEMUSAGE gt 50000" > nul 2>&1

echo ✅ 봇이 종료되었습니다!
echo.
pause
