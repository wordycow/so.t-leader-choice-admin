#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
거래 이유 생성기
매수/매도 시 사용자가 납득할 수 있는 상세한 이유 제공
"""

def generate_buy_reason(ticker, current_price, patterns, strategy_id):
    """
    매수 이유 생성
    
    Args:
        ticker: 코인 티커 (예: KRW-BTC)
        current_price: 현재 가격
        patterns: 감지된 패턴들 (dict)
        strategy_id: 전략 ID (surge_hunter, dip_hunter 등)
    
    Returns:
        str: 매수 이유 (사용자가 이해할 수 있는 형태)
    """
    coin_name = ticker.replace('KRW-', '')
    
    reasons = []
    
    # 전략별 핵심 이유
    if strategy_id == 'surge_hunter':
        if patterns.get('surge_1m', 0) > 0:
            reasons.append(f"🚀 1분봉 급등 감지: {patterns['surge_1m']:.2f}% 상승")
        if patterns.get('surge_3m', 0) > 0:
            reasons.append(f"📈 3분봉 강한 상승세: {patterns['surge_3m']:.2f}% 상승")
        if patterns.get('volume_spike', 0) > 2:
            reasons.append(f"💥 거래량 폭발: 평균의 {patterns['volume_spike']:.1f}배")
        main_reason = f"급등장 진입 신호 - 단기 상승 모멘텀 포착"
        
    elif strategy_id == 'dip_hunter':
        if patterns.get('dip_rate', 0) < -1.5:
            reasons.append(f"💎 급락 저점 감지: {patterns['dip_rate']:.2f}% 하락")
        if patterns.get('rsi', 50) < 35:
            reasons.append(f"📉 RSI 과매도 구간: {patterns['rsi']:.1f} (매수 타이밍)")
        if patterns.get('volume_spike', 0) > 2:
            reasons.append(f"🔥 공황 매도 포착: 거래량 {patterns['volume_spike']:.1f}배 증가")
        main_reason = f"급락 반등 기회 - 과매도 구간에서 저점 매수"
        
    elif strategy_id == 'box_trader':
        box_bottom = patterns.get('box_bottom', current_price)
        box_top = patterns.get('box_top', current_price * 1.03)
        reasons.append(f"📦 박스권 하단 감지: {box_bottom:,.0f}원 근처")
        reasons.append(f"🎯 목표가: {box_top:,.0f}원 (박스 상단)")
        reasons.append(f"📊 박스권 범위: ±{patterns.get('box_range', 3):.1f}%")
        main_reason = f"박스권 하단 매수 - 상단 반등 기대"
        
    elif strategy_id == 'trend_follower':
        if patterns.get('ma_20', 0) < current_price:
            reasons.append(f"📈 20일 이평선 돌파: {patterns['ma_20']:,.0f}원")
        if patterns.get('ma_60', 0) < current_price:
            reasons.append(f"🚀 60일 이평선 상향: {patterns['ma_60']:,.0f}원")
        if patterns.get('trend_strength', 0) > 0:
            reasons.append(f"💪 추세 강도: {patterns['trend_strength']:.1f}% 상승세")
        main_reason = f"상승 추세 편승 - 중기 모멘텀 진입"
        
    elif strategy_id == 'volume_hunter':
        if patterns.get('volume_spike', 0) > 2.5:
            reasons.append(f"🔥 거래량 급증: 평균의 {patterns['volume_spike']:.1f}배")
        if patterns.get('volume_ma_ratio', 0) > 2:
            reasons.append(f"📊 수급 변화 감지: 매집 신호")
        reasons.append(f"💰 큰 손 진입 추정: 대규모 거래량")
        main_reason = f"거래량 기반 매수 - 수급 변화 포착"
    
    else:
        main_reason = f"AI 분석 매수 신호"
        reasons.append(f"📊 현재가: {current_price:,.0f}원")
    
    # 최종 이유 조합
    reason_text = f"[{coin_name}] {main_reason}\n"
    if reasons:
        reason_text += "\n".join(f"• {r}" for r in reasons)
    
    return reason_text


def generate_sell_reason(ticker, buy_price, sell_price, profit_rate, hold_time_minutes, reason_type):
    """
    매도 이유 생성
    
    Args:
        ticker: 코인 티커
        buy_price: 매수가
        sell_price: 매도가
        profit_rate: 수익률 (%)
        hold_time_minutes: 보유 시간 (분)
        reason_type: 매도 이유 타입 (target_profit, stop_loss, timeout, recovery)
    
    Returns:
        str: 매도 이유
    """
    coin_name = ticker.replace('KRW-', '')
    profit_amount = (sell_price - buy_price) * (1 if profit_rate > 0 else -1)
    
    reasons = []
    
    if reason_type == 'target_profit':
        if profit_rate >= 4.0:
            main_reason = f"🎯 고수익 목표 달성"
            reasons.append(f"✨ 수익률 {profit_rate:+.2f}% - 4배 목표가 도달")
        elif profit_rate >= 2.5:
            main_reason = f"🎯 중수익 목표 달성"
            reasons.append(f"💰 수익률 {profit_rate:+.2f}% - 2.5배 목표가 도달")
        else:
            main_reason = f"🎯 목표 수익 달성"
            reasons.append(f"✅ 수익률 {profit_rate:+.2f}% - 목표가 도달")
        
        reasons.append(f"💵 매수가: {buy_price:,.0f}원 → 매도가: {sell_price:,.0f}원")
        reasons.append(f"⏱️ 보유 시간: {hold_time_minutes}분")
        
        if hold_time_minutes < 10:
            reasons.append(f"⚡ 단타 성공 - 빠른 수익 실현")
        elif hold_time_minutes < 60:
            reasons.append(f"🎮 스윙 성공 - 적정 타이밍 매도")
        else:
            reasons.append(f"🏆 중기 보유 성공 - 안정적 수익")
    
    elif reason_type == 'stop_loss':
        main_reason = f"🛡️ 손절 실행 (손실 제한)"
        reasons.append(f"⚠️ 손실률 {profit_rate:.2f}% - 추가 하락 방지")
        reasons.append(f"💵 매수가: {buy_price:,.0f}원 → 매도가: {sell_price:,.0f}원")
        reasons.append(f"🔒 손실 확정하여 추가 리스크 차단")
        
        if profit_rate <= -5:
            reasons.append(f"🚨 큰 손실 발생 - 즉시 정리")
        else:
            reasons.append(f"✅ 손절 기준 준수 - 리스크 관리")
    
    elif reason_type == 'timeout':
        main_reason = f"⏰ 보유 시간 초과"
        reasons.append(f"⏱️ {hold_time_minutes}분 보유 - 장기화 방지")
        reasons.append(f"💵 매수가: {buy_price:,.0f}원 → 매도가: {sell_price:,.0f}원")
        
        if profit_rate > 0:
            reasons.append(f"✅ 소폭 수익 {profit_rate:+.2f}% - 안전 매도")
        else:
            reasons.append(f"⚠️ 소폭 손실 {profit_rate:.2f}% - 자금 회전")
    
    elif reason_type == 'recovery':
        main_reason = f"🔄 복구 모드 매도"
        reasons.append(f"💡 손실 복구 전략 실행")
        reasons.append(f"💵 매수가: {buy_price:,.0f}원 → 매도가: {sell_price:,.0f}원")
        
        if profit_rate > 0:
            reasons.append(f"✅ 복구 성공 {profit_rate:+.2f}% - 손실 만회")
        else:
            reasons.append(f"⚠️ 부분 복구 {profit_rate:.2f}% - 재시도 준비")
    
    elif reason_type == 'dip_recovery':
        main_reason = f"💎 급락 반등 매도 (원가 복귀)"
        reasons.append(f"🎯 목표: 원가 회복 ({buy_price:,.0f}원)")
        reasons.append(f"📈 현재가: {sell_price:,.0f}원")
        
        if profit_rate >= -0.5:
            reasons.append(f"✅ 원가 근접 - 안전 매도")
        else:
            reasons.append(f"⚠️ 복구 진행 중 - 부분 정리")
    
    else:
        main_reason = f"💼 전략 매도"
        reasons.append(f"수익률: {profit_rate:+.2f}%")
        reasons.append(f"보유: {hold_time_minutes}분")
    
    # 최종 이유 조합
    reason_text = f"[{coin_name}] {main_reason}\n"
    if reasons:
        reason_text += "\n".join(f"• {r}" for r in reasons)
    
    return reason_text
