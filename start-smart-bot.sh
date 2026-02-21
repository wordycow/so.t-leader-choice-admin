#!/bin/bash
# 업비트 스마트 봇 실행 스크립트

echo "🤖 업비트 스마트 스캘핑 봇 v2.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# API 키 파일 확인
if [ ! -f "api_keys.json" ]; then
    echo "❌ api_keys.json 파일이 없습니다!"
    echo ""
    echo "📋 API 키 설정 방법:"
    echo "   1. API-KEYS-SETUP.md 파일 읽기"
    echo "   2. api_keys.json.example을 복사:"
    echo "      cp api_keys.json.example api_keys.json"
    echo "   3. 실제 API 키로 수정:"
    echo "      nano api_keys.json"
    echo ""
    exit 1
fi

# Python 패키지 확인
echo "📦 필수 패키지 확인 중..."
python3 -c "import pyupbit, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  필수 패키지가 설치되지 않았습니다!"
    echo ""
    echo "설치 명령어:"
    echo "  pip install pyupbit pandas numpy"
    echo ""
    read -p "지금 설치하시겠습니까? (y/n): " answer
    if [ "$answer" = "y" ]; then
        pip install pyupbit pandas numpy
    else
        exit 1
    fi
fi

echo "✅ 준비 완료!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 봇 실행
python3 upbit-smart-bot.py
