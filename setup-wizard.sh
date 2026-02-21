#!/bin/bash
# 업비트 스마트 봇 v5.0 - 원클릭 설치 마법사 (Mac/Linux)

echo ""
echo "========================================"
echo "  🤖 업비트 스마트 봇 v5.0"
echo "  📦 완전 자동 설치 시작!"
echo "========================================"
echo ""

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# Python 설치 확인
echo "[1/4] Python 설치 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "❌ Python3가 설치되어 있지 않습니다!"
    echo ""
    echo "📥 Python 설치 방법:"
    echo "- Mac: brew install python3"
    echo "- Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "- CentOS/Fedora: sudo yum install python3 python3-pip"
    echo ""
    exit 1
fi
echo "   ✅ Python 설치 확인 완료"
echo ""

# pip 업그레이드
echo "[2/4] pip 업그레이드 중..."
python3 -m pip install --upgrade pip > /dev/null 2>&1
echo "   ✅ pip 업그레이드 완료"
echo ""

# 필수 라이브러리 설치
echo "[3/4] 필수 라이브러리 설치 중..."
echo "   ⏳ pyupbit 설치 중..."
pip3 install pyupbit > /dev/null 2>&1
echo "   ⏳ pandas 설치 중..."
pip3 install pandas > /dev/null 2>&1
echo "   ⏳ numpy 설치 중..."
pip3 install numpy > /dev/null 2>&1
echo "   ⏳ flask 설치 중..."
pip3 install flask > /dev/null 2>&1
echo "   ⏳ flask-cors 설치 중..."
pip3 install flask-cors > /dev/null 2>&1
echo "   ✅ 모든 라이브러리 설치 완료"
echo ""

# 필요한 파일 다운로드 (없는 경우)
echo "[4/4] 봇 파일 확인 중..."
if [ ! -f "upbit-smart-bot-v5.py" ]; then
    echo "   ⏳ 봇 코드 다운로드 중..."
    curl -sS -o upbit-smart-bot-v5.py https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/upbit-smart-bot-v5.py
fi
if [ ! -d "templates" ]; then
    mkdir templates
fi
if [ ! -f "templates/dashboard.html" ]; then
    echo "   ⏳ 대시보드 다운로드 중..."
    curl -sS -o templates/dashboard.html https://raw.githubusercontent.com/wordycow/so.t-leader-choice/main/templates/dashboard.html
fi
echo "   ✅ 봇 파일 준비 완료"
echo ""

echo "========================================"
echo "  ✅ 설치 완료!"
echo "========================================"
echo ""
echo "🌐 웹 브라우저가 자동으로 열립니다..."
echo "📝 API 키를 입력하고 봇을 시작하세요!"
echo ""
echo "🔹 종료하려면 Ctrl+C를 누르세요"
echo ""

# 2초 후 브라우저 열기 (백그라운드)
(sleep 2 && open http://localhost:5000 2>/dev/null || xdg-open http://localhost:5000 2>/dev/null) &

# 봇 실행
python3 upbit-smart-bot-v5.py
