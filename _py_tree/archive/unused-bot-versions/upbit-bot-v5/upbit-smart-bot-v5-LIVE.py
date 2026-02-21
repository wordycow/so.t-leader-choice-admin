#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 업비트 스마트 스캘핑 봇 v5.0 - LIVE MODE (실전 모드)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 핵심 특징:
- 웹 대시보드: 한눈에 보이는 실시간 모니터링
- 수익 분산 투자: SOL, XRP, BTC, HBAR 순차 구매 (1만원씩)
- 시드 보호: 초기 시드 절대 보존
- 웹 제어: 봇 켜기/끄기, API 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading

# ═══════════════════════════════════════════════════════
# 🌐 Flask 웹 서버 설정
# ═══════════════════════════════════════════════════════
app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════════
# 🎨 전역 상태 관리
# ═══════════════════════════════════════════════════════
bot_state = {
    'running': False,
    'upbit': None,
    'thread': None,
    'initial_seed': 0,  # 초기 시드 (절대 건드리지 않음)
    'current_krw': 0,
    'total_profit': 0,
    'holdings': [],
    'trade_history': [],
    'profit_investments': [],  # 수익 투자 내역
    'last_update': None,
    'error': None,
    'first_run': True,  # 🔒 첫 실행 여부 (안전 모드)
    'start_time': None  # 봇 시작 시간
}

# 수익 투자 대상 코인 (우선순위 순)
PROFIT_TARGETS = ['KRW-SOL', 'KRW-XRP', 'KRW-BTC', 'KRW-HBAR']
PROFIT_INVEST_AMOUNT = 10000  # 1만원씩

# ═══════════════════════════════════════════════════════
# 🎨 터미널 색상 코드
# ═══════════════════════════════════════════════════════
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ═══════════════════════════════════════════════════════
# 💰 5단계 매수 + 3단계 매도 설정
# ═══════════════════════════════════════════════════════
BUY_STAGES = {
    1: {'amount': 6000, 'rsi_range': (28, 30), 'drop_percent': 0, 'description': '1차 테스트 매수 (6천원)'},
    2: {'amount': 10000, 'rsi_range': (26, 28), 'drop_percent': 3, 'description': '2차 추가 매수 (1만원)'},
    3: {'amount': 10000, 'rsi_range': (24, 26), 'drop_percent': 5, 'description': '3차 추가 매수 (1만원)'},
    4: {'amount': 10000, 'rsi_range': (22, 24), 'drop_percent': 7, 'description': '4차 추가 매수 (1만원)'},
    5: {'amount': 100000, 'rsi_range': (0, 22), 'drop_percent': 10, 'description': '최종 승부수 (10만원)'}
}

SELL_STAGES = {
    1: {'ratio': 0.50, 'profit_target': 2.5, 'description': '1차 익절 (50%, 가장 높은 가격)'},
    2: {'ratio': 0.30, 'profit_target': 2.0, 'description': '2차 익절 (30%)'},
    3: {'ratio': 0.20, 'profit_target': 1.5, 'description': '3차 익절 (20%, 잔량)'}
}

# 코인별 매수/매도 이력 저장
coin_trading_history = {}

