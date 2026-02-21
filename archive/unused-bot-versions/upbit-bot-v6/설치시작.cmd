@echo off
chcp 65001 > nul
title 업비트 스마트 봇 v6.0 - 설치 시작

cd /d "%~dp0"

cls
echo.
echo ╔═══════════════════════════════════════════════╗
echo ║                                               ║
echo ║    🤖 업비트 스마트 봇 v6.0                  ║
echo ║         완전 자동 설치 시작                  ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo 📦 자동 설치를 시작합니다...
echo.
echo ⏱️  예상 소요 시간: 2-5분
echo.
echo 잠시만 기다려주세요...
echo.

REM 관리자 권한 확인 (선택적)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  일반 사용자 권한으로 실행 중
    echo    (문제 발생 시 우클릭 → "관리자 권한으로 실행")
    echo.
)

call INSTALL.bat

if %errorLevel% equ 0 (
    echo.
    echo ╔═══════════════════════════════════════════════╗
    echo ║                                               ║
    echo ║  ✅ 설치가 완료되었습니다!                   ║
    echo ║                                               ║
    echo ╚═══════════════════════════════════════════════╝
    echo.
    echo 📌 다음 단계:
    echo  1. 'START.cmd' 파일을 더블클릭하세요
    echo  2. 브라우저가 자동으로 열립니다
    echo  3. 업비트 API 키를 입력하고 봇을 시작하세요
    echo.
) else (
    echo.
    echo ❌ 설치 중 오류가 발생했습니다!
    echo.
    echo 📥 해결 방법:
    echo  1. 이 파일에 우클릭 → "관리자 권한으로 실행"
    echo  2. 인터넷 연결 확인
    echo  3. Python이 설치되어 있는지 확인
    echo     https://www.python.org/downloads/
    echo.
)

pause
