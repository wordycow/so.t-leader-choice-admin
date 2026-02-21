#!/usr/bin/env python3
"""
패턴 인식 백테스팅 시스템
과거 데이터로 5가지 패턴의 정확도를 검증
"""

import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time

# 5가지 전략 정의
STRATEGIES = {
    'surge_hunter': {
        'name': '급등 포착',
        'description': '단기 급등 코인 매수'
    },
    'dip_hunter': {
        'name': '급락 반등',
        'description': '급락 후 반등 포착'
    },
    'box_trader': {
        'name': '박스권 매매',
        'description': 'RSI 과매도 구간 매수'
    },
    'trend_follower': {
        'name': '추세 추종',
        'description': '상승 추세 추종'
    },
    'volume_hunter': {
        'name': '거래량 급증',
        'description': '거래량 폭등 감지'
    }
}

def calculate_rsi(df, period=14):
    """RSI 계산"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def detect_surge_hunter(df, row_idx):
    """급등 포착 패턴"""
    if row_idx < 5:
        return False, {}
    
    current = df.iloc[row_idx]
    prev_5 = df.iloc[row_idx-5:row_idx]
    
    # 5분 내 5% 이상 급등
    price_change = (current['close'] - prev_5['close'].iloc[0]) / prev_5['close'].iloc[0] * 100
    
    if price_change >= 5:
        return True, {
            'pattern': 'surge',
            'change': price_change,
            'score': price_change / 5
        }
    
    return False, {}

def detect_dip_hunter(df, row_idx):
    """급락 반등 패턴"""
    if row_idx < 10:
        return False, {}
    
    current = df.iloc[row_idx]
    recent = df.iloc[row_idx-10:row_idx]
    
    # 최근 급락 후 반등
    max_price = recent['high'].max()
    min_price = recent['low'].min()
    
    dip_percent = (max_price - min_price) / max_price * 100
    recovery = (current['close'] - min_price) / min_price * 100
    
    if dip_percent >= 5 and recovery >= 2:
        return True, {
            'pattern': 'dip',
            'dip_percent': dip_percent,
            'recovery': recovery,
            'score': recovery / 2
        }
    
    return False, {}

def detect_box_trader(df, row_idx):
    """박스권 RSI 과매도 패턴"""
    if row_idx < 20:
        return False, {}
    
    df_temp = df.iloc[:row_idx+1].copy()
    df_temp['rsi'] = calculate_rsi(df_temp)
    
    current_rsi = df_temp['rsi'].iloc[-1]
    
    if pd.isna(current_rsi):
        return False, {}
    
    # RSI < 30 과매도
    if current_rsi < 30:
        return True, {
            'pattern': 'box',
            'rsi': current_rsi,
            'score': (30 - current_rsi) / 10
        }
    
    return False, {}

def detect_trend_follower(df, row_idx):
    """추세 추종 패턴"""
    if row_idx < 20:
        return False, {}
    
    recent = df.iloc[row_idx-20:row_idx]
    current = df.iloc[row_idx]
    
    # 20일 이동평균
    ma20 = recent['close'].mean()
    
    # 현재가가 이동평균 위 + 상승 추세
    if current['close'] > ma20:
        trend_strength = (current['close'] - ma20) / ma20 * 100
        
        if trend_strength > 1:
            return True, {
                'pattern': 'trend',
                'strength': trend_strength,
                'score': min(trend_strength / 2, 3)
            }
    
    return False, {}

def detect_volume_hunter(df, row_idx):
    """거래량 급증 패턴"""
    if row_idx < 10:
        return False, {}
    
    current = df.iloc[row_idx]
    prev_avg = df.iloc[row_idx-10:row_idx]['volume'].mean()
    
    if prev_avg == 0:
        return False, {}
    
    volume_change = (current['volume'] - prev_avg) / prev_avg * 100
    
    # 거래량 50% 이상 급증
    if volume_change >= 50:
        return True, {
            'pattern': 'volume',
            'volume_change': volume_change,
            'score': min(volume_change / 50, 3)
        }
    
    return False, {}

def backtest_coin(ticker, days=30):
    """단일 코인 백테스팅"""
    print(f"\n{'='*60}")
    print(f"📊 {ticker} 백테스팅 시작...")
    print(f"{'='*60}")
    
    # 과거 데이터 가져오기
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count=days*24)
        if df is None or len(df) < 100:
            print(f"❌ {ticker} 데이터 부족")
            return None
        
        print(f"✅ {ticker} 데이터 로드: {len(df)}개 캔들")
        
        results = {
            'ticker': ticker,
            'total_candles': len(df),
            'strategies': {}
        }
        
        # 각 전략별 백테스팅
        for strategy_id, strategy_info in STRATEGIES.items():
            print(f"\n🔍 {strategy_info['name']} 패턴 검증 중...")
            
            signals = []
            profits = []
            
            for i in range(20, len(df) - 24):  # 미래 24시간 수익 계산 가능한 범위
                detected = False
                pattern_data = {}
                
                if strategy_id == 'surge_hunter':
                    detected, pattern_data = detect_surge_hunter(df, i)
                elif strategy_id == 'dip_hunter':
                    detected, pattern_data = detect_dip_hunter(df, i)
                elif strategy_id == 'box_trader':
                    detected, pattern_data = detect_box_trader(df, i)
                elif strategy_id == 'trend_follower':
                    detected, pattern_data = detect_trend_follower(df, i)
                elif strategy_id == 'volume_hunter':
                    detected, pattern_data = detect_volume_hunter(df, i)
                
                if detected:
                    buy_price = df.iloc[i]['close']
                    
                    # 24시간 후 수익률 계산
                    future_prices = df.iloc[i+1:i+25]['close']
                    max_price = future_prices.max()
                    
                    # 목표 수익률 3% 도달 여부
                    profit_rate = (max_price - buy_price) / buy_price * 100
                    
                    signals.append({
                        'timestamp': df.index[i],
                        'buy_price': buy_price,
                        'max_price': max_price,
                        'profit_rate': profit_rate,
                        'pattern': pattern_data
                    })
                    
                    profits.append(profit_rate)
            
            if len(signals) > 0:
                winning_trades = len([p for p in profits if p >= 3])
                win_rate = winning_trades / len(signals) * 100
                avg_profit = np.mean(profits)
                
                results['strategies'][strategy_id] = {
                    'name': strategy_info['name'],
                    'total_signals': len(signals),
                    'winning_trades': winning_trades,
                    'win_rate': win_rate,
                    'avg_profit': avg_profit,
                    'max_profit': max(profits),
                    'min_profit': min(profits),
                    'signals': signals[:5]  # 최근 5개만 저장
                }
                
                print(f"  신호 감지: {len(signals)}회")
                print(f"  승률: {win_rate:.1f}%")
                print(f"  평균 수익: {avg_profit:.2f}%")
                print(f"  최대 수익: {max(profits):.2f}%")
            else:
                print(f"  ⚠️ 신호 없음")
                results['strategies'][strategy_id] = {
                    'name': strategy_info['name'],
                    'total_signals': 0
                }
        
        return results
        
    except Exception as e:
        print(f"❌ {ticker} 오류: {e}")
        return None

def run_full_backtest():
    """전체 백테스팅 실행"""
    print("\n" + "="*80)
    print("🚀 패턴 인식 백테스팅 시스템 v1.0")
    print("="*80)
    
    # 주요 코인 리스트
    test_coins = [
        'KRW-BTC',
        'KRW-ETH',
        'KRW-XRP',
        'KRW-SOL',
        'KRW-DOGE',
        'KRW-ADA',
        'KRW-AVAX',
        'KRW-MATIC',
        'KRW-DOT',
        'KRW-SHIB'
    ]
    
    all_results = []
    
    for ticker in test_coins:
        result = backtest_coin(ticker, days=7)  # 최근 7일
        if result:
            all_results.append(result)
        time.sleep(0.5)  # API 레이트 리미트
    
    # 전체 결과 분석
    print("\n" + "="*80)
    print("📊 전체 백테스팅 결과")
    print("="*80)
    
    strategy_summary = {}
    
    for strategy_id in STRATEGIES.keys():
        total_signals = 0
        total_wins = 0
        all_profits = []
        
        for result in all_results:
            if strategy_id in result['strategies']:
                strat = result['strategies'][strategy_id]
                if strat['total_signals'] > 0:
                    total_signals += strat['total_signals']
                    total_wins += strat['winning_trades']
                    
                    # 개별 수익률 수집
                    for signal in strat.get('signals', []):
                        all_profits.append(signal['profit_rate'])
        
        if total_signals > 0:
            overall_win_rate = total_wins / total_signals * 100
            overall_avg_profit = np.mean(all_profits)
            
            strategy_summary[strategy_id] = {
                'name': STRATEGIES[strategy_id]['name'],
                'total_signals': total_signals,
                'win_rate': overall_win_rate,
                'avg_profit': overall_avg_profit
            }
            
            print(f"\n🎯 {STRATEGIES[strategy_id]['name']}")
            print(f"   총 신호: {total_signals}회")
            print(f"   전체 승률: {overall_win_rate:.1f}%")
            print(f"   평균 수익: {overall_avg_profit:.2f}%")
    
    # 결과 저장
    output = {
        'timestamp': datetime.now().isoformat(),
        'test_coins': test_coins,
        'coin_results': all_results,
        'strategy_summary': strategy_summary
    }
    
    with open('backtest_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n✅ 결과 저장: backtest_results.json")
    
    # 최고 성능 전략 추천
    print("\n" + "="*80)
    print("🏆 추천 전략")
    print("="*80)
    
    best_strategy = None
    best_score = 0
    
    for strat_id, summary in strategy_summary.items():
        # 점수 = 승률 * 평균수익
        score = summary['win_rate'] * summary['avg_profit']
        
        if score > best_score:
            best_score = score
            best_strategy = summary
    
    if best_strategy:
        print(f"\n⭐ 최고 성능: {best_strategy['name']}")
        print(f"   승률: {best_strategy['win_rate']:.1f}%")
        print(f"   평균 수익: {best_strategy['avg_profit']:.2f}%")
        print(f"   종합 점수: {best_score:.1f}")

if __name__ == '__main__':
    run_full_backtest()
