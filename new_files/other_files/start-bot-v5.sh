#!/bin/bash
# 업비트 스마트 봇 v5.0 빠른 시작 스크립트

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 업비트 스마트 스캘핑 봇 v5.0 시작"
echo "🌐 웹 대시보드 + 수익 분산 투자"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Python 버전 확인
echo "📋 1단계: Python 버전 확인..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3이 설치되어 있지 않습니다."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION 감지됨"
echo ""

# 2. 필수 라이브러리 확인
echo "📦 2단계: 필수 라이브러리 확인..."

# pyupbit
if ! python3 -c "import pyupbit" 2>/dev/null; then
    echo "⚠️  pyupbit 설치 중..."
    pip3 install pyupbit --quiet
fi

# pandas
if ! python3 -c "import pandas" 2>/dev/null; then
    echo "⚠️  pandas 설치 중..."
    pip3 install pandas --quiet
fi

# numpy
if ! python3 -c "import numpy" 2>/dev/null; then
    echo "⚠️  numpy 설치 중..."
    pip3 install numpy --quiet
fi

# flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  flask 설치 중..."
    pip3 install flask --quiet
fi

# flask-cors
if ! python3 -c "import flask_cors" 2>/dev/null; then
    echo "⚠️  flask-cors 설치 중..."
    pip3 install flask-cors --quiet
fi

echo "✅ 필수 라이브러리 확인 완료"
echo ""

# 3. 파일 확인
echo "📁 3단계: 파일 확인..."

if [ ! -f "upbit-smart-bot-v5.py" ]; then
    echo "❌ upbit-smart-bot-v5.py 파일이 없습니다."
    echo ""
    echo "다운로드 방법:"
    echo "curl -o upbit-smart-bot-v5.py https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/upbit-smart-bot-v5.py"
    exit 1
fi

if [ ! -d "templates" ]; then
    echo "⚠️  templates 폴더 생성 중..."
    mkdir templates
fi

if [ ! -f "templates/dashboard.html" ]; then
    echo "⚠️  dashboard.html 다운로드 중..."
    curl -o templates/dashboard.html https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/templates/dashboard.html 2>/dev/null
fi

echo "✅ 파일 확인 완료"
echo ""

# 4. API 키 확인
echo "🔑 4단계: API 키 설정 확인..."
if [ ! -f "api_keys.json" ]; then
    echo "⚠️  API 키가 설정되지 않았습니다."
    echo ""
    echo "📋 설정 방법:"
    echo "1. 봇을 시작한 후"
    echo "2. 브라우저에서 http://localhost:5000 접속"
    echo "3. '⚙️ 설정' 버튼 클릭"
    echo "4. API 키 입력 및 저장"
    echo ""
else
    echo "✅ API 키 파일 확인 완료"
    echo ""
fi

# 5. 봇 실행
echo "🚀 5단계: 봇 실행..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ v5.0 주요 기능:"
echo "   • 🌐 웹 대시보드 (실시간 모니터링)"
echo "   • 💎 수익 분산 투자 (SOL→XRP→BTC→HBAR)"
echo "   • 🛡️ 시드 보호 (초기 시드 절대 보존)"
echo "   • ⚙️ 웹 제어 (켜기/끄기, API 설정)"
echo ""
echo "📱 접속 주소:"
echo "   로컬: http://localhost:5000"
echo "   PC: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "⚠️  주의사항:"
echo "   • 시뮬레이션 모드로 실행됩니다"
echo "   • 실전 모드는 코드에서 주석 해제 필요"
echo "   • 종료: Ctrl + C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 2초 대기 후 실행
sleep 2

python3 upbit-smart-bot-v5.py
