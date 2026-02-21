@echo off
chcp 65001 > nul
title 업비트 봇 시작

cd /d "%~dp0"

cls
echo.
echo ==========================================
echo   업비트 스마트 봇 v5.0
echo   실행 중...
echo ==========================================
echo.
echo 웹브라우저가 자동으로 열립니다!
echo 브라우저에서 API 키를 입력하세요.
echo.
echo 봇을 종료하려면:
echo 1. 브라우저에서 '⏸ Bot Stop' 클릭
echo 또는
echo 2. 이 창에서 Ctrl+C
echo.
echo ==========================================
echo.

start http://localhost:5000

python upbit-smart-bot-v5.py

pause
