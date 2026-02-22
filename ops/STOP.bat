@echo off
chcp 65001 >nul
title Lee May Training Center - STOP

echo ============================================================
echo   🛑 Lee May Training Center - Stopping
echo ============================================================
echo.

echo [1/1] Stopping Lee May API Server...

:: API 서버 중지
tasklist | find /i "python.exe" >nul
if errorlevel 1 (
    echo [SKIP] API Server was not running
) else (
    taskkill /F /FI "WINDOWTITLE eq Lee May API*" >nul 2>&1
    echo [OK] API Server stopped
)

echo.
echo ============================================================
echo   ✅ All services stopped!
echo ============================================================
echo.
echo 💡 Tip: Ollama Tunnel은 수동으로 중지하세요
echo    (필요 시: taskkill /F /IM cloudflared.exe)
echo.
pause
