#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 업비트 스마트 스캘핑 봇 v5.0 - 웹 대시보드 + 수익 분산 투자
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

# 트레이딩 데이터베이스 임포트
from trading_database import TradingDatabase

# ═══════════════════════════════════════════════════════
# 🌐 Flask 웹 서버 설정
# ═══════════════════════════════════════════════════════
app = Flask(__name__)
CORS(app)

# 트레이딩 데이터베이스 초기화
trading_db = TradingDatabase("trading_history.db")

# ═══════════════════════════════════════════════════════
# 💳 라이선스 설정
# ═══════════════════════════════════════════════════════
LICENSE_CONFIG = {
    'usdt_address': 'TLb5D3uDQjPQt6CzATM21t21etxGsSvtbt',  # USDT 수신 주소 (TRC-20)
    'price_per_day': 1,  # 1 USDT = 1일 (비례 계산)
    'min_amount': 10,  # 최소 10 USDT
    'network': 'TRC-20',  # Tron 네트워크
}

# ⚠️ 가격 정책 변경 예정:
# 현재: 1 USDT = 1일 (소수점 버림)
# 사용자 증가 시 가격 인상 예정 (예: 1 USDT = 0.5일)
# LICENSE_CONFIG['price_per_day'] 값을 변경하고
# save_license() 함수의 계산식도 함께 수정 필요

