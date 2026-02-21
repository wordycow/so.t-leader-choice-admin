@echo off
chcp 65001 > nul
title 업비트 봇 설치

echo.
echo ==========================================
echo   업비트 스마트 봇 v5.0 - 설치
echo ==========================================
echo.

REM 현재 폴더로 이동
cd /d "%~dp0"

echo Python 확인 중...
python --version
if %errorlevel% neq 0 (
    echo.
    echo ❌ Python이 설치되지 않았습니다!
    echo.
    echo 해결 방법:
    echo 1. https://www.python.org/downloads/ 에서 Python 다운로드
    echo 2. 설치 시 "Add Python to PATH" 체크 필수!
    echo 3. 설치 완료 후 이 파일을 다시 실행하세요
    echo.
    pause
    exit /b 1
)

echo.
echo [1/2] 라이브러리 설치 중...
echo.

python -m pip install --upgrade pip
python -m pip install pyupbit
python -m pip install pandas
python -m pip install numpy
python -m pip install flask
python -m pip install flask-cors

echo.
echo [2/2] 설치 확인...
echo.

python -m pip list | findstr "flask pyupbit pandas"

echo.
echo ==========================================
echo   설치 완료!
echo   이제 START.bat을 실행하세요!
echo ==========================================
echo.

pause
