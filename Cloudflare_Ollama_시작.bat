@echo off
chcp 65001 > nul
title Cloudflare Tunnel + Ollama Server
color 0A
echo ========================================
echo [START] Cloudflare Tunnel + Ollama Server
echo ========================================
echo.

REM Ollama check and start
echo [CHECK] Ollama Server...
tasklist | find "ollama" > nul
if %errorlevel% equ 0 (
    echo [OK] Ollama is already running.
) else (
    echo [START] Starting Ollama...
    start /B ollama serve
    timeout /t 3 /nobreak > nul
    echo [OK] Ollama started - localhost:11434
)
echo.

REM Cloudflare Tunnel check and start
echo [CHECK] Cloudflare Tunnel...
tasklist | find "cloudflared" > nul
if %errorlevel% equ 0 (
    echo [OK] Cloudflare Tunnel is already running.
) else (
    echo [START] Starting Cloudflare Tunnel...
    echo.
    echo ========================================
    echo [IMPORTANT] Cloudflare Tunnel URL:
    echo ========================================
    REM Run cloudflared WITHOUT /B to see URL in console
    start "Cloudflare Tunnel" cloudflared tunnel --url http://localhost:11434
    timeout /t 8 /nobreak > nul
    echo.
    echo [OK] Cloudflare Tunnel started
    echo [INFO] Check the 'Cloudflare Tunnel' window for URL
    echo       Example: https://xxx-yyy-zzz.trycloudflare.com
)
echo.

echo ========================================
echo [SUCCESS] All servers started!
echo ========================================
echo.
echo [SERVICES]
echo    - Ollama: http://localhost:11434
echo    - Cloudflare Tunnel: Check separate window for URL
echo.
echo [WARNING] Do NOT close this window!
echo           Use Cloudflare_Ollama_stop.bat to stop services.
echo.
pause
