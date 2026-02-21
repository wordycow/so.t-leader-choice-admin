#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수익 시 포트폴리오 분산 매수 시스템
사용자가 설정한 4개 코인에 각 1만원씩 분산 투자
"""

import pyupbit
from datetime import datetime

def execute_diversified_buy(user_portfolio, current_krw, mode='practice', upbit=None):
    """
    수익 발생 시 포트폴리오 분산 매수
    
    Args:
        user_portfolio: {'coin_1': 'KRW-BTC', 'coin_2': 'KRW-XRP', ...}
        current_krw: 현재 현금 잔고
        mode: 'practice' or 'live'
        upbit: Upbit 객체 (실전 모드일 때)
    
    Returns:
        list: 매수 결과 목록
    """
    investment_per_coin = user_portfolio.get('investment_per_coin', 10000)
    total_investment = investment_per_coin * 4
    
    # 잔고 부족 체크
    if current_krw < total_investment:
        return {
            'success': False,
            'message': f'잔고 부족: {current_krw:,.0f}원 (필요: {total_investment:,.0f}원)'
        }
    
    results = []
    
    for coin_num in range(1, 5):
        coin_key = f'coin_{coin_num}'
        ticker = user_portfolio.get(coin_key)
        
        if not ticker:
            continue
        
        try:
            # 현재가 조회
            current_price = pyupbit.get_current_price(ticker)
            if not current_price:
                results.append({
                    'ticker': ticker,
                    'success': False,
                    'message': '가격 조회 실패'
                })
                continue
            
            # 매수 수량 계산
            buy_amount = investment_per_coin / current_price
            
            if mode == 'practice':
                # 시뮬레이션 매수
                results.append({
                    'ticker': ticker,
                    'success': True,
                    'amount': buy_amount,
                    'price': current_price,
                    'invested': investment_per_coin,
                    'reason': f'[분산 투자] {ticker.replace("KRW-", "")} - 수익금 재투자 전략\n• 투자금: {investment_per_coin:,}원\n• 수량: {buy_amount:.6f}개\n• 단가: {current_price:,.0f}원\n• 전략: 장기 보유 포트폴리오'
                })
            else:
                # 실전 매수
                if upbit:
                    order = upbit.buy_market_order(ticker, investment_per_coin)
                    if order:
                        results.append({
                            'ticker': ticker,
                            'success': True,
                            'order_id': order.get('uuid'),
                            'amount': buy_amount,
                            'price': current_price,
                            'invested': investment_per_coin,
                            'reason': f'[분산 투자] {ticker.replace("KRW-", "")} - 수익금 재투자 전략\n• 투자금: {investment_per_coin:,}원\n• 주문ID: {order.get("uuid")[:8]}...\n• 전략: 장기 보유 포트폴리오'
                        })
                    else:
                        results.append({
                            'ticker': ticker,
                            'success': False,
                            'message': '주문 실패'
                        })
        
        except Exception as e:
            results.append({
                'ticker': ticker,
                'success': False,
                'message': str(e)
            })
    
    success_count = sum(1 for r in results if r['success'])
    
    return {
        'success': True,
        'total_invested': success_count * investment_per_coin,
        'results': results,
        'summary': f'포트폴리오 분산 매수: {success_count}/4개 성공'
    }


def check_profit_trigger(start_seed, current_total_value, threshold=1.10):
    """
    수익 발생 여부 확인
    
    Args:
        start_seed: 초기 시드
        current_total_value: 현재 총 자산 (현금 + 코인)
        threshold: 수익 기준 (기본 10%)
    
    Returns:
        bool: 분산 매수 실행 여부
    """
    profit_rate = (current_total_value - start_seed) / start_seed
    return profit_rate >= (threshold - 1.0)


def get_available_coins():
    """
    선택 가능한 코인 목록 반환
    
    Returns:
        list: [('KRW-BTC', '비트코인'), ('KRW-ETH', '이더리움'), ...]
    """
    return [
        ('KRW-BTC', '비트코인'),
        ('KRW-ETH', '이더리움'),
        ('KRW-XRP', '리플'),
        ('KRW-SOL', '솔라나'),
        ('KRW-DOGE', '도지코인'),
        ('KRW-ADA', '에이다'),
        ('KRW-AVAX', '아발란체'),
        ('KRW-DOT', '폴카닷'),
        ('KRW-MATIC', '폴리곤'),
        ('KRW-SHIB', '시바이누'),
        ('KRW-ATOM', '코스모스'),
        ('KRW-LINK', '체인링크'),
        ('KRW-BCH', '비트코인캐시'),
        ('KRW-NEAR', '니어프로토콜'),
        ('KRW-UNI', '유니스왑'),
        ('KRW-ALGO', '알고랜드'),
        ('KRW-HBAR', '헤데라'),
        ('KRW-APT', '앱토스'),
        ('KRW-SUI', '수이'),
        ('KRW-ARB', '아비트럼'),
        ('KRW-OP', '옵티미즘'),
        ('KRW-SEI', '세이'),
        ('KRW-STRK', '스타크넷'),
        ('KRW-WLD', '월드코인'),
    ]
