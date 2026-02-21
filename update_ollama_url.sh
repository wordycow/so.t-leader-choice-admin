#!/bin/bash
# 이메이 Ollama URL 업데이트 스크립트

if [ -z "$1" ]; then
    echo "❌ 사용법: ./update_ollama_url.sh <OLLAMA_TUNNEL_URL>"
    echo ""
    echo "예시:"
    echo "  ./update_ollama_url.sh https://xxxx-yyyy-zzzz.trycloudflare.com"
    exit 1
fi

OLLAMA_URL="$1"

echo "🔄 이메이 Ollama URL 업데이트 중..."
echo "   새 URL: $OLLAMA_URL"
echo ""

# 1. 환경변수 설정 파일 생성
cat > /home/user/webapp/.env << EOF
OLLAMA_URL=$OLLAMA_URL
OLLAMA_MODEL=qwen2.5:7b-instruct
EOF

echo "✅ .env 파일 생성 완료"

# 2. 연결 테스트
echo ""
echo "🧪 연결 테스트 중..."

if curl -s --connect-timeout 5 "$OLLAMA_URL/api/tags" > /dev/null; then
    echo "✅ Ollama 연결 성공!"
    
    # 3. 서버 재시작
    echo ""
    echo "🔄 서버 재시작 중..."
    pkill -f "python3.*upbit-smart-bot" 2>/dev/null
    sleep 1
    
    cd /home/user/webapp
    export OLLAMA_URL="$OLLAMA_URL"
    export OLLAMA_MODEL="qwen2.5:7b-instruct"
    nohup python3 upbit-smart-bot-v8.0-ULTIMATE.py > /tmp/bot_ollama.log 2>&1 &
    
    sleep 3
    
    if ps aux | grep -v grep | grep "python3.*upbit-smart-bot" > /dev/null; then
        echo "✅ 서버 재시작 완료!"
        echo ""
        echo "🎉 이메이가 이제 Ollama와 연결되었습니다!"
        echo "   URL: https://5000-imdh8jpm1izc140vdjj3t-3844e1b6.sandbox.novita.ai"
        echo ""
        echo "테스트해보세요:"
        echo "  - '너 뭐해?' (DB에 없는 새로운 질문)"
        echo "  - '오늘 날씨 어때?' (AI가 생성하는 답변)"
    else
        echo "❌ 서버 시작 실패. 로그 확인: tail -50 /tmp/bot_ollama.log"
    fi
else
    echo "❌ Ollama 연결 실패!"
    echo ""
    echo "확인사항:"
    echo "  1. URL이 정확한가요?"
    echo "  2. 노트북에서 Ollama가 실행 중인가요?"
    echo "  3. Cloudflare 터널이 활성화되어 있나요?"
fi
