@echo off
chcp 65001 > nul
title 업비트 스마트 봇 v5.0

echo.
echo ==========================================
echo   업비트 스마트 봇 v5.0
echo ==========================================
echo.

REM 현재 폴더로 이동
cd /d "%~dp0"

echo 봇을 시작합니다...
echo.
echo 웹 브라우저: http://localhost:5000
echo 봇 중지: 이 창을 닫거나 Ctrl+C
echo.

REM 2초 후 브라우저 열기
timeout /t 2 > nul
start http://localhost:5000

REM 봇 실행
python upbit-smart-bot-v5.py

pause
