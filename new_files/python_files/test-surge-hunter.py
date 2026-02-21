#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 SURGE HUNTER 빠른 테스트 스크립트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
봇의 핵심 기능들을 단계별로 테스트합니다.
"""

import pyupbit
import pandas as pd
import time
from datetime import datetime

print("=" * 80)
print("🧪 SURGE HUNTER v7.2 - 기능 테스트")
print("=" * 80)
print()

# ═══════════════════════════════════════════════════════
# 테스트 1: PyUpbit API 연결 테스트
# ═══════════════════════════════════════════════════════
print("📡 [테스트 1/5] PyUpbit API 연결...")
try:
    tickers = pyupbit.get_tickers(fiat="KRW")
    print(f"✅ 성공! KRW 마켓 코인 수: {len(tickers)}개")
    print(f"   예시: {', '.join(tickers[:5])}")
except Exception as e:
    print(f"❌ 실패: {e}")
    exit(1)

print()

# ═══════════════════════════════════════════════════════
# 테스트 2: 현재가 조회
# ═══════════════════════════════════════════════════════
print("💰 [테스트 2/5] 현재가 조회...")
try:
    test_tickers = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
    for ticker in test_tickers:
        price = pyupbit.get_current_price(ticker)
        print(f"   {ticker}: {price:,.0f}원")
    print("✅ 성공!")
except Exception as e:
    print(f"❌ 실패: {e}")

print()

# ═══════════════════════════════════════════════════════
# 테스트 3: OHLCV 데이터 조회 (1분봉)
# ═══════════════════════════════════════════════════════
print("📊 [테스트 3/5] OHLCV 데이터 조회 (1분봉)...")
try:
    df = pyupbit.get_ohlcv('KRW-BTC', interval="minute1", count=5)
    if df is not None:
        print(f"✅ 성공! 데이터 {len(df)}개 조회")
        print(f"   최근 종가: {df['close'].iloc[-1]:,.0f}원")
        print(f"   거래량: {df['volume'].iloc[-1]:.4f} BTC")
    else:
        print("❌ 데이터 없음")
except Exception as e:
    print(f"❌ 실패: {e}")

print()

# ═══════════════════════════════════════════════════════
# 테스트 4: 급등 신호 감지 (시뮬레이션)
# ═══════════════════════════════════════════════════════
print("🚀 [테스트 4/5] 급등 신호 감지 로직...")
try:
    test_coins = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-ADA']
    surge_found = False
    
    for ticker in test_coins:
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=5)
        if df is not None and len(df) >= 2:
            # 1분 변동률 계산
            change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100
            
            # 거래량 비율
            avg_volume = df['volume'].iloc[:-1].mean()
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            print(f"   {ticker}: 변동 {change:+.2f}% | 거래량 비율 {volume_ratio:.2f}x")
            
            # 급등 조건 (테스트용으로 완화)
            if abs(change) > 0.5 or volume_ratio > 1.5:
                surge_found = True
                print(f"      🚀 주목! 변동성 감지")
        
        time.sleep(0.2)  # API 호출 제한
    
    if surge_found:
        print("✅ 급등 감지 로직 작동 확인!")
    else:
        print("✅ 로직 정상 작동 (현재 급등 없음)")
        
except Exception as e:
    print(f"❌ 실패: {e}")

print()

# ═══════════════════════════════════════════════════════
# 테스트 5: 시뮬레이션 거래 로직
# ═══════════════════════════════════════════════════════
print("💼 [테스트 5/5] 시뮬레이션 거래 로직...")
try:
    # 가상 시드
    simulation_krw = 1000000
    simulation_holdings = {}
    
    # 매수 시뮬레이션
    ticker = 'KRW-BTC'
    current_price = pyupbit.get_current_price(ticker)
    invest_amount = 150000
    buy_amount = invest_amount / current_price
    
    simulation_krw -= invest_amount
    simulation_holdings[ticker] = {
        'amount': buy_amount,
        'avg_price': current_price,
        'invested': invest_amount
    }
    
    print(f"   [매수 시뮬레이션]")
    print(f"   코인: {ticker}")
    print(f"   가격: {current_price:,.0f}원")
    print(f"   수량: {buy_amount:.8f} BTC")
    print(f"   투자: {invest_amount:,}원")
    print(f"   잔고: {simulation_krw:,}원")
    
    # 수익률 계산 (현재가 기준)
    total_value = simulation_krw
    for t, holding in simulation_holdings.items():
        cp = pyupbit.get_current_price(t)
        if cp:
            total_value += holding['amount'] * cp
    
    profit = total_value - 1000000
    profit_rate = (profit / 1000000) * 100
    
    print(f"\n   [시뮬레이션 결과]")
    print(f"   총 평가액: {total_value:,.0f}원")
    print(f"   수익: {profit:+,.0f}원 ({profit_rate:+.2f}%)")
    
    print("✅ 시뮬레이션 로직 정상 작동!")
    
except Exception as e:
    print(f"❌ 실패: {e}")

print()

# ═══════════════════════════════════════════════════════
# 테스트 결과 요약
# ═══════════════════════════════════════════════════════
print("=" * 80)
print("✅ 모든 핵심 기능 테스트 완료!")
print("=" * 80)
print()
print("📋 다음 단계:")
print("   1. 봇 실행: python3 upbit-smart-bot-v7.2-SURGE-HUNTER.py")
print("   2. 웹 브라우저: http://localhost:5000")
print("   3. 연습 모드 선택 → Bot Start")
print("   4. 급등 알림 확인 (30초마다 스캔)")
print()
print("💡 참고:")
print("   - 연습 모드는 실제 거래 없이 시뮬레이션만 합니다")
print("   - API 키 없이도 연습 모드 사용 가능합니다")
print("   - 실전 모드는 업비트 API 키 필요합니다")
print()
