@echo off
chcp 65001 > nul
title 업비트 스마트 봇 v5.0

cls
echo.
echo ==========================================
echo   🤖 업비트 스마트 봇 v5.0
echo ==========================================
echo.

REM 현재 폴더로 이동
cd /d "%~dp0"

echo Flask 확인 중...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ❌ Flask가 설치되지 않았습니다!
    echo.
    echo 먼저 INSTALL.bat을 실행하세요!
    echo.
    pause
    exit /b 1
)

echo ✅ Flask 확인됨
echo.
echo 봇을 시작합니다...
echo.
echo 웹 페이지: http://localhost:5000
echo 봇 중지: 이 창을 닫거나 Ctrl+C
echo.

REM 브라우저 열기 (3초 후)
start /b timeout /t 3 > nul & start http://localhost:5000

REM 봇 실행
python upbit-smart-bot-v5.py

pause
