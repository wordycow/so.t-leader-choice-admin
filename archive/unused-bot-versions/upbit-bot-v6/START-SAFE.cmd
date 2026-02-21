@echo off
chcp 65001 > nul
title 업비트 스마트 봇 v6.0 시작

cd /d "%~dp0"

cls
echo.
echo ╔═══════════════════════════════════════════════╗
echo ║                                               ║
echo ║    🤖 업비트 스마트 봇 v6.0                  ║
echo ║         Professional Trading System          ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.

:: Python 확인
echo [1/3] Python 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Python이 설치되지 않았습니다!
    echo.
    echo 📥 Python 다운로드: https://www.python.org/downloads/
    echo.
    echo ⚠️  설치 시 "Add Python to PATH" 반드시 체크!
    echo.
    echo 설치 후 이 창을 닫고 다시 실행하세요.
    echo.
    pause
    exit /b 1
)
echo ✅ Python 설치 확인 완료!
echo.

:: 라이브러리 확인
echo [2/3] 필수 라이브러리 확인 중...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Flask가 설치되지 않았습니다!
    echo.
    echo 먼저 "설치시작.cmd"를 실행해주세요!
    echo.
    echo 또는 수동 설치:
    echo   python -m pip install flask flask-cors pyupbit pandas numpy requests
    echo.
    pause
    exit /b 1
)
echo ✅ 라이브러리 확인 완료!
echo.

:: 봇 파일 확인
echo [3/3] 봇 파일 확인 중...
if not exist "upbit-smart-bot-v6.py" (
    echo.
    echo ❌ upbit-smart-bot-v6.py 파일이 없습니다!
    echo.
    echo 현재 폴더: %CD%
    echo.
    echo 올바른 폴더에서 실행하고 있는지 확인하세요.
    echo.
    pause
    exit /b 1
)
echo ✅ 봇 파일 확인 완료!
echo.

echo ═══════════════════════════════════════════════
echo   모든 준비 완료! 봇을 시작합니다...
echo ═══════════════════════════════════════════════
echo.
echo 🌐 웹 브라우저가 자동으로 열립니다
echo    주소: http://localhost:5000
echo.
echo 💡 이 창을 닫지 마세요!
echo    이 창이 열려있어야 봇이 작동합니다.
echo.
echo 🛑 봇 종료 방법:
echo    1. 브라우저에서 "STOP BOT" 클릭
echo    또는
echo    2. 이 창에서 Ctrl+C
echo.
echo ═══════════════════════════════════════════════
echo.

:: 3초 후 브라우저 자동 실행
timeout /t 3 /nobreak >nul
start http://localhost:5000

:: 봇 실행
python upbit-smart-bot-v6.py

:: 봇이 종료되면
echo.
echo ═══════════════════════════════════════════════
echo   봇이 종료되었습니다.
echo ═══════════════════════════════════════════════
echo.
echo 오류가 발생했다면:
echo  1. Python 버전 확인: python --version
echo  2. 라이브러리 재설치: 설치시작.cmd 실행
echo  3. 방화벽 확인: 5000 포트 허용
echo.
pause
