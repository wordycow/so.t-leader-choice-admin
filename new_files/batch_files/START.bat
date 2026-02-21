@echo off
chcp 65001 >nul
title Lee May Training Center - START

echo ============================================================
echo   🤖 Lee May Training Center
echo ============================================================
echo.

:: Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다!
    pause
    exit /b 1
)

echo [1/3] Starting Lee May API Server...
echo.

:: API 서버 시작
start "Lee May API" python api_server.py

timeout /t 3 /nobreak >nul

echo ✅ Lee May API Server started!
echo.

echo [2/3] Checking Ollama Tunnel...
echo.

:: Ollama 터널 확인
tasklist | find /i "cloudflared.exe" >nul
if errorlevel 1 (
    echo ⚠️  Ollama Tunnel이 실행되지 않았습니다
    echo    수동으로 시작하세요: cloudflared tunnel run ollama-stable
) else (
    echo ✅ Ollama Tunnel is already running!
)

echo.
echo [3/3] All Done!
echo.
echo ============================================================
echo   📍 Local:    http://localhost:5001
echo   🌐 External: https://leemay.더유니크.com
echo ============================================================
echo.
echo ⚠️  이 창을 닫지 마세요!
echo    종료하려면 STOP.bat 실행
echo.
pause
