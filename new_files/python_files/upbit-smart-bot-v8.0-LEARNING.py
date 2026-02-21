#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 업비트 AI 학습 매매 봇 v8.0 - PATTERN LEARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 핵심: 패턴 학습 + 멀티 전략 경쟁 + 최적 전략 자동 선택

✨ 학습 패턴:
1. 박스권 (Range-bound)
2. 상승 추세 (Uptrend)
3. 하락 추세 (Downtrend)
4. 급등 후 수급 이탈 (Post-surge drain)
5. 수급 유입 (Volume influx)

🏆 멀티 전략 경쟁:
- Strategy A: 급등 포착 (기존)
- Strategy B: 급락 저점 매수 (v7.3)
- Strategy C: 박스권 하단 매수
- Strategy D: 추세 추종
- Strategy E: 수급 기반 진입

각 전략이 실시간 경쟁 → 승률/수익률 높은 전략 자동 채택
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
import threading
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import traceback

# ═══════════════════════════════════════════════════════
# 🧠 AI 학습 설정
# ═══════════════════════════════════════════════════════
LEARNING_CONFIG = {
    'enable_learning': True,
    'min_data_for_learning': 10,      # 최소 10개 거래 후 학습 시작
    'learning_interval': 50,          # 50개 거래마다 재학습
    'pattern_history_size': 500,      # 최근 500개 패턴 저장
    'strategy_performance_window': 20, # 최근 20개 거래로 성과 평가
}

# ═══════════════════════════════════════════════════════
# 📊 패턴 분석 설정
# ═══════════════════════════════════════════════════════
PATTERN_CONFIG = {
    # 박스권 감지
    'box_range_threshold': 3.0,       # 3% 이내 변동 = 박스권
    'box_min_duration': 30,           # 최소 30분
    
    # 추세 감지
    'trend_ma_short': 20,             # 단기 이동평균 (20분)
    'trend_ma_long': 60,              # 장기 이동평균 (60분)
    'uptrend_threshold': 2.0,         # 상승추세: +2% 이상
    'downtrend_threshold': -2.0,      # 하락추세: -2% 이하
    
    # 수급 분석
    'volume_ma_period': 20,           # 거래량 평균 기간
    'volume_surge_ratio': 2.5,        # 수급 유입: 2.5배 이상
    'volume_drain_ratio': 0.3,        # 수급 이탈: 0.3배 이하
    
    # 급등 후 패턴
    'post_surge_duration': 60,        # 급등 후 60분간 관찰
    'post_surge_threshold': 5.0,      # 5% 이상 급등
}

