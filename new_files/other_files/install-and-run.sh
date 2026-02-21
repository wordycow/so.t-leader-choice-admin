#!/bin/bash
# 업비트 스마트 봇 v5.0 - 완전 자동 설치 및 실행

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 업비트 스마트 봇 v5.0"
echo "🌐 웹 대시보드 + 수익 분산 투자"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Python 확인 및 설치 안내
echo "📋 1단계: Python 확인..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python이 설치되어 있지 않습니다."
    echo ""
    echo "📥 Python 설치 방법:"
    echo "   Windows: https://www.python.org/downloads/"
    echo "   Mac: brew install python3"
    echo "   Ubuntu: sudo apt install python3 python3-pip"
    echo ""
    read -p "Python을 설치한 후 Enter를 누르세요..."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION 감지됨"
echo ""

# 2. 필수 라이브러리 자동 설치
echo "📦 2단계: 필수 라이브러리 자동 설치..."
echo "   (처음 실행 시 1~2분 소요될 수 있습니다)"
echo ""

pip3 install --upgrade pip --quiet 2>/dev/null
pip3 install pyupbit pandas numpy flask flask-cors --quiet

if [ $? -eq 0 ]; then
    echo "✅ 라이브러리 설치 완료"
else
    echo "⚠️  일부 라이브러리 설치 실패 (무시하고 계속)"
fi
echo ""

# 3. 파일 다운로드 (없을 경우)
echo "📁 3단계: 파일 확인..."

if [ ! -f "upbit-smart-bot-v5.py" ]; then
    echo "⚠️  봇 파일 다운로드 중..."
    curl -L -o upbit-smart-bot-v5.py https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/upbit-smart-bot-v5.py 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ 다운로드 실패. 인터넷 연결을 확인하세요."
        exit 1
    fi
fi

if [ ! -d "templates" ]; then
    mkdir templates
fi

if [ ! -f "templates/dashboard.html" ]; then
    echo "⚠️  대시보드 다운로드 중..."
    curl -L -o templates/dashboard.html https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/templates/dashboard.html 2>/dev/null
fi

echo "✅ 파일 확인 완료"
echo ""

# 4. API 키 확인
echo "🔑 4단계: API 키 확인..."
if [ ! -f "api_keys.json" ]; then
    echo "⚠️  API 키가 아직 설정되지 않았습니다."
    echo ""
    echo "📋 API 키는 웹 대시보드에서 설정할 수 있습니다:"
    echo "   1. 봇이 시작되면"
    echo "   2. 브라우저에서 http://localhost:5000 접속"
    echo "   3. '⚙️ 설정' 버튼 클릭"
    echo "   4. 업비트 API 키 입력 및 저장"
    echo ""
else
    echo "✅ API 키 파일 확인 완료"
    echo ""
fi

# 5. 봇 실행
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 봇 시작..."
echo ""
echo "✨ v5.0 주요 기능:"
echo "   • 🌐 웹 대시보드 (실시간 모니터링)"
echo "   • 💎 수익 분산 투자 (SOL→XRP→BTC→HBAR)"
echo "   • 🛡️ 시드 보호 (초기 시드 절대 보존)"
echo "   • ⚙️ 웹 제어 (켜기/끄기, API 설정)"
echo ""
echo "📱 접속 주소:"
echo "   🔗 http://localhost:5000"
echo ""
echo "⚠️  중요 안내:"
echo "   • 시뮬레이션 모드로 실행됩니다"
echo "   • 실전 모드는 웹 대시보드에서 설정 가능"
echo "   • 종료: Ctrl + C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 브라우저 자동 열기 (5초 후)
(sleep 5 && (
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5000 2>/dev/null
    elif command -v open &> /dev/null; then
        open http://localhost:5000 2>/dev/null
    elif command -v start &> /dev/null; then
        start http://localhost:5000 2>/dev/null
    fi
)) &

# 봇 실행
python3 upbit-smart-bot-v5.py
