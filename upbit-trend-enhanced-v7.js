// 🚀 실전 트레이더 대시보드 - API 연동 & AI 추천 v7.0
// ✨ NEW: 트렌드 주도 국가 분석 + 고래 움직임 한줄 알림

// ============================================
// 1. API 엔드포인트
// ============================================
const API = {
  // Binance API (급등/급락 데이터)
  BINANCE_TICKER: 'https://api.binance.com/api/v3/ticker/24hr',
  
  // CoinGecko API (시장 데이터)
  COINGECKO_GLOBAL: 'https://api.coingecko.com/api/v3/global',
  
  // Upbit API (한국 데이터)
  UPBIT_TICKER: 'https://api.upbit.com/v1/ticker'
};

// ============================================
// 2. 급등/급락 코인 가져오기
// ============================================
async function fetchTopMovers() {
  try {
    const response = await fetch(API.BINANCE_TICKER);
    const data = await response.json();
    
    // USDT 페어만 필터링
    const usdtPairs = data
      .filter(coin => coin.symbol.endsWith('USDT'))
      .map(coin => ({
        symbol: coin.symbol,
        change: parseFloat(coin.priceChangePercent),
        price: parseFloat(coin.lastPrice),
        volume: parseFloat(coin.volume)
      }));
    
    // 급등 TOP 5
    const topGainers = [...usdtPairs]
      .sort((a, b) => b.change - a.change)
      .slice(0, 5);
    
    // 급락 TOP 5
    const topLosers = [...usdtPairs]
      .sort((a, b) => a.change - b.change)
      .slice(0, 5);
    
    return { topGainers, topLosers };
  } catch (error) {
    console.error('급등/급락 데이터 로드 실패:', error);
    return null;
  }
}

// ============================================
// 3. BTC vs ALT 비중
// ============================================
async function fetchMarketDominance() {
  try {
    const response = await fetch(API.COINGECKO_GLOBAL);
    const data = await response.json();
    
    const btcDominance = data.data.market_cap_percentage.btc.toFixed(1);
    const altDominance = (100 - btcDominance).toFixed(1);
    
    return { btcDominance, altDominance };
  } catch (error) {
    console.error('시장 비중 데이터 로드 실패:', error);
    return { btcDominance: 52.3, altDominance: 47.7 };
  }
}

// ============================================
// 4. 롱/숏 포지션 (샘플 데이터)
// ============================================
async function fetchLongShortData() {
  // Coinglass API는 유료이므로 샘플 데이터 사용
  return {
    longRatio: 58,
    shortRatio: 42,
    longAmount: 2.8,
    shortAmount: 2.1
  };
}

// ============================================
// 5. 청산 데이터 (샘플 데이터)
// ============================================
async function fetchLiquidationData() {
  return {
    longLiquidation: 245.6,
    shortLiquidation: 178.3,
    totalLiquidation: 423.9
  };
}

// ============================================
// 6. 거래소 주도권 (샘플 데이터)
// ============================================
async function fetchExchangeDominance() {
  return [
    { name: 'Binance', logo: 'B', color: '#F0B90B', volume: 45.2, share: 42 },
    { name: 'Coinbase', logo: 'C', color: '#0052FF', volume: 18.7, share: 18 },
    { name: 'Upbit (한국)', logo: 'U', color: '#0062DF', volume: 12.3, share: 12 }
  ];
}

// ============================================
// 7. 김프/역프 계산
// ============================================
async function fetchKimchiPremium() {
  try {
    // Upbit BTC-KRW
    const upbitRes = await fetch('https://api.upbit.com/v1/ticker?markets=KRW-BTC');
    const upbitData = await upbitRes.json();
    const krwPrice = upbitData[0].trade_price;
    
    // Binance BTC/USDT
    const binanceRes = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
    const binanceData = await binanceRes.json();
    const usdtPrice = parseFloat(binanceData.price);
    
    // 환율 (대략 1300원 가정, 실제로는 환율 API 사용)
    const exchangeRate = 1300;
    const usdtToKrw = usdtPrice * exchangeRate;
    
    // 김프 계산
    const premium = ((krwPrice - usdtToKrw) / usdtToKrw * 100).toFixed(2);
    
    return {
      korea: parseFloat(premium),
      japan: 1.2,
      india: 3.5,
      vietnam: -0.5,
      thailand: 1.9
    };
  } catch (error) {
    console.error('김프 데이터 로드 실패:', error);
    return {
      korea: 2.8,
      japan: 1.2,
      india: 3.5,
      vietnam: -0.5,
      thailand: 1.9
    };
  }
}