# ═══════════════════════════════════════════════════════
# 🎨 전역 상태 관리
# ═══════════════════════════════════════════════════════
bot_state = {
    'running': False,
    'mode': 'practice',  # 'practice' 또는 'live'
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
    'start_time': None,  # 봇 시작 시간
    'license': None,  # 라이선스 정보
    
    # 🎮 시뮬레이션 모드 전용 (연습 모드)
    'simulation_seed': 1000000,  # 시뮬레이션 시드 (기본 100만원)
    'simulation_krw': 1000000,  # 시뮬레이션 현재 잔고
    'simulation_holdings': {},  # 시뮬레이션 보유 코인 {'KRW-BTC': {'amount': 0.001, 'avg_price': 50000000}}
    'simulation_start_seed': 1000000,  # 시뮬레이션 시작 시드 (수익률 계산용)
    
    # 📊 학습 및 데이터 수집
    'current_session_id': None,  # 현재 세션 ID
    'trade_reasons': []  # 거래 이유 리스트 (실시간 표시용)
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
# 💳 라이선스 관리 시스템
# ═══════════════════════════════════════════════════════

def load_license():
    """라이선스 파일 로드"""
    license_file = "license.json"
    try:
        if os.path.exists(license_file):
            with open(license_file, "r", encoding="utf-8") as f:
                license_data = json.load(f)
            
            # 만료 확인
            if license_data.get('expiry_date'):
                expiry = datetime.fromisoformat(license_data['expiry_date'])
                if datetime.now() > expiry:
                    log("⚠️ 라이선스가 만료되었습니다", "WARNING")
                    license_data['status'] = 'expired'
                else:
                    days_left = (expiry - datetime.now()).days
                    log(f"✅ 라이선스 활성화됨 (남은 기간: {days_left}일)", "SUCCESS")
                    license_data['status'] = 'active'
                    license_data['days_left'] = days_left
            
            return license_data
        else:
            # 라이선스 파일 없음 - 연습 모드만 가능
            log("📝 라이선스 없음 - 연습 모드로 시작", "INFO")
            return {
                'status': 'none',
                'mode': 'practice'
            }
    except Exception as e:
        log(f"❌ 라이선스 로드 실패: {e}", "ERROR")
        return {'status': 'error', 'mode': 'practice'}

def save_license(txid, amount, network='TRC-20'):
    """라이선스 정보 저장"""
    license_file = "license.json"
    
    # 1 USDT = 1일 (소수점 버림)
    # 예: 10 USDT → 10일, 12.4 USDT → 12일, 20 USDT → 20일
    days = int(amount)  # 소수점 버림
    
    start_date = datetime.now()
    expiry_date = start_date + timedelta(days=days)
    
    license_data = {
        'txid': txid,
        'amount': amount,
        'network': network,
        'start_date': start_date.isoformat(),
        'expiry_date': expiry_date.isoformat(),
        'days': days,
        'status': 'active',
        'wallet_address': LICENSE_CONFIG['usdt_address']
    }
    
    try:
        with open(license_file, "w", encoding="utf-8") as f:
            json.dump(license_data, f, indent=2, ensure_ascii=False)
        
        log(f"✅ 라이선스 활성화 완료! ({amount} USDT → {days}일)", "SUCCESS")
        return license_data
    except Exception as e:
        log(f"❌ 라이선스 저장 실패: {e}", "ERROR")
        return None

def verify_txid(txid):
    """TXID 검증 (Tronscan API 사용)"""
    try:
        # Tronscan API로 트랜잭션 조회
        url = f"https://apilist.tronscanapi.com/api/transaction-info?hash={txid}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # 트랜잭션이 존재하는지 확인
            if not data or 'contractRet' not in data:
                return {'success': False, 'error': 'Invalid TXID'}
            
            # 성공적인 트랜잭션인지 확인
            if data['contractRet'] != 'SUCCESS':
                return {'success': False, 'error': 'Transaction failed'}
            
            # USDT 전송인지 확인 (TRC-20)
            if 'trc20TransferInfo' not in data:
                return {'success': False, 'error': 'Not a USDT transaction'}
            
            transfer_info = data['trc20TransferInfo'][0] if data['trc20TransferInfo'] else {}
            
            # 수신 주소 확인
            to_address = transfer_info.get('to_address', '')
            if to_address.lower() != LICENSE_CONFIG['usdt_address'].lower():
                return {'success': False, 'error': f'Wrong recipient address: {to_address}'}
            
            # 금액 확인 (6 decimals for USDT)
            amount_str = transfer_info.get('amount_str', '0')
            amount = float(amount_str) / 1000000  # USDT는 6 decimals
            
            # 최소 금액 확인 (10 USDT 이상)
            if amount < LICENSE_CONFIG['min_amount']:
                return {'success': False, 'error': f'Insufficient amount: {amount} USDT (minimum: {LICENSE_CONFIG["min_amount"]} USDT)'}
            
            return {
                'success': True,
                'amount': amount,
                'to_address': to_address,
                'from_address': transfer_info.get('from_address', ''),
                'timestamp': data.get('timestamp', 0)
            }
        else:
            return {'success': False, 'error': f'API error: {response.status_code}'}
    
    except Exception as e:
        log(f"❌ TXID 검증 중 오류: {e}", "ERROR")
        return {'success': False, 'error': str(e)}

def check_license_expiry():
    """라이선스 만료 체크 및 알림"""
    license_data = bot_state.get('license')
    
    if not license_data or license_data.get('status') != 'active':
        return
    
    expiry_date = datetime.fromisoformat(license_data['expiry_date'])
    now = datetime.now()
    days_left = (expiry_date - now).days
    hours_left = (expiry_date - now).seconds // 3600
    
    # 만료됨
    if now > expiry_date:
        log("🔴 라이선스가 만료되었습니다! 연습 모드로 전환됩니다.", "ERROR")
        bot_state['mode'] = 'practice'
        bot_state['license']['status'] = 'expired'
        return
    
    # 1일 미만 남음
    if days_left == 0:
        log(f"⚠️ 라이선스 만료 임박! ({hours_left}시간 남음)", "WARNING")
    # 3일 이하 남음
    elif days_left <= 3:
        log(f"⚠️ 라이선스가 {days_left}일 후 만료됩니다", "WARNING")

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
        # 모드에 따라 실제 주문 실행
        current_mode = bot_state.get('mode', 'practice')
        if current_mode == 'live':
            order = upbit.buy_market_order(next_target, PROFIT_INVEST_AMOUNT)
            log(f"✅ [실전 모드] {next_target} 매수 완료: {order}", "SUCCESS")
        else:
            log(f"⚠️  [연습 모드] {next_target} 투자 시뮬레이션", "WARNING")
        
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
            
            # 매수 이유 생성
            buy_reasons = strategy.get('reason', [])
            buy_reason_text = " | ".join([f"{r[0]}: {r[1]}" for r in buy_reasons if r[0] == 'BUY'])
            
            log(f"🔵 매수: {ticker} {stage}단계 {buy_amount:,}원", "INFO")
            log(f"📝 이유: {buy_reason_text}", "REASON")
            
            # RSI 값 가져오기
            rsi_value = strategy.get('rsi', 0)
            rsi_range = BUY_STAGES[stage]['rsi_range']
            drop_percent = BUY_STAGES[stage]['drop_percent']
            
            # 모드에 따라 실제 주문 실행
            current_mode = bot_state.get('mode', 'practice')
            if current_mode == 'live':
                order = upbit.buy_market_order(ticker, buy_amount)
                log(f"✅ [실전 모드] 매수 주문 체결: {order}", "SUCCESS")
            else:
                log(f"⚠️  [연습 모드] 매수 시뮬레이션", "WARNING")
            
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
            
            # 📊 데이터베이스에 매수 기록 (학습용)
            if bot_state['current_session_id']:
                try:
                    # 24시간 가격 변동
                    price_change_24h = 0
                    try:
                        ticker_data = pyupbit.get_ohlcv(ticker, interval="day", count=2)
                        if ticker_data is not None and len(ticker_data) >= 2:
                            prev_close = ticker_data.iloc[-2]['close']
                            curr_close = ticker_data.iloc[-1]['close']
                            price_change_24h = ((curr_close - prev_close) / prev_close) * 100
                    except:
                        pass
                    
                    trade_data = {
                        'timestamp': datetime.now().isoformat(),
                        'trade_type': 'BUY',
                        'ticker': ticker,
                        'amount': buy_amount / holding['current_price'],  # 코인 수량
                        'price': holding['current_price'],
                        'total': buy_amount,
                        'buy_reason': buy_reason_text,
                        'buy_stage': stage,
                        'rsi_value': rsi_value,
                        'rsi_range': rsi_range,
                        'drop_percent': drop_percent,
                        'market_condition': 'bearish' if price_change_24h < -3 else 'bullish' if price_change_24h > 3 else 'neutral',
                        'price_change_24h': price_change_24h
                    }
                    
                    trading_db.record_trade(bot_state['current_session_id'], trade_data)
                    
                    # 실시간 표시용
                    bot_state['trade_reasons'].append({
                        'time': datetime.now().strftime("%H:%M:%S"),
                        'action': 'BUY',
                        'ticker': ticker.replace('KRW-', ''),
                        'reason': buy_reason_text,
                        'stage': stage
                    })
                    
                    log(f"✅ 매수 이유 기록 완료", "SUCCESS")
                except Exception as e:
                    log(f"⚠️  매수 기록 오류 (계속 진행): {e}", "WARNING")
            
        elif action == 'SELL':
            stage = strategy.get('sell_stage', 0)
            ratio = strategy.get('sell_ratio', 1.0)
            sell_amount = holding['amount'] * ratio
            
            # 매도 이유 생성
            sell_reasons = strategy.get('reason', [])
            sell_reason_text = " | ".join([f"{r[0]}: {r[1]}" for r in sell_reasons if r[0] == 'SELL'])
            
            log(f"🔴 매도: {ticker} {stage}차 익절 {ratio*100:.0f}%", "INFO")
            log(f"📝 이유: {sell_reason_text}", "REASON")
            
            # 모드에 따라 실제 주문 실행
            current_mode = bot_state.get('mode', 'practice')
            if current_mode == 'live':
                order = upbit.sell_market_order(ticker, sell_amount)
                log(f"✅ [실전 모드] 매도 주문 체결: {order}", "SUCCESS")
            else:
                log(f"⚠️  [연습 모드] 매도 시뮬레이션", "WARNING")
            
            profit = (holding['current_price'] - holding['avg_buy_price']) * sell_amount
            profit_rate = ((holding['current_price'] - holding['avg_buy_price']) / holding['avg_buy_price']) * 100
            
            history = coin_trading_history.get(ticker, {
                'sell_stages_completed': [],
                'total_profit': 0,
                'first_buy_price': holding['avg_buy_price'],
                'last_buy_time': datetime.now() - timedelta(hours=1)  # 임시
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
            
            # 📊 데이터베이스에 매도 기록 (학습용)
            if bot_state['current_session_id']:
                try:
                    # 보유 시간 계산
                    hold_time = 0
                    if history.get('last_buy_time'):
                        hold_time = int((datetime.now() - history['last_buy_time']).total_seconds())
                    
                    # 목표 수익률
                    target_profit = SELL_STAGES.get(stage, {}).get('profit_target', 0) if stage > 0 else 0
                    
                    # 성공 여부
                    is_successful = profit > 0
                    
                    # 배운 점
                    if is_successful:
                        if profit_rate >= target_profit:
                            lesson = f"목표 수익률 {target_profit}% 달성 성공 (실제: {profit_rate:.2f}%)"
                        else:
                            lesson = f"수익은 났지만 목표 미달성 ({profit_rate:.2f}% < {target_profit}%)"
                    else:
                        if stage == 0:
                            lesson = f"긴급 손절 발동 ({profit_rate:.2f}%) - 매수 타이밍 재검토 필요"
                        else:
                            lesson = f"익절 실패 ({profit_rate:.2f}%) - 전략 재검토 필요"
                    
                    # 24시간 가격 변동
                    price_change_24h = 0
                    try:
                        ticker_data = pyupbit.get_ohlcv(ticker, interval="day", count=2)
                        if ticker_data is not None and len(ticker_data) >= 2:
                            prev_close = ticker_data.iloc[-2]['close']
                            curr_close = ticker_data.iloc[-1]['close']
                            price_change_24h = ((curr_close - prev_close) / prev_close) * 100
                    except:
                        pass
                    
                    trade_data = {
                        'timestamp': datetime.now().isoformat(),
                        'trade_type': 'SELL',
                        'ticker': ticker,
                        'amount': sell_amount,
                        'price': holding['current_price'],
                        'total': holding['current_price'] * sell_amount,
                        'sell_reason': sell_reason_text,
                        'sell_stage': stage,
                        'profit': profit,
                        'profit_rate': profit_rate,
                        'hold_time': hold_time,
                        'target_profit': target_profit,
                        'is_successful': is_successful,
                        'lesson_learned': lesson,
                        'market_condition': 'bearish' if price_change_24h < -3 else 'bullish' if price_change_24h > 3 else 'neutral',
                        'price_change_24h': price_change_24h
                    }
                    
                    trading_db.record_trade(bot_state['current_session_id'], trade_data)
                    
                    # 실시간 표시용
                    profit_text = f"+{profit:,.0f}원 (+{profit_rate:.1f}%)" if profit > 0 else f"{profit:,.0f}원 ({profit_rate:.1f}%)"
                    bot_state['trade_reasons'].append({
                        'time': datetime.now().strftime("%H:%M:%S"),
                        'action': 'SELL',
                        'ticker': ticker.replace('KRW-', ''),
                        'reason': sell_reason_text,
                        'profit': profit_text,
                        'stage': stage,
                        'success': is_successful
                    })
                    
                    log(f"✅ 매도 이유 기록 완료 - {lesson}", "SUCCESS")
                except Exception as e:
                    log(f"⚠️  매도 기록 오류 (계속 진행): {e}", "WARNING")
            
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
    
    # 📊 학습 세션 시작
    session_id = f"{bot_state['mode']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    bot_state['current_session_id'] = session_id
    
    # 시드 결정 (연습/실전 모드)
    if bot_state['mode'] == 'practice':
        initial_seed = bot_state['simulation_seed']
        log(f"🎮 연습 모드: 시뮬레이션 시드 {initial_seed:,}원", "INFO")
    else:
        initial_seed = bot_state['initial_seed']
        log(f"🔴 실전 모드: 실제 시드 {initial_seed:,}원", "WARNING")
    
    # 전략 설정
    strategy_config = {
        'mode': bot_state['mode'],
        'buy_stages': BUY_STAGES,
        'sell_stages': SELL_STAGES,
        'profit_targets': PROFIT_TARGETS,
        'profit_invest_amount': PROFIT_INVEST_AMOUNT
    }
    
    # 데이터베이스에 세션 시작 기록
    trading_db.start_session(session_id, initial_seed, strategy_config)
    log(f"📊 학습 세션 시작: {session_id}", "SUCCESS")
    
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
    
    # 📊 학습 세션 종료
    if bot_state['current_session_id']:
        if bot_state['mode'] == 'practice':
            final_balance = bot_state['simulation_krw']
        else:
            final_balance = bot_state['current_krw']
        
        trading_db.end_session(bot_state['current_session_id'], final_balance)
        log(f"📊 학습 세션 종료: {bot_state['current_session_id']}", "SUCCESS")
        
        # 세션 결과 출력
        sessions = trading_db.get_session_history(1)
        if sessions:
            session = sessions[0]
            log_separator()
            log(f"📈 세션 결과:", "SUCCESS")
            log(f"  시작 시드: {session['initial_seed']:,}원", "INFO")
            log(f"  최종 잔고: {session['final_balance']:,}원", "INFO")
            log(f"  수익/손실: {session['profit']:,}원 ({session['profit_rate']:.2f}%)", 
                "SUCCESS" if session['profit'] >= 0 else "WARNING")
            log(f"  총 거래: {session['total_trades']}회", "INFO")
            log(f"  승률: {session['win_rate']:.1f}% ({session['win_trades']}승 {session['lose_trades']}패)", "INFO")
            log_separator()
    
    log("🛑 봇 종료", "WARNING")

# ═══════════════════════════════════════════════════════
# 🌐 Flask API 엔드포인트
# ═══════════════════════════════════════════════════════
@app.route('/')
def index():
    """메인 대시보드"""
    return render_template('dashboard-pro.html')

@app.route('/api/license/info')
def api_license_info():
    """라이선스 정보 조회"""
    license_data = bot_state.get('license', {})
    return jsonify({
        'status': license_data.get('status', 'none'),
        'days_left': license_data.get('days_left', 0),
        'expiry_date': license_data.get('expiry_date'),
        'wallet_address': LICENSE_CONFIG['usdt_address'],
        'price_per_day': LICENSE_CONFIG['price_per_day'],
        'min_amount': LICENSE_CONFIG['min_amount'],
        'network': LICENSE_CONFIG['network']
    })

@app.route('/api/license/verify', methods=['POST'])
def api_license_verify():
    """TXID 검증 및 라이선스 활성화"""
    data = request.get_json()
    txid = data.get('txid', '').strip()
    
    if not txid:
        return jsonify({'success': False, 'error': 'TXID를 입력해주세요'})
    
    # TXID 검증
    result = verify_txid(txid)
    
    if not result['success']:
        return jsonify(result)
    
    # 라이선스 저장
    license_data = save_license(txid, result['amount'], LICENSE_CONFIG['network'])
    
    if license_data:
        bot_state['license'] = license_data
        return jsonify({
            'success': True,
            'message': f'라이선스 활성화 완료! (기간: {license_data["days"]}일)',
            'license': license_data
        })
    else:
        return jsonify({'success': False, 'error': '라이선스 저장 실패'})

@app.route('/api/mode/switch', methods=['POST'])
def api_mode_switch():
    """모드 전환 (연습 ↔ 실전)"""
    data = request.get_json()
    new_mode = data.get('mode', 'practice')
    
    # 실전 모드로 전환 시 라이선스 확인
    if new_mode == 'live':
        license_data = bot_state.get('license', {})
        if license_data.get('status') != 'active':
            return jsonify({
                'success': False,
                'error': '실전 모드를 사용하려면 라이선스가 필요합니다'
            })
        
        # 만료 확인
        expiry_date = datetime.fromisoformat(license_data['expiry_date'])
        if datetime.now() > expiry_date:
            return jsonify({
                'success': False,
                'error': '라이선스가 만료되었습니다'
            })
    
    bot_state['mode'] = new_mode
    mode_name = '실전' if new_mode == 'live' else '연습'
    log(f"🔄 모드 전환: {mode_name} 모드", "INFO")
    
    return jsonify({
        'success': True,
        'mode': new_mode,
        'message': f'{mode_name} 모드로 전환되었습니다'
    })

@app.route('/api/status')
def api_status():
    """봇 상태 조회"""
    license_data = bot_state.get('license', {})
    return jsonify({
        'running': bot_state['running'],
        'mode': bot_state.get('mode', 'practice'),
        'initial_seed': bot_state['initial_seed'],
        'current_krw': bot_state['current_krw'],
        'total_profit': bot_state['total_profit'],
        'holdings': bot_state['holdings'],
        'profit_investments': bot_state['profit_investments'],
        'trade_history': bot_state['trade_history'][-20:],  # 최근 20개
        'last_update': bot_state['last_update'],
        'error': bot_state['error'],
        'license': {
            'status': license_data.get('status', 'none'),
            'days_left': license_data.get('days_left', 0),
            'expiry_date': license_data.get('expiry_date')
        }
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

@app.route('/api/simulation/set-seed', methods=['POST'])
def api_set_simulation_seed():
    """시뮬레이션 시드 설정"""
    if bot_state['running']:
        return jsonify({'success': False, 'message': '봇 실행 중에는 시드를 변경할 수 없습니다'})
    
    try:
        data = request.json
        seed = int(data.get('seed', 1000000))
        
        # 범위 체크: 20만원 ~ 1,000만원
        if seed < 200000 or seed > 10000000:
            return jsonify({
                'success': False,
                'message': '시드는 20만원에서 1,000만원 사이여야 합니다'
            })
        
        # 시뮬레이션 시드 설정
        bot_state['simulation_seed'] = seed
        bot_state['simulation_krw'] = seed
        bot_state['simulation_start_seed'] = seed
        bot_state['simulation_holdings'] = {}
        bot_state['trade_history'] = []
        bot_state['total_profit'] = 0
        
        return jsonify({
            'success': True,
            'message': f'시뮬레이션 시드 {seed:,}원으로 설정되었습니다',
            'seed': seed
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'오류 발생: {str(e)}'
        })

@app.route('/api/simulation/status', methods=['GET'])
def api_simulation_status():
    """시뮬레이션 상태 조회"""
    # 보유 코인 평가액 계산
    total_holding_value = 0
    holdings_list = []
    
    for ticker, holding in bot_state['simulation_holdings'].items():
        try:
            current_price = pyupbit.get_current_price(ticker)
            if current_price:
                value = holding['amount'] * current_price
                total_holding_value += value
                profit = value - (holding['amount'] * holding['avg_price'])
                profit_rate = (profit / (holding['amount'] * holding['avg_price'])) * 100
                
                holdings_list.append({
                    'ticker': ticker,
                    'amount': holding['amount'],
                    'avg_price': holding['avg_price'],
                    'current_price': current_price,
                    'value': value,
                    'profit': profit,
                    'profit_rate': profit_rate
                })
        except:
            pass
    
    # 총 자산
    total_assets = bot_state['simulation_krw'] + total_holding_value
    
    # 총 수익/손실
    total_profit = total_assets - bot_state['simulation_start_seed']
    profit_rate = (total_profit / bot_state['simulation_start_seed']) * 100 if bot_state['simulation_start_seed'] > 0 else 0
    
    return jsonify({
        'success': True,
        'simulation': {
            'start_seed': bot_state['simulation_start_seed'],
            'current_krw': bot_state['simulation_krw'],
            'holdings': holdings_list,
            'total_holding_value': total_holding_value,
            'total_assets': total_assets,
            'total_profit': total_profit,
            'profit_rate': profit_rate
        }
    })

@app.route('/api/learning/history', methods=['GET'])
def api_learning_history():
    """학습 히스토리 조회"""
    try:
        limit = int(request.args.get('limit', 10))
        sessions = trading_db.get_session_history(limit)
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/learning/session/<session_id>', methods=['GET'])
def api_session_details(session_id):
    """특정 세션의 상세 거래 내역"""
    try:
        trades = trading_db.get_trades_by_session(session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'trades': trades,
            'total': len(trades)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/learning/analysis/buy-reasons', methods=['GET'])
def api_analyze_buy_reasons():
    """매수 이유별 성공률 분석"""
    try:
        analysis = trading_db.analyze_buy_reasons()
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/learning/analysis/rsi', methods=['GET'])
def api_analyze_rsi():
    """RSI 범위별 효과 분석"""
    try:
        analysis = trading_db.analyze_rsi_effectiveness()
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/learning/best-conditions', methods=['GET'])
def api_best_conditions():
    """최적 거래 조건 찾기"""
    try:
        min_samples = int(request.args.get('min_samples', 10))
        conditions = trading_db.get_best_performing_conditions(min_samples)
        
        return jsonify({
            'success': True,
            'conditions': conditions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/learning/trade-reasons', methods=['GET'])
def api_trade_reasons():
    """실시간 거래 이유 조회"""
    return jsonify({
        'success': True,
        'reasons': bot_state['trade_reasons'][-20:]  # 최근 20개
    })

# ═══════════════════════════════════════════════════════
# 🚀 메인 실행
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"""
{Colors.BOLD}{Colors.CYAN}
  🤖 업비트 스마트 스캘핑 봇 v6.0
  🌐 웹 대시보드 + 라이선스 시스템
  💰 연습 모드 / 실전 모드 지원
{Colors.END}
""")
    
    # 라이선스 로드
    bot_state['license'] = load_license()
    
    print(f"{Colors.GREEN}🌐 웹 대시보드: http://localhost:5000{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  브라우저에서 접속하세요{Colors.END}\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
