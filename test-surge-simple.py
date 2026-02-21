#!/usr/bin/env python3
"""간단한 급등 감지 테스트"""

import pyupbit
from datetime import datetime

def test_surge_detection():
    print("=" * 80)
    print("🚀 급등 감지 간단 테스트")
    print("=" * 80)
    
    # 1. 전체 티커 조회
    print("\n📊 1단계: 전체 KRW 마켓 조회...")
    tickers = pyupbit.get_tickers(fiat="KRW")
    print(f"✅ {len(tickers)}개 코인 발견")
    
    # 2. 모든 코인 현재가 한 번에 조회
    print("\n💰 2단계: 모든 코인 현재가 조회...")
    start_time = datetime.now()
    all_prices = pyupbit.get_current_price(tickers)
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"✅ {len(all_prices)}개 코인 현재가 조회 완료 ({elapsed:.2f}초)")
    
    # 3. 상위 10개 코인만 급등 체크
    print("\n🔍 3단계: 상위 10개 코인 급등 감지...")
    popular_tickers = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
                       'KRW-ADA', 'KRW-AVAX', 'KRW-DOT', 'KRW-MATIC', 'KRW-LINK']
    
    surge_count = 0
    for ticker in popular_tickers:
        try:
            current_price = all_prices.get(ticker)
            if not current_price:
                continue
            
            # 1분봉 2개만 조회
            df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2)
            if df is None or len(df) < 2:
                continue
            
            # 변화율 계산
            price_before = df['close'].iloc[-2]
            price_now = df['close'].iloc[-1]
            change_pct = ((price_now - price_before) / price_before) * 100
            
            # 거래량 변화
            vol_before = df['volume'].iloc[-2]
            vol_now = df['volume'].iloc[-1]
            vol_spike = (vol_now / vol_before) if vol_before > 0 else 1.0
            
            print(f"  {ticker}: {current_price:,.0f}원 | 변동: {change_pct:+.2f}% | 거래량: {vol_spike:.1f}배")
            
            # 급등 조건
            if change_pct >= 0.5 and vol_spike >= 1.5:
                print(f"  🚀 [급등 후보] {ticker}")
                surge_count += 1
            
        except Exception as e:
            print(f"  ❌ {ticker}: {e}")
    
    print(f"\n✅ 테스트 완료: {surge_count}개 급등 후보 발견")
    print("=" * 80)

if __name__ == "__main__":
    test_surge_detection()
