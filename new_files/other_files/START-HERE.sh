#!/bin/bash
# 업비트 스마트 봇 v5.0 - GUI 런처

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 업비트 스마트 봇 v5.0 - GUI 런처"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python이 설치되어 있지 않습니다."
    echo ""
    echo "📥 Python 설치 방법:"
    echo "   Mac: brew install python3"
    echo "   Ubuntu: sudo apt install python3 python3-pip python3-tk"
    echo ""
    exit 1
fi

echo "✅ Python 감지됨"
echo ""

# GUI 런처 실행
echo "🚀 GUI 런처 시작..."
echo ""

python3 upbit-bot-launcher.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 실행 오류가 발생했습니다."
    echo ""
    read -p "Enter를 눌러 종료..."
fi