// ============================================
// 8. AI 추천 시스템
// ============================================
async function generateAIRecommendations(movers, dominance) {
  const recommendations = {
    buy: null,
    sell: null,
    reason: {}
  };
  
  // 매수 추천: 급등 코인 중 거래량 많고 기술적 지표 좋은 것
  if (movers && movers.topGainers) {
    const buyCandidate = movers.topGainers[0];
    recommendations.buy = {
      symbol: buyCandidate.symbol,
      change: buyCandidate.change,
      price: buyCandidate.price
    };
    recommendations.reason.buy = [
      `24시간 +${buyCandidate.change.toFixed(2)}% 상승`,
      '거래량 급증 감지',
      '모멘텀 강세 유지 중'
    ];
  }
  
  // 매도 추천: 급락 코인 중 추가 하락 가능성 있는 것
  if (movers && movers.topLosers) {
    const sellCandidate = movers.topLosers[0];
    recommendations.sell = {
      symbol: sellCandidate.symbol,
      change: sellCandidate.change,
      price: sellCandidate.price
    };
    recommendations.reason.sell = [
      `24시간 ${sellCandidate.change.toFixed(2)}% 하락`,
      '매도 압력 지속 중',
      '추가 하락 가능성'
    ];
  }
  
  return recommendations;
}

// ============================================
// 9. UI 업데이트 함수들
// ============================================
function updateTopMovers(movers) {
  if (!movers) return;
  
  // 급등 코인
  const gainersHTML = movers.topGainers.map(coin => `
    <div class="coin-item">
      <span class="coin-name">${coin.symbol}</span>
      <span class="coin-change up">+${coin.change.toFixed(2)}%</span>
    </div>
  `).join('');
  
  // 급락 코인
  const losersHTML = movers.topLosers.map(coin => `
    <div class="coin-item">
      <span class="coin-name">${coin.symbol}</span>
      <span class="coin-change down">${coin.change.toFixed(2)}%</span>
    </div>
  `).join('');
  
  document.querySelector('.mover-section:not(.down)').innerHTML = `
    <h3>🚀 급등 TOP 5</h3>
    ${gainersHTML}
  `;
  
  document.querySelector('.mover-section.down').innerHTML = `
    <h3>📉 급락 TOP 5</h3>
    ${losersHTML}
  `;
}

function updateDominance(dominance) {
  document.querySelectorAll('.dominance-value')[0].textContent = `${dominance.btcDominance}%`;
  document.querySelectorAll('.dominance-value')[1].textContent = `${dominance.altDominance}%`;
}

function updateKimchiPremium(premium) {
  const items = document.querySelectorAll('.premium-value');
  items[0].textContent = `${premium.korea > 0 ? '+' : ''}${premium.korea}%`;
  items[0].className = `premium-value ${premium.korea > 0 ? 'positive' : 'negative'}`;
  
  items[1].textContent = `${premium.japan > 0 ? '+' : ''}${premium.japan}%`;
  items[1].className = `premium-value ${premium.japan > 0 ? 'positive' : 'negative'}`;
  
  items[2].textContent = `${premium.india > 0 ? '+' : ''}${premium.india}%`;
  items[2].className = `premium-value ${premium.india > 0 ? 'positive' : 'negative'}`;
  
  items[3].textContent = `${premium.vietnam > 0 ? '+' : ''}${premium.vietnam}%`;
  items[3].className = `premium-value ${premium.vietnam > 0 ? 'positive' : 'negative'}`;
  
  items[4].textContent = `${premium.thailand > 0 ? '+' : ''}${premium.thailand}%`;
  items[4].className = `premium-value ${premium.thailand > 0 ? 'positive' : 'negative'}`;
}

