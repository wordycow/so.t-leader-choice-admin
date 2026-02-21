#!/bin/bash
# 업비트 봇 모니터링 스크립트

echo "================================================"
echo "🤖 업비트 스캘핑 봇 모니터링"
echo "================================================"
echo ""

# 1. 봇 실행 여부 확인
echo "📍 1. 봇 실행 상태 확인"
if pgrep -f "upbit-scalping-bot.py" > /dev/null; then
    echo "   ✅ 봇이 실행 중입니다"
    PID=$(pgrep -f "upbit-scalping-bot.py")
    echo "   프로세스 ID: $PID"
    
    # CPU/메모리 사용률
    echo ""
    echo "   📊 리소스 사용률:"
    ps -p $PID -o %cpu,%mem,etime,cmd | tail -n 1
else
    echo "   ❌ 봇이 실행되지 않았습니다"
    echo ""
    echo "   실행 방법:"
    echo "   - 포그라운드: python3 upbit-scalping-bot.py"
    echo "   - 백그라운드: nohup python3 upbit-scalping-bot.py > bot.log 2>&1 &"
    exit 1
fi

echo ""
echo "================================================"
echo "📋 2. 최근 로그 (마지막 20줄)"
echo "================================================"
if [ -f "bot.log" ]; then
    tail -n 20 bot.log
else
    echo "   ⚠️  로그 파일이 없습니다 (bot.log)"
fi

echo ""
echo "================================================"
echo "💰 3. 오늘의 거래 내역"
echo "================================================"
if [ -f "bot.log" ]; then
    TODAY=$(date +%Y-%m-%d)
    echo "   📅 날짜: $TODAY"
    echo ""
    
    # 매수 기록
    BUY_COUNT=$(grep "$TODAY" bot.log | grep -c "매수")
    echo "   🟢 매수: ${BUY_COUNT}회"
    grep "$TODAY" bot.log | grep "매수" | tail -n 5
    
    echo ""
    
    # 매도 기록
    SELL_COUNT=$(grep "$TODAY" bot.log | grep -c "매도")
    echo "   🔴 매도: ${SELL_COUNT}회"
    grep "$TODAY" bot.log | grep "매도" | tail -n 5
    
    echo ""
    
    # 수익률
    echo "   📈 수익률:"
    grep "$TODAY" bot.log | grep "수익률" | tail -n 5
else
    echo "   ⚠️  로그 파일이 없습니다"
fi

echo ""
echo "================================================"
echo "⚠️  4. 에러 확인"
echo "================================================"
if [ -f "bot.log" ]; then
    ERROR_COUNT=$(grep -c "ERROR\|Exception\|Traceback" bot.log)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "   ⚠️  에러 발견: ${ERROR_COUNT}개"
        grep -A 3 "ERROR\|Exception\|Traceback" bot.log | tail -n 10
    else
        echo "   ✅ 에러 없음"
    fi
else
    echo "   ⚠️  로그 파일이 없습니다"
fi

echo ""
echo "================================================"
echo "🛠️  5. 빠른 명령어"
echo "================================================"
echo "   • 실시간 로그: tail -f bot.log"
echo "   • 봇 종료: kill $PID"
echo "   • 매수 내역: grep '매수' bot.log"
echo "   • 매도 내역: grep '매도' bot.log"
echo "   • 수익 내역: grep '수익률' bot.log"
echo ""
echo "================================================"
