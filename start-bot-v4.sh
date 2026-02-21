#!/bin/bash
# 업비트 스마트 봇 v4.0 빠른 시작 스크립트

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 업비트 스마트 스캘핑 봇 v4.0 시작"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Python 버전 확인
echo "📋 1단계: Python 버전 확인..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3이 설치되어 있지 않습니다."
    echo "   설치 방법: sudo apt install python3 (Ubuntu/Debian)"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION 감지됨"
echo ""

# 2. 필수 라이브러리 확인
echo "📦 2단계: 필수 라이브러리 확인..."
if ! python3 -c "import pyupbit" 2>/dev/null; then
    echo "⚠️  pyupbit 라이브러리가 없습니다. 설치 중..."
    pip3 install pyupbit
fi

if ! python3 -c "import pandas" 2>/dev/null; then
    echo "⚠️  pandas 라이브러리가 없습니다. 설치 중..."
    pip3 install pandas
fi

if ! python3 -c "import numpy" 2>/dev/null; then
    echo "⚠️  numpy 라이브러리가 없습니다. 설치 중..."
    pip3 install numpy
fi

echo "✅ 필수 라이브러리 확인 완료"
echo ""

# 3. API 키 확인
echo "🔑 3단계: API 키 설정 확인..."
if [ ! -f "api_keys.json" ]; then
    echo "❌ api_keys.json 파일이 없습니다."
    echo ""
    echo "📋 설정 방법:"
    echo "1. 업비트에서 API 키 발급 (https://upbit.com)"
    echo "2. api_keys.json 파일 생성:"
    echo '   {
     "access_key": "여기에_실제_키_입력",
     "secret_key": "여기에_실제_키_입력"
   }'
    echo ""
    echo "3. 다시 이 스크립트 실행"
    exit 1
fi

echo "✅ API 키 파일 확인 완료"
echo ""

# 4. 봇 실행
echo "🚀 4단계: 봇 실행..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  주의사항:"
echo "   • 시뮬레이션 모드로 실행됩니다 (실제 주문 없음)"
echo "   • 실전 모드는 코드에서 주석 해제 필요"
echo "   • 종료: Ctrl + C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
sleep 2

python3 upbit-smart-bot-v4.py
