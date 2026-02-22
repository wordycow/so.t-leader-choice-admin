@echo off
chcp 65001 > nul
title 업비트 봇 - 완전 자동 설치

cls
echo.
echo ==========================================
echo   업비트 스마트 봇 v5.0
echo   완전 자동 설치
echo ==========================================
echo.

cd /d "%~dp0"

echo Python 확인 중...
python --version
if %errorlevel% neq 0 (
    echo.
    echo ❌ Python이 설치되지 않았습니다!
    echo.
    echo Python 다운로드: https://www.python.org/downloads/
    echo 설치 시 "Add Python to PATH" 반드시 체크!
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   라이브러리 설치 중... (5분 소요)
echo ==========================================
echo.

python -m pip install --user --upgrade pip

echo.
echo [1/6] Flask 설치 중...
python -m pip install --user flask

echo.
echo [2/6] flask-cors 설치 중...
python -m pip install --user flask-cors

echo.
echo [3/6] pyupbit 설치 중...
python -m pip install --user pyupbit

echo.
echo [4/6] pandas 설치 중...
python -m pip install --user pandas

echo.
echo [5/6] numpy 설치 중...
python -m pip install --user numpy

echo.
echo [6/6] requests 설치 중...
python -m pip install --user requests

echo.
echo ==========================================
echo   설치 확인 중...
echo ==========================================
echo.

python -c "import flask; print('✅ Flask:', flask.__version__)"
python -c "import flask_cors; print('✅ flask-cors 설치됨')"
python -c "import pyupbit; print('✅ pyupbit 설치됨')"
python -c "import pandas; print('✅ pandas 설치됨')"
python -c "import numpy; print('✅ numpy 설치됨')"
python -c "import requests; print('✅ requests 설치됨')"

echo.
echo ==========================================
echo   ✅ 모든 라이브러리 설치 완료!
echo ==========================================
echo.
echo 이제 START.bat을 실행하세요!
echo.

pause