# ═══════════════════════════════════════════════════════
# 📝 로깅 함수
# ═══════════════════════════════════════════════════════
def log(message, level="INFO", color=None):
    """상세한 로그 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    level_colors = {
        "INFO": Colors.CYAN,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "STRATEGY": Colors.BLUE,
        "REASON": Colors.HEADER,
    }
    
    color = color or level_colors.get(level, Colors.END)
    prefix = f"{color}[{level}]{Colors.END}"
    
    log_msg = f"{timestamp} {prefix} {message}"
    print(log_msg)
    
    clean_msg = f"{timestamp} [{level}] {message}\n"
    with open("bot.log", "a", encoding="utf-8") as f:
        f.write(clean_msg)

def log_separator():
    """구분선 출력"""
    print(f"\n{Colors.BOLD}{'═' * 80}{Colors.END}\n")

# ═══════════════════════════════════════════════════════
# 🚫 상장폐지 코인 목록 관리
# ═══════════════════════════════════════════════════════
DELISTED_COINS = set()
EXCLUDED_MARKETS = set()

def load_delisted_coins_config():
    """delisted_coins.json 파일에서 설정 로드"""
    global DELISTED_COINS, EXCLUDED_MARKETS
    
    config_file = "delisted_coins.json"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            DELISTED_COINS = set(config.get("delisted_coins", []))
            EXCLUDED_MARKETS = set(config.get("excluded_markets", []))
            
            log("📋 상장폐지 코인 설정 로드 완료", "SUCCESS")
        else:
            DELISTED_COINS = set(['KRW-AXS', 'KRW-WAXP', 'KRW-STEEM', 'KRW-SBD', 'KRW-SC', 'KRW-POWR', 'KRW-STORJ', 'KRW-RFR'])
            EXCLUDED_MARKETS = set(['USDT', 'BTC'])
        
        return DELISTED_COINS, EXCLUDED_MARKETS
        
    except Exception as e:
        log(f"❌ 설정 로드 실패: {e}", "ERROR")
        return set(), set()

def is_valid_market(ticker):
    """유효한 시장인지 검증"""
    for market in EXCLUDED_MARKETS:
        if ticker.startswith(f'{market}-'):
            return False
    
    if ticker in DELISTED_COINS:
        return False
    
    return True

# ═══════════════════════════════════════════════════════
# 🔑 API 키 관리
# ═══════════════════════════════════════════════════════
def load_api_keys():
    """api_keys.json 파일에서 API 키 로드"""
    config_file = "api_keys.json"
    
    if not os.path.exists(config_file):
        return None, None
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            keys = json.load(f)
        
        access_key = keys.get("access_key")
        secret_key = keys.get("secret_key")
        
        if access_key and secret_key and "여기에" not in access_key:
            log(f"✅ API 키 로드 성공: {access_key[:8]}****", "SUCCESS")
            return access_key, secret_key
        
        return None, None
        
    except Exception as e:
        log(f"❌ API 키 로드 실패: {e}", "ERROR")
        return None, None

def save_api_keys(access_key, secret_key):
    """API 키를 파일에 저장"""
    config_file = "api_keys.json"
    
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({
                "access_key": access_key,
                "secret_key": secret_key
            }, f, indent=2)
        
        log("✅ API 키 저장 완료", "SUCCESS")
        return True
    except Exception as e:
        log(f"❌ API 키 저장 실패: {e}", "ERROR")
        return False

# ═══════════════════════════════════════════════════════
# 📊 기술적 지표 계산
# ═══════════════════════════════════════════════════════
def calculate_rsi(df, period=14):
    """RSI 계산"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_bollinger_bands(df, period=20, std=2):
    """볼린저 밴드 계산"""
    sma = df['close'].rolling(window=period).mean()
    std_dev = df['close'].rolling(window=period).std()
    
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    
    return {
        'upper': upper.iloc[-1],
        'middle': sma.iloc[-1],
        'lower': lower.iloc[-1]
    }

def check_volume_increase(df):
    """거래량 증가 확인"""
    avg_volume = df['volume'].tail(20).mean()
    current_volume = df['volume'].iloc[-1]
    return current_volume >= avg_volume * 1.5