# ═══════════════════════════════════════════════════════
# 🏆 멀티 전략 정의
# ═══════════════════════════════════════════════════════
STRATEGIES = {
    'surge_hunter': {
        'name': '급등 포착',
        'description': '급등 신호 즉시 진입',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'dip_hunter': {
        'name': '급락 저점 매수',
        'description': '과매도 저점 포착 → 원가 복귀',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'box_trader': {
        'name': '박스권 하단 매수',
        'description': '박스권 하단에서 매수 → 상단 매도',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'trend_follower': {
        'name': '추세 추종',
        'description': '상승추세 진입 → 추세 이탈 시 매도',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'volume_hunter': {
        'name': '수급 기반',
        'description': '수급 유입 감지 → 수급 이탈 전 매도',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    }
}

# ═══════════════════════════════════════════════════════
# 🎮 봇 상태 관리
# ═══════════════════════════════════════════════════════
bot_state = {
    'running': False,
    'mode': 'practice',
    'upbit': None,
    'thread': None,
    
    # 시뮬레이션
    'simulation_seed': 1000000,
    'simulation_krw': 1000000,
    'simulation_holdings': {},
    'simulation_start_seed': 1000000,
    
    # 학습 데이터
    'pattern_history': deque(maxlen=LEARNING_CONFIG['pattern_history_size']),
    'trade_results': deque(maxlen=LEARNING_CONFIG['pattern_history_size']),
    'strategy_performance': STRATEGIES.copy(),
    
    # 현재 패턴 분석
    'current_patterns': {},  # {ticker: {type, confidence, data}}
    
    # 통계
    'statistics': {
        'total_trades': 0,
        'winning_trades': 0,
        'losing_trades': 0,
        'total_profit': 0,
        'best_strategy': None,
        'pattern_accuracy': {},
    },
    
    'last_update': None,
    'error': None,
    'start_time': None,
}

# ═══════════════════════════════════════════════════════
# 📝 로깅
# ═══════════════════════════════════════════════════════
def log(message, level="INFO"):
    """로그 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "INFO": "\033[96m",
        "PATTERN": "\033[95m",
        "LEARN": "\033[94m"
    }
    color = colors.get(level, "\033[0m")
    reset = "\033[0m"
    print(f"{color}[{timestamp}] {level}: {message}{reset}")

# ═══════════════════════════════════════════════════════
# 📊 패턴 분석 함수
# ═══════════════════════════════════════════════════════
def calculate_rsi(df, period=14):
    """RSI 계산"""
    try:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if len(rsi) > 0 else 50
    except:
        return 50

def detect_box_range(ticker):
    """박스권 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=50)
        if df is None or len(df) < 30:
            return None
        
        # 최근 30분간 고가/저가
        recent_high = df['high'].iloc[-6:].max()
        recent_low = df['low'].iloc[-6:].min()
        range_pct = ((recent_high - recent_low) / recent_low) * 100
        
        # 박스권 조건: 변동폭 3% 이내
        if range_pct <= PATTERN_CONFIG['box_range_threshold']:
            current_price = df['close'].iloc[-1]
            box_position = (current_price - recent_low) / (recent_high - recent_low)
            
            return {
                'type': 'BOX_RANGE',
                'high': recent_high,
                'low': recent_low,
                'position': box_position,  # 0=하단, 1=상단
                'confidence': 1.0 - (range_pct / PATTERN_CONFIG['box_range_threshold']),
                'action': 'BUY' if box_position < 0.3 else ('SELL' if box_position > 0.7 else 'HOLD')
            }
        
        return None
    except:
        return None

def detect_trend(ticker):
    """추세 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=70)
        if df is None or len(df) < 60:
            return None
        
        # 이동평균
        ma_short = df['close'].rolling(window=PATTERN_CONFIG['trend_ma_short']).mean()
        ma_long = df['close'].rolling(window=PATTERN_CONFIG['trend_ma_long']).mean()
        
        current_price = df['close'].iloc[-1]
        ma_short_now = ma_short.iloc[-1]
        ma_long_now = ma_long.iloc[-1]
        
        # 추세 판단
        trend_strength = ((ma_short_now - ma_long_now) / ma_long_now) * 100
        
        if trend_strength >= PATTERN_CONFIG['uptrend_threshold']:
            return {
                'type': 'UPTREND',
                'strength': trend_strength,
                'ma_short': ma_short_now,
                'ma_long': ma_long_now,
                'confidence': min(trend_strength / 5.0, 1.0),
                'action': 'BUY' if current_price < ma_short_now * 1.01 else 'HOLD'
            }
        elif trend_strength <= PATTERN_CONFIG['downtrend_threshold']:
            return {
                'type': 'DOWNTREND',
                'strength': abs(trend_strength),
                'ma_short': ma_short_now,
                'ma_long': ma_long_now,
                'confidence': min(abs(trend_strength) / 5.0, 1.0),
                'action': 'AVOID'
            }
        
        return None
    except:
        return None

def detect_volume_pattern(ticker):
    """수급 패턴 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=30)
        if df is None or len(df) < 20:
            return None
        
        vol_avg = df['volume'].iloc[-20:-1].mean()
        vol_now = df['volume'].iloc[-1]
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1.0
        
        # 수급 유입
        if vol_ratio >= PATTERN_CONFIG['volume_surge_ratio']:
            price_change = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            
            return {
                'type': 'VOLUME_SURGE',
                'ratio': vol_ratio,
                'price_change': price_change,
                'confidence': min(vol_ratio / 5.0, 1.0),
                'action': 'BUY' if price_change > 0 else 'WATCH'
            }
        
        # 수급 이탈
        elif vol_ratio <= PATTERN_CONFIG['volume_drain_ratio']:
            return {
                'type': 'VOLUME_DRAIN',
                'ratio': vol_ratio,
                'confidence': 1.0 - vol_ratio,
                'action': 'SELL'
            }
        
        return None
    except:
        return None

def detect_post_surge_pattern(ticker):
    """급등 후 패턴 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=20)
        if df is None or len(df) < 15:
            return None
        
        # 최근 15~10분 전 고점
        past_high = df['high'].iloc[-15:-10].max()
        current_price = df['close'].iloc[-1]
        
        # 급등 확인
        surge_from_past = ((past_high - df['low'].iloc[-15]) / df['low'].iloc[-15]) * 100
        
        if surge_from_past >= PATTERN_CONFIG['post_surge_threshold']:
            # 현재 고점 대비 위치
            pullback = ((past_high - current_price) / past_high) * 100
            
            return {
                'type': 'POST_SURGE',
                'surge_amount': surge_from_past,
                'pullback': pullback,
                'peak_price': past_high,
                'confidence': min(surge_from_past / 10.0, 1.0),
                'action': 'BUY' if 3.0 <= pullback <= 7.0 else 'AVOID'  # 3~7% 되돌림 시 진입
            }
        
        return None
    except:
        return None

def analyze_all_patterns(ticker):
    """모든 패턴 종합 분석"""
    try:
        patterns = {
            'box': detect_box_range(ticker),
            'trend': detect_trend(ticker),
            'volume': detect_volume_pattern(ticker),
            'post_surge': detect_post_surge_pattern(ticker)
        }
        
        # None이 아닌 패턴만 반환
        active_patterns = {k: v for k, v in patterns.items() if v is not None}
        
        if active_patterns:
            log(f"📊 {ticker} 패턴: {list(active_patterns.keys())}", "PATTERN")
        
        return active_patterns
    except Exception as e:
        return {}

# ═══════════════════════════════════════════════════════
# 🏆 전략 선택 및 경쟁
# ═══════════════════════════════════════════════════════
def select_best_strategy(ticker, patterns):
    """현재 패턴에 맞는 최적 전략 선택"""
    try:
        strategy_scores = {}
        
        # 각 전략의 점수 계산
        for strategy_id, strategy in bot_state['strategy_performance'].items():
            if not strategy['enabled']:
                continue
            
            score = 0.0
            perf = strategy['performance']
            
            # 1. 과거 성과 (승률 × 평균 수익)
            if perf['trades'] > 0:
                win_rate = perf['wins'] / perf['trades']
                avg_profit = perf['total_profit'] / perf['trades']
                performance_score = win_rate * avg_profit * strategy['weight']
                score += performance_score * 0.5
            
            # 2. 패턴 적합도
            pattern_match_score = 0.0
            
            if 'box' in patterns and strategy_id == 'box_trader':
                pattern_match_score = patterns['box']['confidence'] * 2.0
            elif 'trend' in patterns and strategy_id == 'trend_follower':
                pattern_match_score = patterns['trend']['confidence'] * 2.0
            elif 'volume' in patterns and strategy_id == 'volume_hunter':
                pattern_match_score = patterns['volume']['confidence'] * 2.0
            elif 'post_surge' in patterns and strategy_id == 'surge_hunter':
                pattern_match_score = patterns['post_surge']['confidence'] * 1.5
            
            score += pattern_match_score * 0.5
            
            strategy_scores[strategy_id] = score
        
        # 최고 점수 전략 선택
        if strategy_scores:
            best_strategy = max(strategy_scores, key=strategy_scores.get)
            best_score = strategy_scores[best_strategy]
            
            log(f"🏆 {ticker} 최적 전략: {STRATEGIES[best_strategy]['name']} (점수: {best_score:.2f})", "LEARN")
            
            return best_strategy, best_score
        
        return None, 0.0
        
    except Exception as e:
        log(f"전략 선택 오류: {e}", "ERROR")
        return None, 0.0

# ═══════════════════════════════════════════════════════
# 🧠 학습 시스템
# ═══════════════════════════════════════════════════════
def learn_from_trade(trade_result):
    """거래 결과로부터 학습"""
    try:
        strategy_id = trade_result.get('strategy')
        success = trade_result.get('profit_rate', 0) > 0
        profit = trade_result.get('profit_rate', 0)
        
        if strategy_id and strategy_id in bot_state['strategy_performance']:
            perf = bot_state['strategy_performance'][strategy_id]['performance']
            perf['trades'] += 1
            if success:
                perf['wins'] += 1
            perf['total_profit'] += profit
            
            # 승률 계산
            win_rate = (perf['wins'] / perf['trades'] * 100) if perf['trades'] > 0 else 0
            
            log(f"🧠 학습: {STRATEGIES[strategy_id]['name']} | "
                f"거래: {perf['trades']}회 | 승률: {win_rate:.1f}% | "
                f"평균수익: {(perf['total_profit']/perf['trades']):.2f}%", "LEARN")
        
        # 패턴 학습
        bot_state['trade_results'].append(trade_result)
        
        # 주기적 재학습
        if len(bot_state['trade_results']) % LEARNING_CONFIG['learning_interval'] == 0:
            optimize_strategies()
        
    except Exception as e:
        log(f"학습 오류: {e}", "ERROR")

def optimize_strategies():
    """전략 가중치 최적화"""
    try:
        log("🔄 전략 최적화 시작...", "LEARN")
        
        # 최근 성과 기반 가중치 조정
        for strategy_id, strategy in bot_state['strategy_performance'].items():
            perf = strategy['performance']
            
            if perf['trades'] >= 5:  # 최소 5회 거래
                win_rate = perf['wins'] / perf['trades']
                avg_profit = perf['total_profit'] / perf['trades']
                
                # 가중치 조정 (승률 70% 이상 or 평균 수익 3% 이상 = 가중치 증가)
                if win_rate >= 0.7 or avg_profit >= 3.0:
                    strategy['weight'] = min(strategy['weight'] * 1.1, 2.0)
                    log(f"📈 {strategy['name']} 가중치 증가: {strategy['weight']:.2f}", "LEARN")
                elif win_rate < 0.4 and avg_profit < 1.0:
                    strategy['weight'] = max(strategy['weight'] * 0.9, 0.5)
                    log(f"📉 {strategy['name']} 가중치 감소: {strategy['weight']:.2f}", "LEARN")
        
        # 최고 성과 전략 기록
        best_strategy = max(
            bot_state['strategy_performance'].items(),
            key=lambda x: (x[1]['performance']['wins'] / max(x[1]['performance']['trades'], 1))
        )
        bot_state['statistics']['best_strategy'] = best_strategy[0]
        
        log(f"✅ 최적 전략: {STRATEGIES[best_strategy[0]]['name']}", "SUCCESS")
        
    except Exception as e:
        log(f"최적화 오류: {e}", "ERROR")

# ═══════════════════════════════════════════════════════
# 🚀 Flask 웹 서버
# ═══════════════════════════════════════════════════════
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('dashboard-learning.html')

@app.route('/api/status')
def api_status():
    try:
        return jsonify({
            'running': bot_state['running'],
            'mode': bot_state['mode'],
            'simulation': {
                'seed': bot_state['simulation_seed'],
                'current_krw': bot_state['simulation_krw'],
                'total_value': bot_state['simulation_krw'] + sum(
                    h['amount'] * h['avg_price'] 
                    for h in bot_state['simulation_holdings'].values()
                ),
                'profit_rate': (
                    (bot_state['simulation_krw'] - bot_state['simulation_start_seed']) / 
                    bot_state['simulation_start_seed'] * 100
                ) if bot_state['simulation_start_seed'] > 0 else 0
            },
            'strategies': bot_state['strategy_performance'],
            'statistics': bot_state['statistics'],
            'patterns': bot_state['current_patterns'],
            'last_update': bot_state['last_update'].isoformat() if bot_state['last_update'] else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    log("🚀 AI 학습 매매 봇 v8.0 시작!", "SUCCESS")
    log("📊 멀티 전략 경쟁 시스템 활성화", "INFO")
    log("🧠 패턴 학습 엔진 준비 완료", "LEARN")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

@app.route('/api/start', methods=['POST'])
def api_start():
    try:
        data = request.json or {}
        mode = data.get('mode', 'practice')
        seed = data.get('seed', 1000000)
        
        if bot_state['running']:
            return jsonify({'success': False, 'message': '봇이 이미 실행 중입니다.'})
        
        bot_state['mode'] = mode
        bot_state['simulation_seed'] = seed
        bot_state['simulation_krw'] = seed
        bot_state['simulation_start_seed'] = seed
        bot_state['running'] = True
        
        # 별도 스레드에서 봇 실행
        thread = threading.Thread(target=bot_main_loop, daemon=True)
        thread.start()
        bot_state['thread'] = thread
        
        return jsonify({'success': True, 'message': '봇이 시작되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    bot_state['running'] = False
    return jsonify({'success': True, 'message': '봇이 중지되었습니다.'})

# ═══════════════════════════════════════════════════════
# 💰 거래 실행
# ═══════════════════════════════════════════════════════
def execute_trade(ticker, strategy_id, patterns, mode='practice'):
    """전략에 따라 거래 실행"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        # 투자 금액 계산
        available_krw = bot_state['simulation_krw']
        invest_amount = min(available_krw * 0.15, 150000)
        
        if invest_amount < 5000:
            return None
        
        buy_amount = invest_amount / current_price
        
        # 매수 실행
        bot_state['simulation_krw'] -= invest_amount
        
        bot_state['simulation_holdings'][ticker] = {
            'amount': buy_amount,
            'avg_price': current_price,
            'invested': invest_amount,
            'entry_time': datetime.now(),
            'strategy': strategy_id,
            'patterns': patterns,
            'peak_price': current_price
        }
        
        log(f"💰 매수: {ticker} | {current_price:,.0f}원 | 전략: {STRATEGIES[strategy_id]['name']}", "SUCCESS")
        
        return {
            'type': 'BUY',
            'ticker': ticker,
            'price': current_price,
            'amount': buy_amount,
            'strategy': strategy_id,
            'patterns': list(patterns.keys())
        }
        
    except Exception as e:
        log(f"거래 실행 오류: {e}", "ERROR")
        return None

def check_exit(ticker, holding):
    """청산 조건 체크"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        entry_price = holding['avg_price']
        profit_rate = (current_price - entry_price) / entry_price * 100
        strategy_id = holding.get('strategy')
        
        # 업데이트 최고가
        if current_price > holding.get('peak_price', 0):
            holding['peak_price'] = current_price
        
        # 전략별 청산 조건
        if strategy_id == 'box_trader':
            # 박스권: 상단 도달 or -2% 손절
            if profit_rate >= 2.5 or profit_rate <= -2.0:
                return True, f"박스권 {'익절' if profit_rate > 0 else '손절'}"
        
        elif strategy_id == 'trend_follower':
            # 추세 추종: 추세 이탈 or 트레일링 스톱
            peak = holding.get('peak_price', entry_price)
            drawdown = (peak - current_price) / peak * 100
            if profit_rate >= 3.0 and drawdown >= 1.5:
                return True, "추세 트레일링 스톱"
            elif profit_rate <= -2.5:
                return True, "추세 손절"
        
        elif strategy_id == 'volume_hunter':
            # 수급: +2% 익절 or -2% 손절
            if profit_rate >= 2.0 or profit_rate <= -2.0:
                return True, f"수급 {'익절' if profit_rate > 0 else '손절'}"
        
        else:
            # 기본: +3% 익절 or -2% 손절
            if profit_rate >= 3.0 or profit_rate <= -2.0:
                return True, f"기본 {'익절' if profit_rate > 0 else '손절'}"
        
        return False, None
        
    except:
        return False, None

def execute_exit(ticker, holding):
    """청산 실행"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        amount = holding['amount']
        entry_price = holding['avg_price']
        strategy_id = holding.get('strategy')
        
        # 매도 금액
        sell_krw = amount * current_price
        profit_krw = sell_krw - holding['invested']
        profit_rate = (current_price - entry_price) / entry_price * 100
        
        # KRW 복구
        bot_state['simulation_krw'] += sell_krw
        
        # 보유 제거
        del bot_state['simulation_holdings'][ticker]
        
        log(f"💸 매도: {ticker} | {current_price:,.0f}원 | 수익: {profit_rate:+.2f}% ({profit_krw:+,.0f}원)", 
            "SUCCESS" if profit_rate > 0 else "WARNING")
        
        # 학습 데이터 추가
        trade_result = {
            'ticker': ticker,
            'strategy': strategy_id,
            'entry_price': entry_price,
            'exit_price': current_price,
            'profit_rate': profit_rate,
            'profit_krw': profit_krw,
            'hold_time': (datetime.now() - holding['entry_time']).total_seconds() / 60,
            'patterns': holding.get('patterns', {}),
            'timestamp': datetime.now()
        }
        
        learn_from_trade(trade_result)
        
        # 통계 업데이트
        bot_state['statistics']['total_trades'] += 1
        if profit_rate > 0:
            bot_state['statistics']['winning_trades'] += 1
        else:
            bot_state['statistics']['losing_trades'] += 1
        bot_state['statistics']['total_profit'] += profit_rate
        
        return trade_result
        
    except Exception as e:
        log(f"청산 오류: {e}", "ERROR")
        return None

# ═══════════════════════════════════════════════════════
# 🔄 메인 봇 루프
# ═══════════════════════════════════════════════════════
def bot_main_loop():
    """메인 학습 봇 루프"""
    log("🚀 AI 학습 봇 시작!", "SUCCESS")
    log(f"🎮 모드: {bot_state['mode']}", "INFO")
    
    bot_state['start_time'] = datetime.now()
    scan_interval = 20  # 20초마다 스캔
    
    # 인기 코인 목록
    popular_tickers = [
        'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
        'KRW-ADA', 'KRW-AVAX', 'KRW-DOT', 'KRW-MATIC', 'KRW-LINK',
        'KRW-ATOM', 'KRW-ETC', 'KRW-NEAR', 'KRW-HBAR', 'KRW-APT'
    ]
    
    while bot_state['running']:
        try:
            log("🔍 패턴 스캔 시작...", "INFO")
            
            # 1. 보유 포지션 관리
            for ticker, holding in list(bot_state['simulation_holdings'].items()):
                should_exit, reason = check_exit(ticker, holding)
                if should_exit:
                    log(f"📤 청산 신호: {ticker} | {reason}", "INFO")
                    execute_exit(ticker, holding)
            
            # 2. 신규 진입 기회 탐색
            if len(bot_state['simulation_holdings']) < 3:  # 최대 3개 동시 보유
                import random
                scan_tickers = random.sample(popular_tickers, min(5, len(popular_tickers)))
                
                for ticker in scan_tickers:
                    try:
                        # 패턴 분석
                        patterns = analyze_all_patterns(ticker)
                        
                        if patterns:
                            # 패턴 저장
                            bot_state['current_patterns'][ticker] = patterns
                            
                            # 최적 전략 선택
                            best_strategy, score = select_best_strategy(ticker, patterns)
                            
                            if best_strategy and score > 0.5:
                                # 매수 실행
                                execute_trade(ticker, best_strategy, patterns, bot_state['mode'])
                                time.sleep(2)
                        
                    except Exception as e:
                        continue
            
            # 3. 상태 업데이트
            bot_state['last_update'] = datetime.now()
            
            # 4. 대기
            time.sleep(scan_interval)
            
        except Exception as e:
            log(f"메인 루프 오류: {e}", "ERROR")
            log(traceback.format_exc(), "ERROR")
            time.sleep(10)
    
    log("🛑 봇 중지됨", "WARNING")

