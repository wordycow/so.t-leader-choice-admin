#!/bin/bash
echo "=== 배경 이미지 적용 현황 체크 ==="
echo ""
TOTAL=0
WITH_BG=0
WITHOUT_BG=0

for file in *.html; do
    TOTAL=$((TOTAL+1))
    if grep -q "img/.*-background\.png" "$file" 2>/dev/null; then
        WITH_BG=$((WITH_BG+1))
    else
        WITHOUT_BG=$((WITHOUT_BG+1))
        echo "❌ $file"
    fi
done

echo ""
echo "총 페이지: $TOTAL"
echo "배경 적용: $WITH_BG"
echo "배경 미적용: $WITHOUT_BG"
