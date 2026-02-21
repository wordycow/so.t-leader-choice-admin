@echo off
chcp 65001 > nul
title 업비트 봇 설치 시작

:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 관리자 권한으로 재실행 중...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

cls
echo.
echo ==========================================
echo   업비트 스마트 봇 v5.0
echo   완전 자동 설치 시작
echo ==========================================
echo.
echo 잠시만 기다려주세요...
echo.

call INSTALL.bat

echo.
echo 설치가 완료되었습니다!
echo.
pause