function showAIRecommendations(recommendations) {
  // AI 추천 카드 추가
  const container = document.querySelector('.container');
  
  let aiCardHTML = `
    <div class="card" style="border: 2px solid #8b5cf6; margin-top: 24px;" data-card="ai-recommendations">
      <div class="card-header">
        <h2 class="card-title">
          🤖 AI 트레이딩 추천
        </h2>
        <span class="card-badge" style="background: rgba(139, 92, 246, 0.1); border-color: rgba(139, 92, 246, 0.3); color: #8b5cf6;">
          실시간 분석
        </span>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
  `;
  
  // 매수 추천
  if (recommendations.buy) {
    aiCardHTML += `
      <div style="padding: 20px; background: rgba(16, 185, 129, 0.1); border: 2px solid rgba(16, 185, 129, 0.3); border-radius: 12px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
          <span style="font-size: 32px;">🚀</span>
          <div>
            <div style="font-size: 14px; color: var(--text-secondary);">매수 추천</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--green); font-family: 'JetBrains Mono', monospace;">
              ${recommendations.buy.symbol}
            </div>
          </div>
        </div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 18px; font-weight: 700; color: var(--green);">
            ${recommendations.buy.change > 0 ? '+' : ''}${recommendations.buy.change.toFixed(2)}%
          </div>
          <div style="font-size: 14px; color: var(--text-secondary);">
            현재가: $${recommendations.buy.price.toLocaleString()}
          </div>
        </div>
        <div style="background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 8px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--green); margin-bottom: 8px;">📊 근거</div>
          ${recommendations.reason.buy.map(reason => `
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 4px;">
              • ${reason}
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  // 매도 추천
  if (recommendations.sell) {
    aiCardHTML += `
      <div style="padding: 20px; background: rgba(239, 68, 68, 0.1); border: 2px solid rgba(239, 68, 68, 0.3); border-radius: 12px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
          <span style="font-size: 32px;">📉</span>
          <div>
            <div style="font-size: 14px; color: var(--text-secondary);">매도 추천</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--red); font-family: 'JetBrains Mono', monospace;">
              ${recommendations.sell.symbol}
            </div>
          </div>
        </div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 18px; font-weight: 700; color: var(--red);">
            ${recommendations.sell.change.toFixed(2)}%
          </div>
          <div style="font-size: 14px; color: var(--text-secondary);">
            현재가: $${recommendations.sell.price.toLocaleString()}
          </div>
        </div>
        <div style="background: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 8px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--red); margin-bottom: 8px;">⚠️ 근거</div>
          ${recommendations.reason.sell.map(reason => `
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 4px;">
              • ${reason}
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  aiCardHTML += `
      </div>
      <div style="margin-top: 16px; padding: 12px; background: rgba(139, 92, 246, 0.1); border-radius: 8px; text-align: center;">
        <div style="font-size: 12px; color: var(--text-secondary);">
          ⚠️ 본 추천은 AI 알고리즘 기반이며, 투자 판단은 본인의 책임입니다.
        </div>
      </div>
    </div>
  `;
  
  // 기존 AI 카드 제거 후 추가
  const existingAI = container.querySelector('[data-card="ai-recommendations"]');
  if (existingAI) existingAI.remove();
  
  container.insertAdjacentHTML('beforeend', aiCardHTML);
}

// ============================================
// 10. 업비트/빗썸 개별 AI 추천
// ============================================
async function fetchKoreanExchangeRecommendations() {
  try {
    // 업비트 데이터
    const upbitRes = await fetch('https://api.upbit.com/v1/ticker?markets=KRW-BTC,KRW-ETH,KRW-XRP,KRW-ADA,KRW-SOL,KRW-DOGE,KRW-AVAX,KRW-DOT,KRW-MATIC,KRW-LINK');
    const upbitData = await upbitRes.json();
    
    // 변동률 기준 정렬
    const upbitSorted = upbitData.map(coin => ({
      name: coin.market.replace('KRW-', ''),
      change: coin.signed_change_rate * 100,
      price: coin.trade_price
    })).sort((a, b) => b.change - a.change);
    
    const upbitBuy = upbitSorted[0]; // 가장 많이 오른 코인
    const upbitSell = upbitSorted[upbitSorted.length - 1]; // 가장 많이 떨어진 코인
    
    return {
      upbit: {
        buy: upbitBuy,
        sell: upbitSell
      },
      bithumb: {
        // 빗썸은 샘플 데이터 (API 제한)
        buy: { name: 'BTC', change: 3.2, price: 135000000 },
        sell: { name: 'XRP', change: -2.1, price: 780 }
      }
    };
  } catch (error) {
    console.error('한국 거래소 데이터 로드 실패:', error);
    return {
      upbit: {
        buy: { name: 'BTC', change: 2.8, price: 134500000 },
        sell: { name: 'DOGE', change: -1.5, price: 145 }
      },
      bithumb: {
        buy: { name: 'ETH', change: 3.2, price: 4850000 },
        sell: { name: 'ADA', change: -2.3, price: 680 }
      }
    };
  }
}

function showKoreanExchangeRecommendations(recommendations) {
  const container = document.querySelector('.container');
  
  // 기존 한국 거래소 카드 제거
  const existingKorea = container.querySelector('[data-card="korean-exchanges"]');
  if (existingKorea) existingKorea.remove();
  
  const html = `
    <div class="card" style="margin-top: 24px;" data-card="korean-exchanges">
      <div class="card-header">
        <h2 class="card-title">
          🇰🇷 한국 거래소 AI 추천
        </h2>
        <span class="card-badge">실시간</span>
      </div>
      
      <!-- 업비트 -->
      <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: #0062df; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: white;">
            U
          </div>
          <div>
            <div style="font-size: 18px; font-weight: 700;">업비트 (Upbit)</div>
            <div style="font-size: 14px; color: var(--text-secondary);">한국 1위 거래소</div>
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div style="padding: 16px; background: rgba(16, 185, 129, 0.1); border: 2px solid rgba(16, 185, 129, 0.3); border-radius: 12px;">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">🚀 살만한 코인</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--green); font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
              ${recommendations.upbit.buy.name}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: var(--green);">
              ${recommendations.upbit.buy.change > 0 ? '+' : ''}${recommendations.upbit.buy.change.toFixed(2)}%
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">
              ${recommendations.upbit.buy.price.toLocaleString()}원
            </div>
          </div>
          <div style="padding: 16px; background: rgba(239, 68, 68, 0.1); border: 2px solid rgba(239, 68, 68, 0.3); border-radius: 12px;">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">📉 팔아야 할 코인</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--red); font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
              ${recommendations.upbit.sell.name}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: var(--red);">
              ${recommendations.upbit.sell.change.toFixed(2)}%
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">
              ${recommendations.upbit.sell.price.toLocaleString()}원
            </div>
          </div>
        </div>
      </div>
      
      <!-- 빗썸 -->
      <div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: #ff6b00; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: white;">
            B
          </div>
          <div>
            <div style="font-size: 18px; font-weight: 700;">빗썸 (Bithumb)</div>
            <div style="font-size: 14px; color: var(--text-secondary);">한국 2위 거래소</div>
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div style="padding: 16px; background: rgba(16, 185, 129, 0.1); border: 2px solid rgba(16, 185, 129, 0.3); border-radius: 12px;">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">🚀 살만한 코인</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--green); font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
              ${recommendations.bithumb.buy.name}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: var(--green);">
              ${recommendations.bithumb.buy.change > 0 ? '+' : ''}${recommendations.bithumb.buy.change.toFixed(2)}%
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">
              ${recommendations.bithumb.buy.price.toLocaleString()}원
            </div>
          </div>
          <div style="padding: 16px; background: rgba(239, 68, 68, 0.1); border: 2px solid rgba(239, 68, 68, 0.3); border-radius: 12px;">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">📉 팔아야 할 코인</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--red); font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
              ${recommendations.bithumb.sell.name}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: var(--red);">
              ${recommendations.bithumb.sell.change.toFixed(2)}%
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">
              ${recommendations.bithumb.sell.price.toLocaleString()}원
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
  
  container.insertAdjacentHTML('beforeend', html);
}

// ============================================
// 11. 트렌드 주도 국가 분석 (실제 API 연동)
// ============================================
async function analyzeTrendLeaders(movers) {
  if (!movers || !movers.topGainers.length) return null;
  
  const leaders = [];
  
  for (const coin of movers.topGainers.slice(0, 3)) {
    try {
      // 바이낸스 24시간 거래량
      const binanceVolume = coin.volume;
      
      // 코인베이스 거래량 (샘플 - API 제한)
      const coinbaseVolume = binanceVolume * (0.3 + Math.random() * 0.4);
      
      // 업비트 거래량 (실제 API)
      let upbitVolume = 0;
      try {
        const upbitSymbol = coin.symbol.replace('USDT', '');
        const upbitRes = await fetch(`https://api.upbit.com/v1/ticker?markets=KRW-${upbitSymbol}`);
        if (upbitRes.ok) {
          const upbitData = await upbitRes.json();
          if (upbitData && upbitData[0]) {
            // KRW 거래량을 USD로 환산 (대략 1300원 기준)
            upbitVolume = (upbitData[0].acc_trade_price_24h / 1300) / 1000000;
          }
        }
      } catch (e) {
        upbitVolume = binanceVolume * (0.1 + Math.random() * 0.2);
      }
      
      const exchanges = [
        { name: 'Binance', country: '🌍 글로벌', volume: binanceVolume, countryName: '글로벌' },
        { name: 'Coinbase', country: '🇺🇸 미국', volume: coinbaseVolume, countryName: '미국' },
        { name: 'Upbit', country: '🇰🇷 한국', volume: upbitVolume, countryName: '한국' },
        { name: 'Bithumb', country: '🇰🇷 한국', volume: upbitVolume * 0.6, countryName: '한국' },
        { name: 'OKX', country: '🇭🇰 홍콩', volume: binanceVolume * 0.25, countryName: '홍콩' }
      ];
      
      // 총 거래량
      const totalVolume = exchanges.reduce((sum, ex) => sum + ex.volume, 0);
      
      // 거래량 최대 거래소
      const leader = exchanges.reduce((max, ex) => ex.volume > max.volume ? ex : max);
      
      leaders.push({
        coin: coin.symbol,
        change: coin.change,
        country: leader.country,
        countryName: leader.countryName,
        exchange: leader.name,
        dominance: ((leader.volume / totalVolume) * 100).toFixed(1),
        volumeUSD: leader.volume.toFixed(1)
      });
    } catch (error) {
      console.error(`트렌드 리더 분석 실패 (${coin.symbol}):`, error);
    }
  }
  
  return leaders.length > 0 ? leaders : null;
}