# ═══════════════════════════════════════════════════════
# 💰 수익 분산 투자
# ═══════════════════════════════════════════════════════
def invest_profit_sequentially(upbit, total_profit):
    """
    수익금을 순차적으로 분산 투자
    SOL → XRP → BTC → HBAR 순으로 1만원씩
    """
    if total_profit < PROFIT_INVEST_AMOUNT:
        log(f"수익금 부족 (현재: {total_profit:,.0f}원 < 필요: {PROFIT_INVEST_AMOUNT:,}원)", "INFO")
        return
    
    # 이미 투자한 코인 확인
    invested_coins = [inv['ticker'] for inv in bot_state['profit_investments']]
    
    # 다음 투자 대상 찾기
    next_target = None
    for target in PROFIT_TARGETS:
        if target not in invested_coins:
            next_target = target
            break
    
    if not next_target:
        log("모든 수익 투자 완료 (SOL, XRP, BTC, HBAR)", "SUCCESS")
        return
    
    log_separator()
    log(f"💎 수익 분산 투자 시작: {next_target}", "SUCCESS")
    log(f"   투자 금액: {PROFIT_INVEST_AMOUNT:,}원", "INFO")
    
    try:
        # 실제 주문 실행
        order = upbit.buy_market_order(next_target, PROFIT_INVEST_AMOUNT)
        log(f"✅ {next_target} 매수 완료: {order}", "SUCCESS")
        
        # 투자 내역 기록
        bot_state['profit_investments'].append({
            'ticker': next_target,
            'amount': PROFIT_INVEST_AMOUNT,
            'timestamp': datetime.now().isoformat()
        })
        
        # 거래 이력에 추가
        bot_state['trade_history'].append({
            'type': 'PROFIT_INVEST',
            'ticker': next_target,
            'amount': PROFIT_INVEST_AMOUNT,
            'timestamp': datetime.now().isoformat()
        })
        
        log(f"💰 [실전 모드] {next_target} 실제 매수 완료!", "SUCCESS")
        
        # 다음 투자 확인
        remaining_profit = total_profit - PROFIT_INVEST_AMOUNT
        if remaining_profit >= PROFIT_INVEST_AMOUNT:
            log(f"💰 잔여 수익: {remaining_profit:,.0f}원 - 다음 투자 가능", "INFO")
            invest_profit_sequentially(upbit, remaining_profit)
        
    except Exception as e:
        log(f"❌ 수익 투자 실패: {e}", "ERROR")

# ═══════════════════════════════════════════════════════
# 💼 포트폴리오 분석
# ═══════════════════════════════════════════════════════
def analyze_portfolio(upbit):
    """현재 보유 중인 코인 분석"""
    try:
        balances = upbit.get_balances()
    except Exception as e:
        log(f"❌ 잔고 조회 실패: {e}", "ERROR")
        return 0, []
    
    if not isinstance(balances, list):
        return 0, []
    
    krw_balance = 0
    holdings = []
    
    for balance in balances:
        if not isinstance(balance, dict):
            continue
        
        try:
            currency = balance.get('currency', 'UNKNOWN')
            amount = float(balance.get('balance', 0))
            avg_buy_price = float(balance.get('avg_buy_price', 0))
        except (ValueError, TypeError):
            continue
        
        if currency == 'KRW':
            krw_balance = amount
            continue
        
        if amount > 0:
            ticker = f"KRW-{currency}"
            
            if not is_valid_market(ticker):
                continue
            
            try:
                current_price = pyupbit.get_current_price(ticker)
            except Exception:
                continue
            
            if current_price and current_price > 0:
                invested = avg_buy_price * amount
                current_value = current_price * amount
                profit = current_value - invested
                profit_rate = (profit / invested) * 100
                
                holdings.append({
                    'ticker': ticker,
                    'currency': currency,
                    'amount': amount,
                    'avg_buy_price': avg_buy_price,
                    'current_price': current_price,
                    'invested': invested,
                    'current_value': current_value,
                    'profit': profit,
                    'profit_rate': profit_rate
                })
    
    return krw_balance, holdings

