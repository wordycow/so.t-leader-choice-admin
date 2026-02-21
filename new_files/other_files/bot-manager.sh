#!/bin/bash
# 업비트 봇 관리 스크립트 (시작/중지/재시작/상태)

BOT_SCRIPT="upbit-scalping-bot.py"
LOG_FILE="bot.log"

case "$1" in
    start)
        echo "🚀 봇 시작 중..."
        if pgrep -f "$BOT_SCRIPT" > /dev/null; then
            echo "⚠️  봇이 이미 실행 중입니다"
            PID=$(pgrep -f "$BOT_SCRIPT")
            echo "   프로세스 ID: $PID"
        else
            nohup python3 "$BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
            sleep 2
            if pgrep -f "$BOT_SCRIPT" > /dev/null; then
                PID=$(pgrep -f "$BOT_SCRIPT")
                echo "✅ 봇 시작 완료! (PID: $PID)"
                echo "   로그 확인: tail -f $LOG_FILE"
            else
                echo "❌ 봇 시작 실패!"
                echo "   로그 확인: cat $LOG_FILE"
            fi
        fi
        ;;
    
    stop)
        echo "🛑 봇 종료 중..."
        if pgrep -f "$BOT_SCRIPT" > /dev/null; then
            pkill -f "$BOT_SCRIPT"
            sleep 1
            if pgrep -f "$BOT_SCRIPT" > /dev/null; then
                echo "⚠️  강제 종료..."
                pkill -9 -f "$BOT_SCRIPT"
            fi
            echo "✅ 봇 종료 완료"
        else
            echo "⚠️  실행 중인 봇이 없습니다"
        fi
        ;;
    
    restart)
        echo "🔄 봇 재시작 중..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        echo "📊 봇 상태 확인"
        if pgrep -f "$BOT_SCRIPT" > /dev/null; then
            PID=$(pgrep -f "$BOT_SCRIPT")
            echo "✅ 실행 중 (PID: $PID)"
            echo ""
            ps -p $PID -o pid,ppid,%cpu,%mem,etime,cmd
            echo ""
            echo "📋 최근 로그:"
            tail -n 10 "$LOG_FILE"
        else
            echo "❌ 실행 중이 아닙니다"
        fi
        ;;
    
    log)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "⚠️  로그 파일이 없습니다 ($LOG_FILE)"
        fi
        ;;
    
    *)
        echo "업비트 스캘핑 봇 관리 스크립트"
        echo ""
        echo "사용법: $0 {start|stop|restart|status|log}"
        echo ""
        echo "명령어:"
        echo "  start   - 봇 시작"
        echo "  stop    - 봇 종료"
        echo "  restart - 봇 재시작"
        echo "  status  - 봇 상태 확인"
        echo "  log     - 실시간 로그 보기"
        echo ""
        echo "예시:"
        echo "  ./bot-manager.sh start"
        echo "  ./bot-manager.sh status"
        echo "  ./bot-manager.sh log"
        exit 1
        ;;
esac
