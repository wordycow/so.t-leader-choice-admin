@echo off
REM 업비트 스마트 봇 v5.0 - GUI 런처
chcp 65001 >nul
color 0A

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🤖 업비트 스마트 봇 v5.0 - GUI 런처
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo.
    echo 📥 Python 설치가 필요합니다:
    echo    https://www.python.org/downloads/
    echo.
    echo 설치 시 "Add Python to PATH" 체크 필수!
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 감지됨
echo.

REM GUI 런처 실행
echo 🚀 GUI 런처 시작...
echo.

python upbit-bot-launcher.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 실행 오류가 발생했습니다.
    echo.
    pause
)
