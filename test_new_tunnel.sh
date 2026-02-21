#!/bin/bash

NEW_URL="https://handles-convenience-nylon-trout.trycloudflare.com"

echo "🔍 Ollama 터널 완전 진단 시작..."
echo "터널 URL: $NEW_URL"
echo ""

# 1. Basic ping test
echo "1️⃣ 터널 도메인 확인..."
host handles-convenience-nylon-trout.trycloudflare.com 2>&1 | head -3

echo ""
echo "2️⃣ HTTPS 연결 테스트 (30초 타임아웃)..."
timeout 30 curl -v "$NEW_URL/api/tags" 2>&1 | grep -E "Connected|HTTP|error|timeout" | head -10

echo ""
echo "3️⃣ 단순 GET 테스트 (60초 타임아웃)..."
timeout 60 curl -s --max-time 60 "$NEW_URL/api/tags" 2>&1 | head -5

echo ""
echo "📊 진단 결과:"
echo "- 만약 'timeout' 에러: Ollama 서버가 응답하지 않음"
echo "- 만약 'Connection refused': Ollama 서버가 중지됨"
echo "- 만약 'DNS resolution failed': 터널 URL 문제"
echo "- 만약 응답 없음: Cloudflare 터널이 Ollama와 연결되지 않음"
echo ""
echo "💡 해결책:"
echo "1. 노트북에서: curl http://localhost:11434/api/tags"
echo "2. 응답 없으면: ollama serve"
echo "3. 터널 재시작: cloudflared tunnel --url http://localhost:11434"
echo "4. 새 URL 공유"