# ═══════════════════════════════════════════════════════
# 🎯 봇 메인 로직 (v4.0 기반)
# ═══════════════════════════════════════════════════════
def get_buy_stage(ticker, current_price, avg_buy_price, rsi):
    """매수 단계 판단"""
    history = coin_trading_history.get(ticker, {
        'buy_stages_completed': [],
        'first_buy_price': None,
        'last_buy_time': None,
        'sell_stages_completed': [],
        'total_profit': 0
    })
    
    bought_stages = history.get('buy_stages_completed', [])
    first_price = history.get('first_buy_price')
    last_buy_time = history.get('last_buy_time')
    
    if not bought_stages:
        if rsi <= 30:
            return 1, f"1단계 매수 조건 충족 (RSI: {rsi:.1f})"
        else:
            return None, f"RSI({rsi:.1f})가 높아 매수 대기"
    
    next_stage = max(bought_stages) + 1
    
    if next_stage > 5:
        return None, "5단계 모두 완료"
    
    if last_buy_time:
        time_diff = datetime.now() - last_buy_time
        if time_diff < timedelta(minutes=10):
            remaining = 10 - (time_diff.seconds // 60)
            return None, f"매수 대기 시간 ({remaining}분 남음)"
    
    stage_info = BUY_STAGES[next_stage]
    required_drop = stage_info['drop_percent']
    current_drop = ((first_price - current_price) / first_price) * 100
    
    if current_drop < required_drop:
        return None, f"하락률 부족 ({current_drop:.1f}% < {required_drop}%)"
    
    rsi_min, rsi_max = stage_info['rsi_range']
    if not (rsi_min <= rsi < rsi_max):
        return None, f"RSI 범위 불일치"
    
    return next_stage, f"{next_stage}단계 조건 충족"

def get_sell_stage(ticker, profit_rate):
    """매도 단계 판단"""
    history = coin_trading_history.get(ticker, {
        'sell_stages_completed': []
    })
    
    sold_stages = history.get('sell_stages_completed', [])
    next_stage = len(sold_stages) + 1
    
    if next_stage > 3:
        return None, 0, "3단계 익절 모두 완료"
    
    stage_info = SELL_STAGES[next_stage]
    target_profit = stage_info['profit_target']
    
    if profit_rate >= target_profit:
        return next_stage, stage_info['ratio'], f"{next_stage}차 익절 조건 충족"
    else:
        return None, 0, f"익절 목표 미달"

def create_strategy(upbit, holding):
    """전략 수립"""
    ticker = holding['ticker']
    
    if not is_valid_market(ticker):
        return None
    
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=100)
    if df is None or len(df) < 20:
        return None
    
    current_price = holding['current_price']
    avg_buy_price = holding['avg_buy_price']
    profit_rate = holding['profit_rate']
    
    rsi = calculate_rsi(df)
    bb = calculate_bollinger_bands(df)
    
    strategy = {
        'ticker': ticker,
        'action': 'HOLD',
        'reason': [],
        'buy_stage': None,
        'buy_amount': 0,
        'sell_stage': None,
        'sell_ratio': 0,
        'rsi': rsi,
        'profit_rate': profit_rate
    }
    
    # 매도 우선
    sell_stage, sell_ratio, sell_reason = get_sell_stage(ticker, profit_rate)
    
    if sell_stage:
        strategy['action'] = 'SELL'
        strategy['sell_stage'] = sell_stage
        strategy['sell_ratio'] = sell_ratio
        strategy['reason'].append(("SELL", sell_reason))
        return strategy
    
    # 긴급 손절 (안전 모드: 첫 실행 후 1시간은 손절 안 함)
    if profit_rate <= -15.0:
        # 첫 실행 확인
        if bot_state['first_run']:
            # 봇 시작 후 1시간 경과 확인
            if bot_state['start_time']:
                elapsed = (datetime.now() - bot_state['start_time']).total_seconds() / 3600
                if elapsed < 1.0:  # 1시간 이내
                    log(f"⚠️  안전 모드: 손절 대기 중 {ticker} ({profit_rate:.2f}%, {elapsed*60:.0f}분 경과)", "WARNING")
                    strategy['reason'].append(("HOLD", f"안전 모드 - 손절 대기 ({elapsed*60:.0f}/60분)"))
                    return strategy
                else:
                    # 1시간 경과 → 안전 모드 해제
                    bot_state['first_run'] = False
                    log(f"🔓 안전 모드 해제: 이제 정상 손절이 작동합니다", "INFO")
        
        strategy['action'] = 'SELL'
        strategy['sell_stage'] = 0
        strategy['sell_ratio'] = 1.0
        strategy['reason'].append(("SELL", f"긴급 손절 ({profit_rate:.2f}%)"))
        return strategy
    
    # 매수 신호
    buy_stage, buy_reason = get_buy_stage(ticker, current_price, avg_buy_price, rsi)
    
    if buy_stage:
        strategy['action'] = 'BUY'
        strategy['buy_stage'] = buy_stage
        strategy['buy_amount'] = BUY_STAGES[buy_stage]['amount']
        strategy['reason'].append(("BUY", buy_reason))
    
    return strategy

