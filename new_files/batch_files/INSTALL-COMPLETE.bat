@echo off
chcp 65001 > nul
title 업비트 봇 설치

cls
echo.
echo ==========================================
echo   업비트 스마트 봇 v5.0
echo   완전 자동 설치
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/3] Python 확인...
python --version
if %errorlevel% neq 0 (
    echo.
    echo ❌ Python이 없습니다!
    echo Python 설치: https://www.python.org/downloads/
    echo 설치 시 "Add Python to PATH" 체크!
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] 필수 라이브러리 설치 중... (3분 소요)
echo.

python -m pip install --upgrade pip --user
python -m pip install --user flask
python -m pip install --user flask-cors
python -m pip install --user pyupbit
python -m pip install --user pandas
python -m pip install --user numpy
python -m pip install --user requests

echo.
echo [3/3] 설치 확인...
python -c "import flask; print('✅ Flask:', flask.__version__)"
python -c "import flask_cors; print('✅ flask-cors 설치됨')"
python -c "import pyupbit; print('✅ pyupbit 설치됨')"
python -c "import pandas; print('✅ pandas 설치됨')"

echo.
echo ==========================================
echo   ✅ 모든 라이브러리 설치 완료!
echo.
echo   이제 START.bat을 실행하세요!
echo ==========================================
echo.

pause
