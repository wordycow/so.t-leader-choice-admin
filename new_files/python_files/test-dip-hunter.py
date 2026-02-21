#!/usr/bin/env python3
"""급락 포착 테스트 (과매도 구간 저점 매수)"""

import pyupbit
import pandas as pd
from datetime import datetime

def calculate_rsi(df, period=14):
    """RSI 계산"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if len(rsi) > 0 else 50

def detect_dip_signal(ticker):
    """급락 신호 감지 (과매도 구간 포착)"""
    try:
        # 1분봉 데이터
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=15)
        if df_1m is None or len(df_1m) < 10:
            return None
        
        # 1분 변동률
        price_before = df_1m['close'].iloc[-2]
        price_now = df_1m['close'].iloc[-1]
        change_pct = ((price_now - price_before) / price_before) * 100
        
        # 거래량 폭증 (공포 매도)
        vol_avg = df_1m['volume'].iloc[-10:-1].mean()
        vol_now = df_1m['volume'].iloc[-1]
        vol_spike = (vol_now / vol_avg) if vol_avg > 0 else 1.0
        
        # RSI (과매도 확인)
        rsi = calculate_rsi(df_1m, period=14)
        
        signals = []
        score = 0
        
        # 조건 1: 급락 (-2.5% 이상)
        if change_pct <= -2.5:
            signals.append(f"1분 급락 {change_pct:.2f}%")
            score += 3
        
        # 조건 2: 거래량 폭증 (3배 이상)
        if vol_spike >= 3.0:
            signals.append(f"거래량 {vol_spike:.1f}배")
            score += 2
        
        # 조건 3: RSI 과매도 (30 이하)
        if rsi <= 30:
            signals.append(f"RSI {rsi:.1f} (과매도)")
            score += 2
        
        # 스코어 5점 이상이면 매수 신호
        if score >= 5:
            return {
                'ticker': ticker,
                'change_pct': change_pct,
                'vol_spike': vol_spike,
                'rsi': rsi,
                'signals': signals,
                'score': score,
                'type': 'DIP'  # 급락 매수
            }
        
        return None
        
    except Exception as e:
        return None

def test_dip_detection():
    print("=" * 80)
    print("📉 급락 포착 테스트 (과매도 저점 매수)")
    print("=" * 80)
    
    # 전체 티커 조회
    print("\n📊 전체 KRW 마켓 조회...")
    tickers = pyupbit.get_tickers(fiat="KRW")
    print(f"✅ {len(tickers)}개 코인 발견")
    
    # 모든 코인 현재가 조회
    print("\n💰 모든 코인 현재가 조회...")
    all_prices = pyupbit.get_current_price(tickers)
    print(f"✅ {len(all_prices)}개 코인 현재가 조회 완료")
    
    # 급락 스캔
    print("\n🔍 급락 신호 스캔 중...")
    dip_candidates = []
    
    for i, ticker in enumerate(tickers):
        try:
            current_price = all_prices.get(ticker)
            if not current_price or current_price < 100 or current_price > 10000000:
                continue
            
            # 급락 감지
            dip_signal = detect_dip_signal(ticker)
            
            if dip_signal:
                dip_signal['current_price'] = current_price
                dip_candidates.append(dip_signal)
                print(f"\n🔥 [급락 포착] {ticker}")
                print(f"   가격: {current_price:,.0f}원")
                print(f"   변동: {dip_signal['change_pct']:.2f}%")
                print(f"   RSI: {dip_signal['rsi']:.1f}")
                print(f"   거래량: {dip_signal['vol_spike']:.1f}배")
                print(f"   신호: {', '.join(dip_signal['signals'])}")
                print(f"   스코어: {dip_signal['score']}점")
            
            if (i + 1) % 50 == 0:
                print(f"  진행: {i+1}/{len(tickers)} 스캔 완료...")
                
        except Exception as e:
            continue
    
    print(f"\n✅ 스캔 완료: {len(dip_candidates)}개 급락 매수 기회 발견!")
    print("=" * 80)
    
    if dip_candidates:
        print("\n💎 TOP 급락 매수 기회:")
        for dip in sorted(dip_candidates, key=lambda x: x['score'], reverse=True)[:5]:
            print(f"  {dip['ticker']}: {dip['change_pct']:.2f}% | RSI {dip['rsi']:.1f} | 스코어 {dip['score']}")

if __name__ == "__main__":
    test_dip_detection()
