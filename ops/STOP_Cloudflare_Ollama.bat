@echo off
chcp 65001 > nul
title Stop Cloudflare + Ollama
color 0C
echo ========================================
echo [STOP] Cloudflare Tunnel + Ollama
echo ========================================
echo.

REM Stop Cloudflare Tunnel
echo [1/2] Stopping Cloudflare Tunnel...
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>nul | find "cloudflared.exe" > nul
if %errorlevel% equ 0 (
    taskkill /F /IM cloudflared.exe > nul 2>&1
    echo [OK] Cloudflare Tunnel stopped
) else (
    echo [SKIP] Cloudflare Tunnel was not running
)
echo.

REM Stop Ollama
echo [2/2] Stopping Ollama Server...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find "ollama.exe" > nul
if %errorlevel% equ 0 (
    taskkill /F /IM ollama.exe > nul 2>&1
    echo [OK] Ollama stopped
) else (
    echo [SKIP] Ollama was not running
)
echo.

echo ========================================
echo SUCCESS! All services stopped
echo ========================================
echo.
pause
