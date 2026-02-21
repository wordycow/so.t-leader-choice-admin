@echo off
REM 업비트 스마트 봇 v5.0 - Windows 자동 설치 및 실행
chcp 65001 >nul
color 0A

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🤖 업비트 스마트 봇 v5.0
echo 🌐 웹 대시보드 + 수익 분산 투자
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 1. Python 확인
echo 📋 1단계: Python 확인...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo.
    echo 📥 Python 설치 방법:
    echo    1. https://www.python.org/downloads/ 접속
    echo    2. 최신 Python 다운로드
    echo    3. 설치 시 "Add Python to PATH" 체크 필수!
    echo    4. 설치 후 이 프로그램 다시 실행
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% 감지됨
echo.

REM 2. 필수 라이브러리 자동 설치
echo 📦 2단계: 필수 라이브러리 자동 설치...
echo    (처음 실행 시 1~2분 소요될 수 있습니다)
echo.

python -m pip install --upgrade pip --quiet 2>nul
python -m pip install pyupbit pandas numpy flask flask-cors --quiet

if %errorlevel% equ 0 (
    echo ✅ 라이브러리 설치 완료
) else (
    echo ⚠️  일부 라이브러리 설치 실패 (무시하고 계속)
)
echo.

REM 3. 파일 다운로드 (없을 경우)
echo 📁 3단계: 파일 확인...

if not exist "upbit-smart-bot-v5.py" (
    echo ⚠️  봇 파일 다운로드 중...
    curl -L -o upbit-smart-bot-v5.py https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/upbit-smart-bot-v5.py 2>nul
    if %errorlevel% neq 0 (
        echo ❌ 다운로드 실패. 인터넷 연결을 확인하세요.
        pause
        exit /b 1
    )
)

if not exist "templates" mkdir templates

if not exist "templates\dashboard.html" (
    echo ⚠️  대시보드 다운로드 중...
    curl -L -o templates\dashboard.html https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/templates/dashboard.html 2>nul
)

echo ✅ 파일 확인 완료
echo.

REM 4. API 키 확인
echo 🔑 4단계: API 키 확인...
if not exist "api_keys.json" (
    echo ⚠️  API 키가 아직 설정되지 않았습니다.
    echo.
    echo 📋 API 키는 웹 대시보드에서 설정할 수 있습니다:
    echo    1. 봇이 시작되면
    echo    2. 브라우저에서 http://localhost:5000 접속
    echo    3. '⚙️ 설정' 버튼 클릭
    echo    4. 업비트 API 키 입력 및 저장
    echo.
) else (
    echo ✅ API 키 파일 확인 완료
    echo.
)

REM 5. 봇 실행
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🚀 봇 시작...
echo.
echo ✨ v5.0 주요 기능:
echo    • 🌐 웹 대시보드 (실시간 모니터링)
echo    • 💎 수익 분산 투자 (SOL→XRP→BTC→HBAR)
echo    • 🛡️ 시드 보호 (초기 시드 절대 보존)
echo    • ⚙️ 웹 제어 (켜기/끄기, API 설정)
echo.
echo 📱 접속 주소:
echo    🔗 http://localhost:5000
echo.
echo ⚠️  중요 안내:
echo    • 시뮬레이션 모드로 실행됩니다
echo    • 실전 모드는 웹 대시보드에서 설정 가능
echo    • 종료: Ctrl + C
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM 브라우저 자동 열기 (5초 후)
start "" /min cmd /c "timeout /t 5 /nobreak >nul && start http://localhost:5000"

REM 봇 실행
python upbit-smart-bot-v5.py

pause
