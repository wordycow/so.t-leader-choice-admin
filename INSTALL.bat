@echo off
chcp 65001 > nul
title 업비트 봇 설치

echo.
echo ==========================================
echo   업비트 스마트 봇 v5.0 - 설치 시작
echo ==========================================
echo.

REM 현재 폴더로 이동
cd /d "%~dp0"

echo [1/3] 필수 라이브러리 설치 중...
echo.
python -m pip install --upgrade pip
pip install pyupbit pandas numpy flask flask-cors

echo.
echo [2/3] 설치 확인 중...
pip list | findstr "flask pyupbit pandas"

echo.
echo [3/3] 설치 완료!
echo.
echo ==========================================
echo   이제 START.bat을 실행하세요!
echo ==========================================
echo.

pause
