@echo off
chcp 65001 > nul
echo ========================================
echo 🚀 Upbit Trading Bot v8.0 ULTIMATE
echo ========================================
echo.

cd /d "%~dp0"

REM Python 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다!
    echo    https://www.python.org/downloads/ 에서 설치하세요.
    pause
    exit /b 1
)

echo ✅ Python 확인 완료
echo.

REM 기존 프로세스 확인
tasklist | find "python" | find "upbit-smart-bot-v8.0-ULTIMATE.py" > nul
if %errorlevel% equ 0 (
    echo ⚠️  봇이 이미 실행 중입니다!
    echo    종료하려면 노트북_종료.bat을 실행하세요.
    pause
    exit /b 0
)

echo 📦 필요한 패키지 설치 중...
pip install flask pyupbit pandas ta numpy requests jwt python-dotenv > nul 2>&1
echo ✅ 패키지 설치 완료
echo.

echo 🚀 봇 시작 중...
start /B python upbit-smart-bot-v8.0-ULTIMATE.py
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo ✅ 봇이 시작되었습니다!
echo ========================================
echo.
echo 📍 접속 주소:
echo    http://localhost:5000
echo.
echo 💡 브라우저에서 위 주소로 접속하세요!
echo.
echo ⚠️  이 창을 닫으면 봇이 종료됩니다!
echo    봇을 중지하려면 노트북_종료.bat을 실행하세요.
echo.
pause
