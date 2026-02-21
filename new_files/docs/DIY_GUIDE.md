# 🛠️ 직접 수정 가이드 - 크래딧 절약

## 1. "지아와 대화" 버튼 삭제

**파일**: `templates/dashboard-ultimate-v3-with-emei.html`

**찾아서 삭제할 내용**:
```html
<button>지아와 대화</button>
<!-- 또는 -->
<a>지아와 대화</a>
<!-- 또는 -->
지아
```

**방법**:
```bash
cd /home/user/webapp
grep -n "지아" templates/dashboard-ultimate-v3-with-emei.html
# 나온 줄 번호를 보고 해당 버튼/링크 삭제
```

---

## 2. 거래 내역 UI 추가

**위치**: 전략 성과 카드들 아래

**추가할 코드**: (472f1af 커밋에서 가져옴)
```html
<!-- 거래 내역 -->
<div class="list-section" style="margin-top: 24px;">
  <h3>📋 최근 거래 내역</h3>
  <div id="recentTrades">
    <div class="list-item">
      <div class="item-left">
        <div class="item-title">거래 내역이 없습니다</div>
        <div class="item-subtitle">거래가 실행되면 여기에 표시됩니다</div>
      </div>
    </div>
  </div>
</div>
```

**스타일 추가**:
```css
.list-section {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 24px;
}

.list-item {
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid rgba(255,255,255,0.08);
}

.item-title {
  font-size: 16px;
  color: white;
  font-weight: 600;
  margin-bottom: 4px;
}

.item-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
}
```

---

## 3. JavaScript에서 거래 내역 업데이트

**파일**: `templates/dashboard-ultimate-v3-with-emei.html` (script 섹션)

**updateBotStatus() 함수 안에 추가**:
```javascript
// 거래 내역 업데이트
if (data.recent_trades && data.recent_trades.length > 0) {
  const tradesHTML = data.recent_trades.slice(0, 5).map(trade => {
    const isProfit = trade.profit_rate > 0;
    const profitClass = isProfit ? 'text-green-400' : 'text-red-400';
    const profitIcon = isProfit ? '📈' : '📉';
    
    return `
      <div class="list-item">
        <div class="item-left">
          <div class="item-title">
            ${profitIcon} ${trade.ticker.replace('KRW-', '')} 
            ${trade.type === 'BUY' ? '매수' : '매도'}
          </div>
          <div class="item-subtitle">
            ${trade.reason || ''}
          </div>
        </div>
        <div class="item-right">
          <div class="${profitClass}" style="font-size: 16px; font-weight: 700;">
            ${trade.profit_rate > 0 ? '+' : ''}${trade.profit_rate.toFixed(2)}%
          </div>
          <div style="font-size: 12px; color: rgba(255,255,255,0.5);">
            ${formatNumber(Math.abs(trade.profit))}원
          </div>
        </div>
      </div>
    `;
  }).join('');
  
  document.getElementById('recentTrades').innerHTML = tradesHTML;
}
```

---

## 4. 서버 재시작 없이 반영하는 방법

**Flask debug 모드 활성화**:

`upbit-smart-bot-v8.0-ULTIMATE.py` 파일 맨 끝:
```python
if __name__ == '__main__':
    # debug=True 추가
    app.run(host='0.0.0.0', port=5000, debug=True)
```

이렇게 하면 파일 수정 시 자동 재시작됩니다.

---

## 5. Git 커밋 & 푸시

```bash
cd /home/user/webapp
git add -A
git commit -m "fix: 거래 내역 UI 추가 + 지아 버튼 삭제"
git push origin main
```

---

## 🎯 우선순위

1. **"지아와 대화" 버튼 찾기** (grep으로)
2. **거래 내역 섹션 추가**
3. **JavaScript 업데이트 로직 추가**
4. **테스트**

---

## ❓ 질문/도움 필요 시

- 코드 위치를 모르겠다
- 에러가 난다
- 특정 부분만 도와달라

→ **구체적인 질문**을 해주시면 크래딧 낭비 없이 도와드리겠습니다.

---

**저장 위치**: `/home/user/webapp/DIY_GUIDE.md`
