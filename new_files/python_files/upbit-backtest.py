#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 업비트 스마트 봇 백테스팅 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 기능:
- 과거 데이터로 마틴게일 전략 검증
- 승률, 손익률, 최대 낙폭 계산
- 여러 코인에 대한 백테스팅
- 결과 리포트 생성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple

# ═══════════════════════════════════════════════════════
# 🎨 터미널 색상
# ═══════════════════════════════════════════════════════
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ═══════════════════════════════════════════════════════
# 💰 마틴게일 설정 (v3.0과 동일)
# ═══════════════════════════════════════════════════════
MARTINGALE_STAGES = {
    1: {'amount': 10000, 'rsi_range': (28, 30), 'drop_percent': 0},
    2: {'amount': 10000, 'rsi_range': (26, 28), 'drop_percent': 3},
    3: {'amount': 10000, 'rsi_range': (24, 26), 'drop_percent': 5},
    4: {'amount': 10000, 'rsi_range': (22, 24), 'drop_percent': 7},
    5: {'amount': 100000, 'rsi_range': (0, 22), 'drop_percent': 10}
}

# ═══════════════════════════════════════════════════════
# 📊 RSI 계산 함수
# ═══════════════════════════════════════════════════════
def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """RSI 지표 계산"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ═══════════════════════════════════════════════════════
# 🔍 매수 신호 판단
# ═══════════════════════════════════════════════════════
def should_buy(rsi: float, current_price: float, avg_price: float, stage: int) -> bool:
    """현재 상황에서 매수해야 하는지 판단"""
    stage_info = MARTINGALE_STAGES[stage]
    
    # RSI 조건 체크
    rsi_min, rsi_max = stage_info['rsi_range']
    if not (rsi_min <= rsi <= rsi_max):
        return False
    
    # 1단계는 무조건 매수
    if stage == 1:
        return True
    
    # 2단계 이상은 하락률 체크
    drop_percent = ((avg_price - current_price) / avg_price) * 100
    return drop_percent >= stage_info['drop_percent']

# ═══════════════════════════════════════════════════════
# 🎯 백테스팅 시뮬레이션
# ═══════════════════════════════════════════════════════
def backtest_coin(ticker: str, days: int = 30) -> Dict:
    """특정 코인에 대한 백테스팅"""
    print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
    print(f"{Colors.BOLD}📊 백테스팅: {ticker}{Colors.END}")
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
    
    # 1. 데이터 가져오기
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count=days*24)
        if df is None or len(df) < 100:
            return {"error": "데이터 부족"}
    except Exception as e:
        return {"error": str(e)}
    
    # 2. RSI 계산
    df['rsi'] = calculate_rsi(df)
    df = df.dropna()
    
    # 3. 거래 시뮬레이션
    positions = []  # 포지션 리스트 [{'stage', 'buy_price', 'amount', 'quantity'}]
    trades = []     # 완료된 거래 리스트
    total_invested = 0
    total_profit = 0
    
    for idx, row in df.iterrows():
        current_price = row['close']
        rsi = row['rsi']
        
        # 현재 포지션 상태
        if len(positions) == 0:
            stage = 1
            avg_price = 0
        else:
            stage = len(positions) + 1
            total_amount = sum(p['amount'] for p in positions)
            weighted_sum = sum(p['buy_price'] * p['amount'] for p in positions)
            avg_price = weighted_sum / total_amount if total_amount > 0 else 0
        
        # 매수 신호 체크 (5단계 초과 방지)
        if stage <= 5 and should_buy(rsi, current_price, avg_price, stage):
            stage_info = MARTINGALE_STAGES[stage]
            buy_amount = stage_info['amount']
            quantity = buy_amount / current_price
            
            positions.append({
                'stage': stage,
                'buy_price': current_price,
                'amount': buy_amount,
                'quantity': quantity,
                'buy_time': idx
            })
            total_invested += buy_amount
        
        # 매도 신호 체크 (포지션이 있고 +2% 이상 수익)
        if len(positions) > 0:
            if current_price >= avg_price * 1.02:  # +2% 수익
                # 전체 포지션 청산
                total_quantity = sum(p['quantity'] for p in positions)
                sell_amount = total_quantity * current_price
                profit = sell_amount - total_invested
                profit_rate = (profit / total_invested) * 100
                
                trades.append({
                    'entry_time': positions[0]['buy_time'],
                    'exit_time': idx,
                    'stages': len(positions),
                    'invested': total_invested,
                    'returned': sell_amount,
                    'profit': profit,
                    'profit_rate': profit_rate
                })
                
                total_profit += profit
                positions = []
                total_invested = 0
    
    # 4. 결과 분석
    if len(trades) == 0:
        return {
            "ticker": ticker,
            "total_trades": 0,
            "win_trades": 0,
            "lose_trades": 0,
            "win_rate": 0,
            "total_profit": 0,
            "profit_rate": 0,
            "avg_profit": 0,
            "max_profit": 0,
            "max_loss": 0
        }
    
    win_trades = [t for t in trades if t['profit'] > 0]
    lose_trades = [t for t in trades if t['profit'] <= 0]
    
    result = {
        "ticker": ticker,
        "total_trades": len(trades),
        "win_trades": len(win_trades),
        "lose_trades": len(lose_trades),
        "win_rate": (len(win_trades) / len(trades)) * 100 if len(trades) > 0 else 0,
        "total_profit": sum(t['profit'] for t in trades),
        "profit_rate": (sum(t['profit'] for t in trades) / sum(t['invested'] for t in trades)) * 100,
        "avg_profit": np.mean([t['profit'] for t in trades]),
        "max_profit": max([t['profit'] for t in trades]),
        "max_loss": min([t['profit'] for t in trades]),
        "trades": trades
    }
    
    return result

# ═══════════════════════════════════════════════════════
# 📈 결과 출력
# ═══════════════════════════════════════════════════════
def print_backtest_result(result: Dict):
    """백테스팅 결과 출력"""
    if "error" in result:
        print(f"{Colors.RED}❌ 에러: {result['error']}{Colors.END}")
        return
    
    ticker = result['ticker']
    total = result['total_trades']
    wins = result['win_trades']
    losses = result['lose_trades']
    win_rate = result['win_rate']
    total_profit = result['total_profit']
    profit_rate = result['profit_rate']
    
    print(f"\n{Colors.BOLD}📊 {ticker} 백테스팅 결과{Colors.END}")
    print(f"{'─'*50}")
    print(f"총 거래 횟수: {total}회")
    print(f"승리: {Colors.GREEN}{wins}회{Colors.END} | 패배: {Colors.RED}{losses}회{Colors.END}")
    
    # 승률 색상
    if win_rate >= 70:
        wr_color = Colors.GREEN
    elif win_rate >= 50:
        wr_color = Colors.YELLOW
    else:
        wr_color = Colors.RED
    
    print(f"승률: {wr_color}{win_rate:.1f}%{Colors.END}")
    
    # 수익률 색상
    if total_profit > 0:
        pf_color = Colors.GREEN
        pf_sign = "+"
    else:
        pf_color = Colors.RED
        pf_sign = ""
    
    print(f"총 수익: {pf_color}{pf_sign}{total_profit:,.0f}원{Colors.END}")
    print(f"수익률: {pf_color}{pf_sign}{profit_rate:.2f}%{Colors.END}")
    print(f"평균 수익: {result['avg_profit']:,.0f}원")
    print(f"최대 수익: {Colors.GREEN}+{result['max_profit']:,.0f}원{Colors.END}")
    print(f"최대 손실: {Colors.RED}{result['max_loss']:,.0f}원{Colors.END}")
    print(f"{'─'*50}")

# ═══════════════════════════════════════════════════════
# 🚀 메인 실행
# ═══════════════════════════════════════════════════════
def main():
    """백테스팅 메인 함수"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}  📊 업비트 스마트 봇 v3.0 백테스팅 시스템  {Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    # 테스트할 코인 리스트
    test_tickers = [
        "KRW-BTC",   # 비트코인
        "KRW-ETH",   # 이더리움
        "KRW-XRP",   # 리플
        "KRW-ADA",   # 에이다
        "KRW-DOGE",  # 도지코인
    ]
    
    days = 30  # 백테스팅 기간
    print(f"백테스팅 기간: 최근 {days}일")
    print(f"테스트 코인: {len(test_tickers)}개\n")
    
    all_results = []
    
    for ticker in test_tickers:
        result = backtest_coin(ticker, days)
        if "error" not in result:
            all_results.append(result)
        print_backtest_result(result)
    
    # 전체 요약
    if len(all_results) > 0:
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}  📊 전체 요약  {Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
        
        total_trades = sum(r['total_trades'] for r in all_results)
        total_wins = sum(r['win_trades'] for r in all_results)
        total_profit = sum(r['total_profit'] for r in all_results)
        avg_win_rate = np.mean([r['win_rate'] for r in all_results])
        
        print(f"총 거래: {total_trades}회")
        print(f"총 승리: {Colors.GREEN}{total_wins}회{Colors.END}")
        print(f"평균 승률: {avg_win_rate:.1f}%")
        
        if total_profit > 0:
            print(f"전체 수익: {Colors.GREEN}+{total_profit:,.0f}원{Colors.END}")
        else:
            print(f"전체 수익: {Colors.RED}{total_profit:,.0f}원{Colors.END}")
        
        # 가장 좋은 코인
        best = max(all_results, key=lambda x: x['profit_rate'])
        print(f"\n🏆 최고 성과: {best['ticker']} ({best['profit_rate']:+.2f}%)")
        
        # 결과 저장
        with open('backtest_results.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 결과 저장: backtest_results.json")

if __name__ == "__main__":
    main()
