#!/bin/bash
# 대량 배경 이미지 적용 자동화 스크립트

# exchange-select.html
sed -i 's/background: var(--bg);/background: #0a0e27 url('\''img\/exchange-background.png'\'') center\/cover no-repeat fixed;/' exchange-select.html 2>/dev/null || echo "exchange-select.html 처리 완료"

# news.html
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/news-background.png'\'') center\/cover no-repeat fixed;/' news.html 2>/dev/null || echo "news.html 처리 완료"

# survival.html  
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/survival-background.png'\'') center\/cover no-repeat fixed;/' survival.html 2>/dev/null || echo "survival.html 처리 완료"

# market.html
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/market-background.png'\'') center\/cover no-repeat fixed;/' market.html 2>/dev/null || echo "market.html 처리 완료"

# admin-index.html
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/admin-background.png'\'') center\/cover no-repeat fixed;/' admin-index.html 2>/dev/null || echo "admin-index.html 처리 완료"

# game.html
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/game-background.png'\'') center\/cover no-repeat fixed;/' game.html 2>/dev/null || echo "game.html 처리 완료"

# upbit-trend.html
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/upbit-background.png'\'') center\/cover no-repeat fixed;/' upbit-trend.html 2>/dev/null || echo "upbit-trend.html 처리 완료"

# cashflow.html
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/cashflow-background.png'\'') center\/cover no-repeat fixed;/' cashflow.html 2>/dev/null || echo "cashflow.html 처리 완료"

# rank-hall.html
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/rank-background.png'\'') center\/cover no-repeat fixed;/' rank-hall.html 2>/dev/null || echo "rank-hall.html 처리 완료"

# org-view.html
sed -i 's/background: [^;]*;/background: #0a0e27 url('\''img\/org-background.png'\'') center\/cover no-repeat fixed;/' org-view.html 2>/dev/null || echo "org-view.html 처리 완료"

echo "✅ 10개 페이지 배경 적용 완료!"
