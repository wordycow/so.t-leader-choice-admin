#!/usr/bin/env python3
"""급락 포착 빠른 테스트 (TOP 30 코인만)"""

import pyupbit
import pandas as pd

def calculate_rsi(df, period=14):
    """RSI 계산"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if len(rsi) > 0 else 50

def detect_dip_signal(ticker):
    """급락 신호 감지"""
    try:
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=15)
        if df_1m is None or len(df_1m) < 10:
            return None
        
        price_before = df_1m['close'].iloc[-2]
        price_now = df_1m['close'].iloc[-1]
        change_pct = ((price_now - price_before) / price_before) * 100
        
        vol_avg = df_1m['volume'].iloc[-10:-1].mean()
        vol_now = df_1m['volume'].iloc[-1]
        vol_spike = (vol_now / vol_avg) if vol_avg > 0 else 1.0
        
        rsi = calculate_rsi(df_1m, period=14)
        
        signals = []
        score = 0
        
        # 급락 체크 (-1.5% 이상, 더 민감하게)
        if change_pct <= -1.5:
            signals.append(f"급락 {change_pct:.2f}%")
            score += 3
        
        # 거래량 폭증 (2배 이상)
        if vol_spike >= 2.0:
            signals.append(f"거래량 {vol_spike:.1f}배")
            score += 2
        
        # RSI 과매도
        if rsi <= 35:
            signals.append(f"RSI {rsi:.1f}")
            score += 2
        
        if score >= 4:  # 4점 이상
            return {
                'change_pct': change_pct,
                'vol_spike': vol_spike,
                'rsi': rsi,
                'signals': signals,
                'score': score
            }
        
        return None
    except:
        return None

print("=" * 80)
print("📉 급락 포착 빠른 테스트 (TOP 30 코인)")
print("=" * 80)

# TOP 30 코인
tickers = [
    'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
    'KRW-ADA', 'KRW-AVAX', 'KRW-DOT', 'KRW-MATIC', 'KRW-LINK',
    'KRW-ATOM', 'KRW-ETC', 'KRW-BCH', 'KRW-LTC', 'KRW-NEAR',
    'KRW-HBAR', 'KRW-APT', 'KRW-ARB', 'KRW-OP', 'KRW-SUI',
    'KRW-SEI', 'KRW-STRK', 'KRW-TIA', 'KRW-INJ', 'KRW-FET',
    'KRW-IMX', 'KRW-SAND', 'KRW-AXS', 'KRW-MANA', 'KRW-ENJ'
]

print(f"\n💰 {len(tickers)}개 코인 개별 조회...")
dip_count = 0
surge_count = 0

for ticker in tickers:
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            continue
        
        # 급등/급락 체크
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2)
        if df is None or len(df) < 2:
            continue
        
        change = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
        
        # 급락 신호 감지
        dip_signal = detect_dip_signal(ticker)
        
        if dip_signal:
            print(f"\n🔥 [급락 매수 기회] {ticker}: {current_price:,.0f}원")
            print(f"   {change:.2f}% | RSI {dip_signal['rsi']:.1f} | {', '.join(dip_signal['signals'])}")
            dip_count += 1
        elif change >= 1.0:
            print(f"  🚀 [급등] {ticker}: +{change:.2f}%")
            surge_count += 1
        else:
            print(f"  {ticker}: {change:+.2f}%", end="\r")
            
    except Exception as e:
        continue

print(f"\n\n✅ 테스트 완료:")
print(f"   📉 급락 매수 기회: {dip_count}개")
print(f"   🚀 급등 신호: {surge_count}개")
print("=" * 80)
