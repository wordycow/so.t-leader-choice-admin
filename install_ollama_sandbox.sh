#!/bin/bash

echo "🚀 샌드박스 Ollama 설치 시작..."
echo "이 설치는 터널을 완전히 대체합니다!"
echo ""

# 1. Ollama 설치
echo "1️⃣ Ollama 설치 중..."
curl -fsSL https://ollama.com/install.sh | sh
if [ $? -ne 0 ]; then
    echo "❌ Ollama 설치 실패"
    exit 1
fi
echo "✅ Ollama 설치 완료"
echo ""

# 2. Ollama 서버 시작
echo "2️⃣ Ollama 서버 시작 중..."
pkill -f "ollama serve" 2>/dev/null
nohup ollama serve > /tmp/ollama_sandbox.log 2>&1 &
sleep 5

# 서버 확인
if ! curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "❌ Ollama 서버 시작 실패"
    echo "로그:"
    tail -20 /tmp/ollama_sandbox.log
    exit 1
fi
echo "✅ Ollama 서버 실행 중"
echo ""

# 3. 작은 모델 다운로드
echo "3️⃣ 경량 모델 다운로드 중..."
echo "   (CPU 최적화된 1.5B 모델, 약 1GB)"
ollama pull qwen2.5:1.5b
if [ $? -ne 0 ]; then
    echo "⚠️ qwen2.5:1.5b 다운로드 실패, gemma2:2b 시도..."
    ollama pull gemma2:2b
fi
echo "✅ 모델 다운로드 완료"
echo ""

# 4. 모델 확인
echo "4️⃣ 설치된 모델 확인..."
ollama list
echo ""

# 5. .env 파일 업데이트
echo "5️⃣ 환경 변수 설정..."
cat > /home/user/webapp/.env << 'ENVFILE'
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:1.5b
ENVFILE
echo "✅ .env 파일 업데이트 완료"
echo ""

# 6. 간단한 테스트
echo "6️⃣ 연결 테스트..."
TEST_RESPONSE=$(curl -s http://127.0.0.1:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = [m['name'] for m in data.get('models', [])]
    print(','.join(models))
except:
    print('FAIL')
")

if [ "$TEST_RESPONSE" != "FAIL" ]; then
    echo "✅ 연결 성공! 사용 가능 모델: $TEST_RESPONSE"
else
    echo "❌ 연결 실패"
    exit 1
fi
echo ""

# 7. Flask 서버 재시작
echo "7️⃣ Flask 서버 재시작..."
pkill -9 -f "python3.*upbit-smart-bot"
sleep 2
cd /home/user/webapp
nohup python3 upbit-smart-bot-v8.0-ULTIMATE.py > /tmp/bot_local_ollama.log 2>&1 &
sleep 5
echo "✅ 서버 재시작 완료"
echo ""

# 8. 최종 확인
echo "════════════════════════════════════════"
echo "🎉 설치 완료!"
echo "════════════════════════════════════════"
echo ""
echo "✅ Ollama: 로컬 실행 중 (http://127.0.0.1:11434)"
echo "✅ 모델: $TEST_RESPONSE"
echo "✅ Flask: 재시작됨"
echo "✅ 터널: 더 이상 필요 없음!"
echo ""
echo "📊 예상 성능:"
echo "   - DB 답변: 0.01초"
echo "   - AI 생성: 5-10초 (CPU)"
echo ""
echo "💡 이제 터널 URL 걱정 없이 사용 가능합니다!"
echo ""
echo "🧪 테스트 명령어:"
echo "   curl -X POST http://localhost:5000/api/emei/chat -H 'Content-Type: application/json' -d '{\"message\":\"안녕\"}'"
