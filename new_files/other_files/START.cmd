@echo off
chcp 65001 > nul
title 업비트 스마트 봇 v6.0 - 라이선스 시스템

cd /d "%~dp0"

cls
echo.
echo ╔═══════════════════════════════════════════════╗
echo ║                                               ║
echo ║    🤖 업비트 스마트 봇 v6.0                  ║
echo ║         라이선스 시스템 탑재                 ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.

REM Python 설치 확인
echo [1/3] Python 확인 중...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ❌ Python이 설치되어 있지 않습니다!
    echo.
    echo 📥 해결 방법:
    echo  1. https://www.python.org/downloads/ 에서 Python 다운로드
    echo  2. 설치 시 "Add Python to PATH" 체크 필수!
    echo  3. 설치 후 컴퓨터 재시작
    echo  4. 다시 이 파일 실행
    echo.
    pause
    exit /b 1
)
echo    ✅ Python 설치됨

REM 필수 라이브러리 확인
echo [2/3] 필수 라이브러리 확인 중...
python -c "import flask" >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ❌ 필수 라이브러리가 설치되지 않았습니다!
    echo.
    echo 📥 자동 설치를 시작합니다...
    echo.
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo.
        echo ❌ 자동 설치 실패!
        echo.
        echo 📥 해결 방법:
        echo  1. '설치시작.cmd' 파일을 우클릭
        echo  2. '관리자 권한으로 실행' 선택
        echo  3. 설치 완료 후 다시 START.cmd 실행
        echo.
        pause
        exit /b 1
    )
)
echo    ✅ 라이브러리 설치 완료

REM 포트 5000 사용 중 확인
echo [3/3] 포트 확인 중...
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorLevel% equ 0 (
    echo.
    echo ⚠️  포트 5000이 이미 사용 중입니다!
    echo.
    echo 📥 해결 방법:
    echo  1. 다른 프로그램을 종료해주세요
    echo  2. 또는 작업 관리자에서 포트 5000 사용 프로세스 종료
    echo.
    choice /C YN /M "그래도 계속 실행하시겠습니까?"
    if %errorLevel% equ 2 exit /b 1
)
echo    ✅ 포트 사용 가능

echo.
echo ═══════════════════════════════════════════════
echo.
echo ✨ 새로운 기능:
echo  • 연습 모드 (무료, 무제한)
echo  • 실전 모드 (1 USDT = 1일, 최소 10 USDT)
echo  • USDT 결제 시스템
echo  • 실시간 모드 전환
echo.
echo 📌 사용 방법:
echo  1. 연습 모드로 먼저 테스트
echo  2. 수익 확인 후 실전 전환
echo  3. 라이선스 구매 (최소 10 USDT)
echo  4. TXID 입력하여 활성화
echo.
echo 봇을 종료하려면:
echo  • 브라우저에서 '⏸ Bot Stop' 클릭
echo  또는
echo  • 이 창에서 Ctrl+C
echo.
echo ═══════════════════════════════════════════════
echo.
echo 🚀 봇 시작 중...
echo.
echo 브라우저가 자동으로 열립니다!
echo (만약 안 열리면 수동으로 http://localhost:5000 접속)
echo.

timeout /t 2 /nobreak >nul
start http://localhost:5000

python upbit-smart-bot-v6.py

if %errorLevel% neq 0 (
    echo.
    echo ❌ 봇 실행 중 오류 발생!
    echo.
    echo 📥 해결 방법:
    echo  1. 위의 에러 메시지 확인
    echo  2. requirements.txt 파일이 있는지 확인
    echo  3. '설치시작.cmd'를 관리자 권한으로 다시 실행
    echo  4. 문제가 계속되면 스크린샷과 함께 문의
    echo.
)

pause
