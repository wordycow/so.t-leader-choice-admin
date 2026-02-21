#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실전 모드 상황 파악 및 복구 시스템
API 키 입력 시 현재 보유 코인 분석 + 손실 시 복구 전략
"""

import pyupbit
from datetime import datetime

# 업비트 수수료
UPBIT_FEE_RATE = 0.0005  # 0.05%

def analyze_current_holdings(upbit):
    """
    API 키로 현재 보유 상황 파악
    
    Returns:
        dict: {
            'krw_balance': 현금 잔고,
            'holdings': [보유 코인 리스트],
            'total_value': 총 자산,
            'analysis': 분석 결과
        }
    """
    try:
        # KRW 잔고 조회
        krw_balance = upbit.get_balance('KRW')
        
        # 모든 보유 코인 조회
        balances = upbit.get_balances()
        
        holdings = []
        total_holdings_value = 0
        
        for balance in balances:
            currency = balance['currency']
            
            # KRW는 제외
            if currency == 'KRW':
                continue
            
            ticker = f'KRW-{currency}'
            amount = float(balance['balance'])
            locked = float(balance['locked'])  # 주문 중인 수량
            avg_buy_price = float(balance['avg_buy_price'])
            
            # 현재가 조회
            current_price = pyupbit.get_current_price(ticker)
            if not current_price:
                current_price = avg_buy_price
            
            # 평가 금액
            total_amount = amount + locked
            current_value = total_amount * current_price
            invested_value = total_amount * avg_buy_price
            
            # 평가 손익
            profit = current_value - invested_value
            profit_rate = (profit / invested_value) * 100 if invested_value > 0 else 0
            
            holdings.append({
                'ticker': ticker,
                'coin_name': currency,
                'amount': total_amount,
                'locked': locked,
                'avg_buy_price': avg_buy_price,
                'current_price': current_price,
                'invested_value': invested_value,
                'current_value': current_value,
                'profit': profit,
                'profit_rate': profit_rate
            })
            
            total_holdings_value += current_value
        
        # 총 자산
        total_value = krw_balance + total_holdings_value
        
        # 분석
        losing_coins = [h for h in holdings if h['profit'] < 0]
        winning_coins = [h for h in holdings if h['profit'] >= 0]
        
        total_profit = sum(h['profit'] for h in holdings)
        
        analysis = {
            'total_coins': len(holdings),
            'losing_coins': len(losing_coins),
            'winning_coins': len(winning_coins),
            'total_profit': total_profit,
            'needs_recovery': total_profit < 0,
            'recovery_priority': sorted(losing_coins, key=lambda x: x['profit'])  # 손실 큰 순
        }
        
        return {
            'krw_balance': krw_balance,
            'holdings': holdings,
            'total_holdings_value': total_holdings_value,
            'total_value': total_value,
            'analysis': analysis
        }
    
    except Exception as e:
        return {'error': str(e)}


def execute_partial_sell(upbit, ticker, amount, sell_percentage=0.1):
    """
    보유 코인의 일부 매도 (10% 등)
    
    Args:
        upbit: Upbit 객체
        ticker: 코인 티커
        amount: 보유 수량
        sell_percentage: 매도 비율 (기본 10%)
    
    Returns:
        dict: 매도 결과
    """
    try:
        sell_amount = amount * sell_percentage
        
        # 업비트 최소 주문 금액 (5,000원)
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return {'success': False, 'message': '가격 조회 실패'}
        
        sell_value = sell_amount * current_price
        if sell_value < 5000:
            return {'success': False, 'message': f'최소 주문 금액 미달: {sell_value:,.0f}원 < 5,000원'}
        
        # 매도 주문 (시장가)
        order = upbit.sell_market_order(ticker, sell_amount)
        
        if order:
            # 수수료 계산
            fee = sell_value * UPBIT_FEE_RATE
            net_proceeds = sell_value - fee  # 실제 받는 금액
            
            return {
                'success': True,
                'order_id': order.get('uuid'),
                'ticker': ticker,
                'amount': sell_amount,
                'price': current_price,
                'gross_value': sell_value,
                'fee': fee,
                'net_proceeds': net_proceeds,
                'message': f'{ticker.replace("KRW-", "")} {sell_amount:.4f}개 매도 완료 (수수료: {fee:,.0f}원)'
            }
        else:
            return {'success': False, 'message': '주문 실패'}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}


def create_recovery_plan(analysis_result):
    """
    복구 계획 수립
    
    Args:
        analysis_result: analyze_current_holdings() 결과
    
    Returns:
        dict: 복구 계획
    """
    holdings = analysis_result['holdings']
    analysis = analysis_result['analysis']
    
    if not analysis['needs_recovery']:
        return {
            'needs_recovery': False,
            'message': '손실 없음 - 복구 불필요'
        }
    
    # 손실 코인 우선순위 (손실 큰 순)
    recovery_priority = analysis['recovery_priority']
    
    plan = {
        'needs_recovery': True,
        'total_loss': abs(analysis['total_profit']),
        'steps': []
    }
    
    # Step 1: 손실 코인 10%씩 매도하여 시드 확보
    for coin in recovery_priority:
        if coin['current_value'] > 5000:  # 최소 주문 금액
            plan['steps'].append({
                'action': 'sell_partial',
                'ticker': coin['ticker'],
                'amount': coin['amount'] * 0.1,
                'percentage': 10,
                'reason': f"손실 {coin['profit_rate']:.2f}% - 시드 확보용 부분 매도"
            })
    
    # Step 2: 이익 코인도 10%씩 매도 (추가 시드 확보)
    winning_coins = [h for h in holdings if h['profit'] >= 0 and h['current_value'] > 5000]
    for coin in winning_coins:
        plan['steps'].append({
            'action': 'sell_partial',
            'ticker': coin['ticker'],
            'amount': coin['amount'] * 0.1,
            'percentage': 10,
            'reason': f"이익 {coin['profit_rate']:.2f}% - 추가 시드 확보"
        })
    
    # Step 3: 확보된 시드로 복구 매매 시작
    plan['steps'].append({
        'action': 'start_recovery_trading',
        'reason': '확보된 시드로 손실 복구 매매 시작'
    })
    
    return plan


def execute_recovery_plan(upbit, recovery_plan):
    """
    복구 계획 실행
    
    Args:
        upbit: Upbit 객체
        recovery_plan: create_recovery_plan() 결과
    
    Returns:
        list: 실행 결과 리스트
    """
    if not recovery_plan['needs_recovery']:
        return [{'message': '복구 불필요'}]
    
    results = []
    
    for step in recovery_plan['steps']:
        if step['action'] == 'sell_partial':
            result = execute_partial_sell(
                upbit,
                step['ticker'],
                step['amount'] / 0.1,  # 전체 수량 복원
                0.1
            )
            result['reason'] = step['reason']
            results.append(result)
            
            # 매도 후 잠시 대기
            import time
            time.sleep(1)
        
        elif step['action'] == 'start_recovery_trading':
            results.append({
                'success': True,
                'action': 'recovery_mode_activated',
                'message': '복구 모드 활성화 - 손실 복구 매매 시작'
            })
    
    return results
