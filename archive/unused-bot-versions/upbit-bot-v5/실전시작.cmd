@echo off
chcp 65001 > nul
title 업비트 봇 실전 모드 시작 ⚠️

cd /d "%~dp0"

cls
echo.
echo ╔═══════════════════════════════════════════════╗
echo ║                                               ║
echo ║    🔴 업비트 스마트 봇 v5.0                  ║
echo ║         실전 모드 (LIVE TRADING)             ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo ⚠️ ⚠️ ⚠️  경고! 실제 거래가 실행됩니다!  ⚠️ ⚠️ ⚠️
echo.
echo 시작 전 필수 확인사항:
echo.
echo  ✅ 시뮬레이션 모드로 24시간 이상 테스트 완료
echo  ✅ 매매 로직을 완전히 이해함
echo  ✅ 소액으로 시작 (10만원 이하 권장)
echo  ✅ API Key에 출금 권한이 없음을 확인
echo  ✅ 손실을 감당할 수 있는 금액만 투자
echo.
echo ═══════════════════════════════════════════════
echo.

:: 사용자 확인
set /p confirm="정말로 실전 모드를 시작하시겠습니까? (yes 입력): "
if not "%confirm%"=="yes" (
    echo.
    echo ❌ 취소되었습니다.
    echo    시뮬레이션 모드를 먼저 충분히 테스트하세요!
    echo.
    pause
    exit /b
)

echo.
echo ═══════════════════════════════════════════════
echo   실전 모드 시작...
echo ═══════════════════════════════════════════════
echo.
echo 웹브라우저가 자동으로 열립니다!
echo 브라우저에서 API 키를 입력하세요.
echo.
echo 🔴 실전 모드 특징:
echo  - 실제 매수/매도 주문이 실행됩니다
echo  - 수익/손실이 실제로 발생합니다
echo  - 첫 1시간은 손절 보호 모드 활성화
echo  - 초기 시드 보호 기능 작동
echo.
echo 봇을 종료하려면:
echo  1. 브라우저에서 '⏸ Bot Stop' 클릭
echo  또는
echo  2. 이 창에서 Ctrl+C
echo.
echo ═══════════════════════════════════════════════
echo.

start http://localhost:5000

python upbit-smart-bot-v5-LIVE.py

pause
