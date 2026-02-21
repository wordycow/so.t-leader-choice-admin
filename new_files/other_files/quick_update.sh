#!/bin/bash

if [ -z "$1" ]; then
    echo "사용법: ./quick_update.sh https://새로운-URL.trycloudflare.com"
    exit 1
fi

NEW_URL="$1"

echo "🔄 Ollama 터널 URL 업데이트 중..."
echo "새 URL: $NEW_URL"
echo ""

# Update .env
echo "OLLAMA_URL=$NEW_URL" > .env
echo "OLLAMA_MODEL=qwen2.5:7b-instruct" >> .env
echo "✅ .env 파일 업데이트 완료"

# Test connection
echo ""
echo "🔍 연결 테스트 중..."
timeout 15 curl -s "$NEW_URL/api/tags" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = [m['name'] for m in data.get('models', [])]
    print(f'✅ 연결 성공! 모델: {models}')
except:
    print('❌ 연결 실패 - 터널 재시작 필요')
"

# Restart server
echo ""
echo "🔄 서버 재시작 중..."
pkill -f "python3.*upbit-smart-bot"
sleep 2
nohup python3 upbit-smart-bot-v8.0-ULTIMATE.py > /tmp/bot_ollama.log 2>&1 &
sleep 3
echo "✅ 서버 재시작 완료"

echo ""
echo "🎉 완료! 이제 Emei가 AI 답변을 생성할 수 있습니다!"
echo ""
echo "테스트 질문:"
echo '- "오늘 코인 시장 어때?"'
echo '- "트레이딩 조언 해줘"'
echo '- "너 지금 기분 어때?"'