def execute_order(upbit, strategy, holding, krw_balance):
    """주문 실행"""
    ticker = strategy['ticker']
    action = strategy['action']
    
    if action == 'HOLD':
        return
    
    try:
        if action == 'BUY':
            stage = strategy.get('buy_stage')
            buy_amount = strategy.get('buy_amount', 0)
            
            # 시드 보호: 현재 원화가 초기 시드보다 적으면 매수 금지
            if krw_balance < bot_state['initial_seed']:
                log(f"⚠️  시드 보호: 매수 금지 (현재: {krw_balance:,.0f} < 시드: {bot_state['initial_seed']:,.0f})", "WARNING")
                return
            
            if buy_amount < 5000 or krw_balance < buy_amount:
                return
            
            log(f"🔵 매수: {ticker} {stage}단계 {buy_amount:,}원", "INFO")
            
            # 실제 주문 실행
            order = upbit.buy_market_order(ticker, buy_amount)
            log(f"✅ 매수 주문 완료: {order}", "SUCCESS")
            
            history = coin_trading_history.get(ticker, {
                'buy_stages_completed': [],
                'first_buy_price': None,
                'last_buy_time': None,
                'sell_stages_completed': [],
                'total_profit': 0
            })
            
            if stage not in history['buy_stages_completed']:
                history['buy_stages_completed'].append(stage)
            
            if not history['first_buy_price']:
                history['first_buy_price'] = holding['current_price']
            
            history['last_buy_time'] = datetime.now()
            coin_trading_history[ticker] = history
            
            # 거래 이력 추가
            bot_state['trade_history'].append({
                'type': 'BUY',
                'ticker': ticker,
                'stage': stage,
                'amount': buy_amount,
                'timestamp': datetime.now().isoformat()
            })
            
        elif action == 'SELL':
            stage = strategy.get('sell_stage', 0)
            ratio = strategy.get('sell_ratio', 1.0)
            sell_amount = holding['amount'] * ratio
            
            log(f"🔴 매도: {ticker} {stage}차 익절 {ratio*100:.0f}%", "INFO")
            
            # 실제 주문 실행
            order = upbit.sell_market_order(ticker, sell_amount)
            log(f"✅ 매도 주문 완료: {order}", "SUCCESS")
            
            profit = (holding['current_price'] - holding['avg_buy_price']) * sell_amount
            
            history = coin_trading_history.get(ticker, {
                'sell_stages_completed': [],
                'total_profit': 0
            })
            
            if stage > 0 and stage not in history['sell_stages_completed']:
                history['sell_stages_completed'].append(stage)
            
            history['total_profit'] += profit
            coin_trading_history[ticker] = history
            
            bot_state['total_profit'] += profit
            
            # 거래 이력 추가
            bot_state['trade_history'].append({
                'type': 'SELL',
                'ticker': ticker,
                'stage': stage,
                'ratio': ratio,
                'profit': profit,
                'timestamp': datetime.now().isoformat()
            })
            
            # 3단계 익절 완료 시 수익 투자
            if stage == 3 and history['total_profit'] >= PROFIT_INVEST_AMOUNT:
                log(f"💎 3단계 익절 완료! 총 수익: {history['total_profit']:,.0f}원", "SUCCESS")
                invest_profit_sequentially(upbit, history['total_profit'])
                
                # 이력 초기화
                del coin_trading_history[ticker]
    
    except Exception as e:
        log(f"❌ 주문 실패: {e}", "ERROR")
        bot_state['error'] = str(e)

