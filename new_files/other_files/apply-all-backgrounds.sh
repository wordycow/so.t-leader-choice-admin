#!/bin/bash
echo "🚀 전체 페이지 배경 이미지 자동 적용 시작..."

# 배경 이미지 매핑 (페이지명:이미지명)
declare -A BACKGROUNDS
BACKGROUNDS=(
    ["up-coin.html"]="up-coin-background.png"
    ["DOWNLOAD.html"]="download-background.png"
    ["buy.html"]="buy-background.png"
    ["linkon.html"]="linkon-background.png"
    ["so.t-5admin.html"]="sot-5admin-background.png"
    ["index.html"]="index-background.png"
    ["tarot.html"]="tarot-background.png"
    ["saju.html"]="saju-background.png"
    ["ebook1.html"]="ebook1-background.png"
    ["ebook2.html"]="ebook2-background.png"
    ["ebook3.html"]="ebook3-background.png"
    ["ebook4.html"]="ebook4-background.png"
    ["download-bot.html"]="download-bot-background.png"
    ["go.html"]="go-background.png"
    ["bithumb-trend.html"]="bithumb-background.png"
    ["admin-rank-hall.html"]="admin-rank-background.png"
    ["casino-admin.html"]="casino-admin-background.png"
    ["market-view.html"]="market-view-background.png"
    ["sot.html"]="sot-background.png"
    ["stp.html"]="stp-background.png"
    ["up-coin-backup.html"]="up-coin-backup-background.png"
    ["up-coin-enhanced.html"]="up-coin-enhanced-background.png"
    ["ebook-view.html"]="ebook-view-background.png"
    ["tarot-ai-integration.html"]="tarot-ai-background.png"
    ["saju-old-backup.html"]="saju-old-backup-background.png"
    ["tarot-old-backup.html"]="tarot-old-backup-background.png"
    ["the-unique-notice.html"]="notice-v2-background.png"
    ["the-unique-promo.html"]="promo-v2-background.png"
    ["the-unique-signup.html"]="signup-v2-background.png"
    ["the-unique-work-tool.html"]="work-tool-v2-background.png"
    ["the-unique-ebook-admin.html"]="ebook-admin-v2-background.png"
    ["the-unique-ebook.html"]="ebook-v2-background.png"
)

SUCCESS=0
SKIPPED=0

for page in "${!BACKGROUNDS[@]}"; do
    img="${BACKGROUNDS[$page]}"
    
    if [[ ! -f "$page" ]]; then
        echo "⚠️  $page 파일 없음 - 스킵"
        SKIPPED=$((SKIPPED+1))
        continue
    fi
    
    if [[ ! -f "img/$img" ]]; then
        echo "⚠️  img/$img 이미지 없음 - 스킵"
        SKIPPED=$((SKIPPED+1))
        continue
    fi
    
    # body 태그의 background 또는 background-image를 img/파일명.png로 교체
    # 여러 패턴 지원
    if grep -q "body.*background" "$page"; then
        sed -i.bak "s|background:.*url(['\"].*['\"])|background: linear-gradient(135deg, rgba(11,17,32,0.95), rgba(30,40,72,0.92), rgba(15,23,42,0.95)), url('img/$img')|g" "$page"
        sed -i "s|background-image:.*url(['\"].*['\"])|background-image: linear-gradient(135deg, rgba(11,17,32,0.95), rgba(30,40,72,0.92)), url('img/$img')|g" "$page"
        echo "✅ $page → img/$img"
        SUCCESS=$((SUCCESS+1))
    else
        echo "⚠️  $page - background 스타일 못 찾음"
        SKIPPED=$((SKIPPED+1))
    fi
done

echo ""
echo "=========================================="
echo "✨ 배경 이미지 적용 완료!"
echo "성공: $SUCCESS 페이지"
echo "스킵: $SKIPPED 페이지"
echo "=========================================="
