@echo off
chcp 65001 > nul
title Cloudflare Tunnel + Ollama Server
color 0A
echo ========================================
echo [START] Cloudflare Tunnel + Ollama
echo ========================================
echo.

REM Check Ollama
echo [1/2] Checking Ollama Server...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find "ollama.exe" > nul
if %errorlevel% equ 0 (
    echo [OK] Ollama is already running
) else (
    echo [START] Starting Ollama on port 11434...
    start /B ollama serve
    timeout /t 3 /nobreak > nul
    echo [OK] Ollama started
)
echo.

REM Check Cloudflare Tunnel
echo [2/2] Checking Cloudflare Tunnel...
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | find "cloudflared.exe" > nul
if %errorlevel% equ 0 (
    echo [OK] Cloudflare Tunnel is already running
) else (
    echo [START] Starting Cloudflare Tunnel...
    echo.
    echo ========================================
    echo CLOUDFLARE TUNNEL URL WILL APPEAR HERE:
    echo ========================================
    echo.
    REM Start cloudflared in NEW window to see URL
    start "Cloudflare Tunnel - Check this window for URL!" cloudflared tunnel --url http://localhost:11434
    timeout /t 5 /nobreak > nul
    echo.
    echo [OK] Cloudflare Tunnel started in separate window
    echo [INFO] Look for "https://xxxxx.trycloudflare.com" in the new window!
)
echo.

echo ========================================
echo SUCCESS! All servers are running
echo ========================================
echo.
echo [LOCAL ACCESS]
echo   Ollama: http://localhost:11434
echo.
echo [EXTERNAL ACCESS]
echo   Check the "Cloudflare Tunnel" window
echo   Look for: https://xxxxx.trycloudflare.com
echo.
echo [STOP SERVICES]
echo   Run: STOP_Cloudflare_Ollama.bat
echo.
echo Press any key to keep services running...
pause > nul