# ═══════════════════════════════════════════════════════
# 🤖 봇 메인 루프
# ═══════════════════════════════════════════════════════
def bot_main_loop():
    """봇 메인 루프"""
    log_separator()
    log("🤖 봇 시작", "SUCCESS")
    
    # API 키 로드
    access_key, secret_key = load_api_keys()
    if not access_key or not secret_key:
        log("❌ API 키가 없습니다", "ERROR")
        bot_state['error'] = "API 키 필요"
        bot_state['running'] = False
        return
    
    # Upbit 객체 생성
    try:
        upbit = pyupbit.Upbit(access_key, secret_key)
        bot_state['upbit'] = upbit
        log("✅ 업비트 연결 성공", "SUCCESS")
    except Exception as e:
        log(f"❌ 업비트 연결 실패: {e}", "ERROR")
        bot_state['error'] = str(e)
        bot_state['running'] = False
        return
    
    # 초기 시드 설정
    krw, _ = analyze_portfolio(upbit)
    if bot_state['initial_seed'] == 0:
        bot_state['initial_seed'] = krw
        log(f"💰 초기 시드: {krw:,.0f}원 (절대 보존)", "SUCCESS")
    
    # 봇 시작 시간 기록 (안전 모드용)
    if bot_state['start_time'] is None:
        bot_state['start_time'] = datetime.now()
        log(f"🔒 안전 모드 활성화: 1시간 동안 손절 보호", "INFO")
    
    # 상장폐지 설정 로드
    load_delisted_coins_config()
    
    iteration = 0
    while bot_state['running']:
        try:
            iteration += 1
            log(f"🔄 [{iteration}회차] 분석 시작", "INFO")
            
            # 포트폴리오 분석
            krw_balance, holdings = analyze_portfolio(upbit)
            bot_state['current_krw'] = krw_balance
            bot_state['holdings'] = holdings
            bot_state['last_update'] = datetime.now().isoformat()
            
            # 보유 코인 전략 실행
            for holding in holdings:
                if not bot_state['running']:
                    break
                
                strategy = create_strategy(upbit, holding)
                if strategy:
                    execute_order(upbit, strategy, holding, krw_balance)
            
            # 10초 대기
            for i in range(10):
                if not bot_state['running']:
                    break
                time.sleep(1)
        
        except Exception as e:
            log(f"❌ 오류: {e}", "ERROR")
            bot_state['error'] = str(e)
            time.sleep(10)
    
    log("🛑 봇 종료", "WARNING")

# ═══════════════════════════════════════════════════════
# 🌐 Flask API 엔드포인트
# ═══════════════════════════════════════════════════════
@app.route('/')
def index():
    """메인 대시보드"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """봇 상태 조회"""
    return jsonify({
        'running': bot_state['running'],
        'initial_seed': bot_state['initial_seed'],
        'current_krw': bot_state['current_krw'],
        'total_profit': bot_state['total_profit'],
        'holdings': bot_state['holdings'],
        'profit_investments': bot_state['profit_investments'],
        'trade_history': bot_state['trade_history'][-20:],  # 최근 20개
        'last_update': bot_state['last_update'],
        'error': bot_state['error']
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    """봇 시작"""
    if bot_state['running']:
        return jsonify({'success': False, 'message': '이미 실행 중'})
    
    bot_state['running'] = True
    bot_state['error'] = None
    thread = threading.Thread(target=bot_main_loop, daemon=True)
    thread.start()
    bot_state['thread'] = thread
    
    return jsonify({'success': True, 'message': '봇 시작'})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """봇 중지"""
    if not bot_state['running']:
        return jsonify({'success': False, 'message': '실행 중이 아님'})
    
    bot_state['running'] = False
    return jsonify({'success': True, 'message': '봇 중지'})

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API 키 설정"""
    if request.method == 'GET':
        access_key, _ = load_api_keys()
        return jsonify({
            'access_key': access_key[:8] + '****' if access_key else None
        })
    
    elif request.method == 'POST':
        data = request.json
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        
        if not access_key or not secret_key:
            return jsonify({'success': False, 'message': 'API 키 필요'})
        
        if save_api_keys(access_key, secret_key):
            return jsonify({'success': True, 'message': 'API 키 저장 완료'})
        else:
            return jsonify({'success': False, 'message': 'API 키 저장 실패'})

@app.route('/api/reset-seed', methods=['POST'])
def api_reset_seed():
    """초기 시드 재설정"""
    if bot_state['running']:
        return jsonify({'success': False, 'message': '봇 실행 중에는 불가'})
    
    bot_state['initial_seed'] = 0
    bot_state['total_profit'] = 0
    bot_state['profit_investments'] = []
    bot_state['trade_history'] = []
    
    return jsonify({'success': True, 'message': '초기화 완료'})

# ═══════════════════════════════════════════════════════
# 🚀 메인 실행
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"""
{Colors.BOLD}{Colors.CYAN}
  🤖 업비트 스마트 스캘핑 봇 v5.0
  🌐 웹 대시보드 + 수익 분산 투자
  💰 시드 보호 + SOL/XRP/BTC/HBAR 투자
{Colors.END}
""")
    
    print(f"{Colors.GREEN}🌐 웹 대시보드: http://localhost:5000{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  브라우저에서 접속하세요{Colors.END}\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
