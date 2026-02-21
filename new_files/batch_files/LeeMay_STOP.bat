@echo off
chcp 65001 >nul
title Lee May Training Center - STOP

echo ============================================================
echo   🛑 Lee May Training Center - Stopping All Services
echo ============================================================
echo.

:: 1. Python API 서버 중지
echo [1/2] Stopping Lee May API Server...
tasklist | find /i "python.exe" >nul
if errorlevel 1 (
    echo [SKIP] API Server was not running
) else (
    taskkill /F /IM python.exe >nul 2>&1
    echo [OK] API Server stopped
)

echo.

:: 2. Cloudflare Tunnel 중지
echo [2/2] Stopping Ollama Tunnel...
tasklist | find /i "cloudflared.exe" >nul
if errorlevel 1 (
    echo [SKIP] Ollama Tunnel was not running
) else (
    taskkill /F /IM cloudflared.exe >nul 2>&1
    echo [OK] Ollama Tunnel stopped
)

echo.
echo ============================================================
echo   ✅ All services stopped successfully!
echo ============================================================
echo.
timeout /t 3 /nobreak >nul
