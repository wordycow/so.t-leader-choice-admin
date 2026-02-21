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
echo ✨ 새로운 기능:
echo  • 연습 모드 (무료, 무제한)
echo  • 실전 모드 (10 USDT = 10일)
echo  • USDT 결제 시스템
echo  • 실시간 모드 전환
echo.
echo ═══════════════════════════════════════════════
echo.
echo 웹브라우저가 자동으로 열립니다!
echo.
echo 📌 사용 방법:
echo  1. 연습 모드로 먼저 테스트
echo  2. 수익 확인 후 실전 전환
echo  3. 라이선스 구매 (10 USDT)
echo  4. TXID 입력하여 활성화
echo.
echo 봇을 종료하려면:
echo  • 브라우저에서 '⏸ Bot Stop' 클릭
echo  또는
echo  • 이 창에서 Ctrl+C
echo.
echo ═══════════════════════════════════════════════
echo.

start http://localhost:5000

python upbit-smart-bot-v6.py

pause
