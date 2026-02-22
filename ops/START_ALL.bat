@echo off
chcp 65001 > nul
title Start ALL Services
color 0B
echo ========================================
echo [START] ALL SERVICES
echo ========================================
echo   1. Ollama Server (localhost:11434)
echo   2. Cloudflare Tunnel
echo   3. Trading Bot (localhost:5000)
echo ========================================
echo.

REM 1. Start Ollama
echo [1/3] Starting Ollama Server...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find "ollama.exe" > nul
if %errorlevel% equ 0 (
    echo [OK] Ollama already running
) else (
    start /B ollama serve
    timeout /t 3 /nobreak > nul
    echo [OK] Ollama started - http://localhost:11434
)
echo.

REM 2. Start Cloudflare Tunnel
echo [2/3] Starting Cloudflare Tunnel...
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | find "cloudflared.exe" > nul
if %errorlevel% equ 0 (
    echo [OK] Cloudflare Tunnel already running
) else (
    echo.
    echo ========================================
    echo CLOUDFLARE TUNNEL URL:
    echo ========================================
    start "Cloudflare Tunnel - CHECK THIS WINDOW!" cloudflared tunnel --url http://localhost:11434
    timeout /t 5 /nobreak > nul
    echo [OK] Cloudflare Tunnel started
    echo [INFO] Check the new window for URL!
)
echo.

REM 3. Start Trading Bot
echo [3/3] Starting Trading Bot...
tasklist /FI "WINDOWTITLE eq upbit-smart-bot*" 2>nul | find "python" > nul
if %errorlevel% equ 0 (
    echo [OK] Trading Bot already running
) else (
    start /B python upbit-smart-bot-v8.0-ULTIMATE.py
    timeout /t 3 /nobreak > nul
    echo [OK] Trading Bot started - http://localhost:5000
)
echo.

echo ========================================
echo SUCCESS! All services running
echo ========================================
echo.
echo [ACCESS URLS]
echo   Trading Bot:  http://localhost:5000
echo   Ollama:       http://localhost:11434
echo   External:     Check Cloudflare Tunnel window
echo.
echo [STOP ALL]
echo   Run: STOP_ALL.bat
echo.
echo Press any key to continue...
pause > nul
