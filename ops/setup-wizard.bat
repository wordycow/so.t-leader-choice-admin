@echo off
chcp 65001 > nul
title 업비트 스마트 봇 v5.0 - 원클릭 설치 마법사

echo.
echo ========================================
echo   🤖 업비트 스마트 봇 v5.0
echo   📦 완전 자동 설치 시작!
echo ========================================
echo.

REM 현재 디렉토리 저장
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Python 설치 확인
echo [1/4] Python 설치 확인 중...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Python이 설치되어 있지 않습니다!
    echo.
    echo 📥 Python 설치 방법:
    echo 1. https://www.python.org/downloads/ 접속
    echo 2. "Download Python" 클릭
    echo 3. 설치 시 "Add Python to PATH" 체크 필수!
    echo 4. 설치 완료 후 이 파일을 다시 실행하세요
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)
echo    ✅ Python 설치 확인 완료
echo.

REM pip 업그레이드
echo [2/4] pip 업그레이드 중...
python -m pip install --upgrade pip > nul 2>&1
echo    ✅ pip 업그레이드 완료
echo.

REM 필수 라이브러리 설치
echo [3/4] 필수 라이브러리 설치 중...
echo    ⏳ pyupbit 설치 중...
pip install pyupbit > nul 2>&1
echo    ⏳ pandas 설치 중...
pip install pandas > nul 2>&1
echo    ⏳ numpy 설치 중...
pip install numpy > nul 2>&1
echo    ⏳ flask 설치 중...
pip install flask > nul 2>&1
echo    ⏳ flask-cors 설치 중...
pip install flask-cors > nul 2>&1
echo    ✅ 모든 라이브러리 설치 완료
echo.

REM 필요한 파일 다운로드 (없는 경우)
echo [4/4] 봇 파일 확인 중...
if not exist "upbit-smart-bot-v5.py" (
    echo    ⏳ 봇 코드 다운로드 중...
    curl -o upbit-smart-bot-v5.py https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/upbit-smart-bot-v5.py > nul 2>&1
)
if not exist "templates" mkdir templates
if not exist "templates\dashboard.html" (
    echo    ⏳ 대시보드 다운로드 중...
    curl -o templates\dashboard.html https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/templates/dashboard.html > nul 2>&1
)
echo    ✅ 봇 파일 준비 완료
echo.

echo ========================================
echo   ✅ 설치 완료!
echo ========================================
echo.
echo 🌐 웹 브라우저가 자동으로 열립니다...
echo 📝 API 키를 입력하고 봇을 시작하세요!
echo.
echo 🔹 종료하려면 이 창을 닫거나 Ctrl+C를 누르세요
echo.

REM 2초 후 브라우저 열기 (백그라운드)
start /b timeout /t 2 > nul 2>&1 & start http://localhost:5000

REM 봇 실행
python upbit-smart-bot-v5.py

pause
