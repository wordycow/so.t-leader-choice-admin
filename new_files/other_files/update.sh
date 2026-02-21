#!/bin/bash

echo "🔄 업비트 봇 무중단 업데이트 시작..."

cd /home/user/webapp

# 1. Git에서 최신 코드 가져오기
echo "📥 최신 코드 다운로드 중..."
git pull origin main

# 2. 의존성 업데이트 (필요 시)
if [ -f "requirements.txt" ]; then
  echo "📦 의존성 업데이트 중..."
  pip3 install -r requirements.txt --quiet
fi

# 3. PM2로 무중단 재시작 (reload는 새 버전으로 교체)
echo "🔄 봇 재시작 중 (사용자 세션 유지)..."
pm2 reload upbit-bot

# 4. 상태 확인
echo ""
echo "✅ 업데이트 완료!"
echo ""
pm2 status

# 5. 로그 확인 (최근 20줄)
echo ""
echo "📋 최근 로그:"
pm2 logs upbit-bot --lines 20 --nostream

echo ""
echo "🎉 무중단 업데이트 성공!"
echo "💡 Tip: 'pm2 logs upbit-bot' 명령어로 실시간 로그 확인 가능"