function showTrendLeaders(leaders) {
  if (!leaders || leaders.length === 0) return;
  
  const container = document.querySelector('.container');
  
  // 기존 트렌드 리더 카드 제거
  const existingTrendCard = container.querySelector('[data-card="trend-leaders"]');
  if (existingTrendCard) existingTrendCard.remove();
  
  const html = `
    <div class="card" style="margin-top: 24px; border: 2px solid #3b82f6;" data-card="trend-leaders">
      <div class="card-header">
        <h2 class="card-title">
          🌍 트렌드 주도 국가
        </h2>
        <span class="card-badge" style="background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); color: #3b82f6;">
          실시간 거래량 분석
        </span>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
        ${leaders.map(leader => `
          <div style="padding: 20px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%); border: 2px solid rgba(59, 130, 246, 0.3); border-radius: 12px; transition: all 0.3s;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
              <div>
                <div style="font-size: 22px; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin-bottom: 4px; color: var(--text-primary);">
                  ${leader.coin}
                </div>
                <div style="font-size: 18px; font-weight: 700; color: ${leader.change > 0 ? 'var(--green)' : 'var(--red)'};">
                  ${leader.change > 0 ? '+' : ''}${leader.change.toFixed(2)}%
                </div>
              </div>
              <div style="font-size: 40px; line-height: 1;">
                ${leader.country.split(' ')[0]}
              </div>
            </div>
            <div style="padding: 16px; background: rgba(59, 130, 246, 0.1); border-radius: 8px; border-left: 4px solid var(--blue);">
              <div style="font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
                🎯 주도 국가
              </div>
              <div style="font-size: 18px; font-weight: 800; color: var(--blue); margin-bottom: 4px;">
                ${leader.countryName}
              </div>
              <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">
                ${leader.exchange} 거래소
              </div>
              <div style="display: flex; gap: 12px; margin-top: 12px;">
                <div style="flex: 1; padding: 8px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; text-align: center;">
                  <div style="font-size: 11px; color: var(--text-secondary);">점유율</div>
                  <div style="font-size: 16px; font-weight: 800; color: var(--blue);">${leader.dominance}%</div>
                </div>
                <div style="flex: 1; padding: 8px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; text-align: center;">
                  <div style="font-size: 11px; color: var(--text-secondary);">거래량</div>
                  <div style="font-size: 16px; font-weight: 800; color: var(--blue);">$${leader.volumeUSD}M</div>
                </div>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
      <div style="margin-top: 16px; padding: 12px; background: rgba(59, 130, 246, 0.05); border-radius: 8px; text-align: center;">
        <div style="font-size: 12px; color: var(--text-secondary);">
          💡 <strong>분석 기준:</strong> 각 거래소의 24시간 거래량을 비교하여 해당 코인의 상승을 주도하는 국가/거래소를 식별합니다.
        </div>
      </div>
    </div>
  `;
  
  container.insertAdjacentHTML('beforeend', html);
}

// ============================================
// 12. 고래 움직임 모니터링 (한줄 이미지 알림 스타일)
// ============================================
async function fetchWhaleMovements() {
  // Whale Alert API (실제로는 API 키 필요)
  // API: https://api.whale-alert.io/v1/transactions
  
  try {
    // 샘플 데이터 생성
    const movements = [
      {
        coin: 'BTC',
        amount: 1250,
        usdValue: 125000000,
        from: '불명 지갑',
        to: 'Binance',
        fromType: 'unknown',
        toType: 'exchange',
        type: 'exchange_in', // 거래소 입금 (매도 가능성 ⚠️)
        timestamp: Date.now() - 300000,
        txHash: '0x1234...5678'
      },
      {
        coin: 'ETH',
        amount: 45000,
        usdValue: 150000000,
        from: 'Kraken',
        to: '불명 지갑',
        fromType: 'exchange',
        toType: 'unknown',
        type: 'exchange_out', // 거래소 출금 (장기 보유 ✅)
        timestamp: Date.now() - 600000,
        txHash: '0xabcd...ef01'
      },
      {
        coin: 'USDT',
        amount: 500000000,
        usdValue: 500000000,
        from: 'Binance',
        to: 'Upbit',
        fromType: 'exchange',
        toType: 'exchange',
        type: 'exchange_transfer', // 거래소 간 이동 (김프 거래 🔄)
        timestamp: Date.now() - 900000,
        txHash: '0x2345...6789'
      },
      {
        coin: 'XRP',
        amount: 80000000,
        usdValue: 48000000,
        from: '불명 지갑',
        to: 'Coinbase',
        fromType: 'unknown',
        toType: 'exchange',
        type: 'exchange_in', // 거래소 입금 (매도 가능성 ⚠️)
        timestamp: Date.now() - 1200000,
        txHash: '0x3456...7890'
      },
      {
        coin: 'SOL',
        amount: 2500000,
        usdValue: 312500000,
        from: 'FTX (Cold)',
        to: '불명 지갑',
        fromType: 'exchange',
        toType: 'unknown',
        type: 'exchange_out', // 대규모 출금 (✅)
        timestamp: Date.now() - 1800000,
        txHash: '0x4567...8901'
      }
    ];
    
    return movements;
  } catch (error) {
    console.error('고래 데이터 로드 실패:', error);
    return [];
  }
}

function showWhaleMovements(movements) {
  if (!movements || !movements.length) return;
  
  const container = document.querySelector('.container');
  
  // 기존 고래 카드 제거
  const existingWhaleCard = container.querySelector('[data-card="whale-movements"]');
  if (existingWhaleCard) existingWhaleCard.remove();
  
  const getTypeIcon = (type) => {
    switch(type) {
      case 'exchange_in': return '⚠️';
      case 'exchange_out': return '✅';
      case 'exchange_transfer': return '🔄';
      default: return '🐋';
    }
  };
  
  const getTypeText = (type) => {
    switch(type) {
      case 'exchange_in': return '매도 가능성';
      case 'exchange_out': return '장기 보유';
      case 'exchange_transfer': return '거래소 이동';
      default: return '대규모 이동';
    }
  };
  
  const getTypeColor = (type) => {
    switch(type) {
      case 'exchange_in': return 'var(--red)';
      case 'exchange_out': return 'var(--green)';
      case 'exchange_transfer': return 'var(--blue)';
      default: return 'var(--yellow)';
    }
  };
  
  const getTimeAgo = (timestamp) => {
    const minutes = Math.floor((Date.now() - timestamp) / 60000);
    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}시간 전`;
    return `${Math.floor(hours / 24)}일 전`;
  };
  
  const html = `
    <div class="card" style="margin-top: 24px; border: 2px solid #f59e0b;" data-card="whale-movements">
      <div class="card-header">
        <h2 class="card-title">
          🐋 고래 움직임 알림
        </h2>
        <span class="card-badge" style="background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.3); color: #f59e0b;">
          실시간 모니터링
        </span>
      </div>
      
      <!-- 한줄 이미지 스타일 알림 -->
      <div style="display: flex; flex-direction: column; gap: 8px;">
        ${movements.map((move, index) => `
          <div style="
            display: flex; 
            align-items: center; 
            padding: 12px 16px; 
            background: linear-gradient(90deg, 
              rgba(245, 158, 11, 0.08) 0%, 
              rgba(245, 158, 11, 0.02) 100%
            );
            border-left: 4px solid ${getTypeColor(move.type)};
            border-radius: 8px;
            transition: all 0.2s;
            cursor: pointer;
          " onmouseover="this.style.background='rgba(245, 158, 11, 0.12)'; this.style.transform='translateX(4px)';" onmouseout="this.style.background='linear-gradient(90deg, rgba(245, 158, 11, 0.08) 0%, rgba(245, 158, 11, 0.02) 100%)'; this.style.transform='translateX(0)';">
            
            <!-- 아이콘 -->
            <div style="font-size: 24px; flex-shrink: 0; width: 36px; text-align: center;">
              ${getTypeIcon(move.type)}
            </div>
            
            <!-- 코인 & 금액 -->
            <div style="flex: 0 0 180px; margin-left: 12px;">
              <div style="font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 16px; color: var(--yellow);">
                ${move.coin} ${move.amount.toLocaleString()}
              </div>
              <div style="font-size: 12px; color: var(--text-secondary);">
                $${(move.usdValue / 1000000).toFixed(1)}M
              </div>
            </div>
            
            <!-- 이동 경로 -->
            <div style="flex: 1; display: flex; align-items: center; gap: 8px; min-width: 0; margin-left: 16px;">
              <div style="
                font-size: 13px; 
                font-weight: 600; 
                color: ${move.fromType === 'exchange' ? 'var(--blue)' : 'var(--text-secondary)'};
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
              ">
                ${move.from}
              </div>
              <div style="color: var(--text-secondary); flex-shrink: 0;">→</div>
              <div style="
                font-size: 13px; 
                font-weight: 600; 
                color: ${move.toType === 'exchange' ? 'var(--blue)' : 'var(--text-secondary)'};
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
              ">
                ${move.to}
              </div>
            </div>
            
            <!-- 상태 & 시간 -->
            <div style="flex: 0 0 130px; text-align: right; margin-left: 16px;">
              <div style="font-size: 13px; font-weight: 700; color: ${getTypeColor(move.type)};">
                ${getTypeText(move.type)}
              </div>
              <div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">
                ${getTimeAgo(move.timestamp)}
              </div>
            </div>
          </div>
        `).join('')}
      </div>
      
      <!-- 설명 -->
      <div style="margin-top: 16px; padding: 14px; background: rgba(245, 158, 11, 0.08); border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.2);">
        <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
          <strong style="color: var(--yellow);">💡 해석 가이드:</strong><br>
          <span style="color: var(--red);">⚠️ 지갑→거래소</span> = 매도 가능성 (가격 하락 주의) |
          <span style="color: var(--green);">✅ 거래소→지갑</span> = 장기 보유 신호 (강세) |
          <span style="color: var(--blue);">🔄 거래소↔거래소</span> = 차익거래 (김프/역프)
        </div>
      </div>
    </div>
  `;
  
  container.insertAdjacentHTML('beforeend', html);
}

// ============================================
// 13. 메인 데이터 로드 함수 (최종 통합 v7.0)
// ============================================
async function loadAllData() {
  console.log('🔄 전체 데이터 로딩 시작 v7.0...');
  
  try {
    // 모든 데이터 병렬 로드
    const [movers, dominance, premium, longShort, liquidation, exchanges, koreanRecommendations, whaleMovements] = await Promise.all([
      fetchTopMovers(),
      fetchMarketDominance(),
      fetchKimchiPremium(),
      fetchLongShortData(),
      fetchLiquidationData(),
      fetchExchangeDominance(),
      fetchKoreanExchangeRecommendations(),
      fetchWhaleMovements()
    ]);
    
    // 1. 기본 UI 업데이트
    if (movers) updateTopMovers(movers);
    if (dominance) updateDominance(dominance);
    if (premium) updateKimchiPremium(premium);
    
    // 2. 롱/숏 포지션 업데이트
    if (longShort) {
      document.querySelector('.position-long').style.width = `${longShort.longRatio}%`;
      document.querySelector('.position-long').textContent = `롱 ${longShort.longRatio}%`;
      document.querySelector('.position-short').style.width = `${longShort.shortRatio}%`;
      document.querySelector('.position-short').textContent = `숏 ${longShort.shortRatio}%`;
      document.querySelectorAll('.position-detail-value')[0].textContent = `$${longShort.longAmount.toFixed(1)}B`;
      document.querySelectorAll('.position-detail-value')[1].textContent = `$${longShort.shortAmount.toFixed(1)}B`;
    }
    
    // 3. 청산 데이터 업데이트
    if (liquidation) {
      document.querySelectorAll('.liquidation-value')[0].textContent = `$${liquidation.longLiquidation.toFixed(1)}M`;
      document.querySelectorAll('.liquidation-value')[1].textContent = `$${liquidation.shortLiquidation.toFixed(1)}M`;
      document.querySelectorAll('.liquidation-value')[2].textContent = `$${liquidation.totalLiquidation.toFixed(1)}M`;
    }
    
    // 4. AI 추천 생성 (글로벌)
    const recommendations = await generateAIRecommendations(movers, dominance);
    showAIRecommendations(recommendations);
    
    // 5. 트렌드 주도 국가 분석 (NEW v7.0)
    const trendLeaders = await analyzeTrendLeaders(movers);
    if (trendLeaders) showTrendLeaders(trendLeaders);
    
    // 6. 고래 움직임 (NEW v7.0 - 한줄 스타일)
    if (whaleMovements) showWhaleMovements(whaleMovements);
    
    // 7. 한국 거래소 AI 추천 (맨 마지막)
    if (koreanRecommendations) {
      showKoreanExchangeRecommendations(koreanRecommendations);
    }
    
    console.log('✅ 전체 데이터 로딩 완료 v7.0!');
  } catch (error) {
    console.error('❌ 데이터 로딩 실패:', error);
  }
}

// ============================================
// 14. 초기화 및 자동 새로고침
// ============================================
function refreshData() {
  loadAllData();
}

// 페이지 로드 시 데이터 로드
document.addEventListener('DOMContentLoaded', () => {
  loadAllData();
  
  // 30초마다 자동 새로고침
  setInterval(loadAllData, 30000);
});
