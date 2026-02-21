#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 업비트 AI 트레이딩 봇 v8.0 - ULTIMATE EDITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 완전체: 모든 기능 통합 최종판

🔥 핵심 기능:
1. 📊 5가지 패턴 자동 인식
   - 박스권, 상승추세, 하락추세, 급등후, 수급 유입/이탈
   
2. 🏆 멀티 전략 경쟁 시스템
   - 급등 포착 (Surge Hunter)
   - 급락 저점 매수 (Dip Hunter - 원가 복귀)
   - 박스권 하단 매수 (Box Trader)
   - 추세 추종 (Trend Follower)
   - 수급 기반 (Volume Hunter)
   
3. 🧠 AI 자동 학습
   - 매 거래마다 성과 기록
   - 전략별 가중치 자동 조정
   - 50개 거래마다 재학습
   
4. 🛡️ 손실 복구 모드
   - -15% 손실 시 자동 활성화
   - 10% 시드로 초단타
   - 기존 코인 동결 (반등 대기)
   
5. ⚙️ 시각적 피드백
   - 로딩 스피너
   - 실시간 상태 표시
   - 전략 경쟁 현황 대시보드

🎯 최종 목표: 월 25%+ 수익, 승률 75%+, 손실 자동 복구
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import os
import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
import threading
from flask import Flask, render_template, jsonify, request, make_response, session, redirect
from flask_cors import CORS
import traceback
import os
import sqlite3
import hashlib
from werkzeug.security import generate_password_hash

# 커스텀 모듈
from user_manager import UserManager
from portfolio_manager import execute_diversified_buy, check_profit_trigger, get_available_coins
from trade_reasons import generate_buy_reason, generate_sell_reason
from recovery_system import analyze_current_holdings, create_recovery_plan, execute_recovery_plan, UPBIT_FEE_RATE
from bot_state_manager import init_bot_state_table, save_bot_state, load_bot_state, get_all_running_bots
from enhanced_emei_learning import get_enhanced_emei
from emei_response_router import EmeiRouter

# ═══════════════════════════════════════════════════════
# ⚙️ 전체 설정
# ═══════════════════════════════════════════════════════

# ✅ .env 파일 수동 로드 (python-dotenv 없이)
def load_env_file(env_path=".env"):
    """수동으로 .env 파일 로드"""
    if not os.path.exists(env_path):
        return
    
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value
                print(f"✅ 환경변수 로드: {key}={value}")

# .env 파일 로드
load_env_file("/home/user/webapp/.env")

# 🧠 이메이 Router 초기화
DB_PATH = "/home/user/webapp/upbit_bot.db"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
print(f"🔧 Ollama 설정: URL={OLLAMA_URL}, Model={OLLAMA_MODEL}")
emei_router = EmeiRouter(DB_PATH, OLLAMA_URL, OLLAMA_MODEL)

# 급등/급락 감지 (🔥 더 공격적으로 완화 - 거래 기회 대폭 증가)
SURGE_CONFIG = {
    # 급등 (매우 완화)
    'surge_threshold_1m': 0.3,  # 0.8 -> 0.3 (1분에 0.3% 급등)
    'surge_threshold_3m': 0.8,  # 1.5 -> 0.8 (3분에 0.8% 급등)
    
    # 급락 (매우 완화)
    'dip_threshold_1m': -0.3,   # -0.8 -> -0.3 (더 작은 급락도 포착)
    'dip_oversold_rsi': 50,     # 40 -> 50 (과매도 기준 매우 완화)
    'dip_volume_spike': 1.2,    # 1.5 -> 1.2 (거래량 기준 완화)
    
    # 복귀 전략
    'dip_recovery_threshold': -0.2,  # -0.3 -> -0.2 (복귀 기준 완화)
    'dip_max_hold_time': 24 * 60,
    'dip_emergency_stop': -10.0,
    
    # 거래량 (더 완화)
    'volume_spike_ratio': 1.1,      # 1.2 -> 1.1
    'min_volume_krw': 5000000,      # 10M -> 5M (5백만원)
    
    # 익절/손절
    'take_profit_targets': [0.5, 1.0, 1.5],
    'stop_loss': -2.0,
}

# 패턴 분석 (🔥 더 공격적으로 완화 - 실제 매매 활성화)
PATTERN_CONFIG = {
    'box_range_threshold': 0.3,      # 0.5 -> 0.3 (박스권 매우 쉽게 인식)
    'trend_ma_short': 3,
    'trend_ma_long': 10,
    'uptrend_threshold': 0.1,        # 0.2 -> 0.1 (상승 추세 매우 쉽게 인식)
    'volume_surge_ratio': 1.05,      # 1.1 -> 1.05 (거래량 거의 모든 경우 감지)
}

# AI 학습
LEARNING_CONFIG = {
    'enable_learning': True,
    'learning_interval': 50,
    'pattern_history_size': 500,
}

# 손실 복구
RECOVERY_CONFIG = {
    'enable_recovery_mode': True,
    'activate_loss_threshold': -15.0,
    'recovery_cash_ratio': 0.10,
    'recovery_target_profit': 1.5,
    'recovery_stop_loss': -1.0,
    'recovery_max_hold_time': 30,
    'recovery_target_rate': 0.5,
}

# ═══════════════════════════════════════════════════════
# 🏆 전략 정의
# ═══════════════════════════════════════════════════════
STRATEGIES = {
    'surge_hunter': {
        'name': '급등 포착',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'dip_hunter': {
        'name': '급락 저점 → 원가 복귀',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'box_trader': {
        'name': '박스권 매매',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'trend_follower': {
        'name': '추세 추종',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'volume_hunter': {
        'name': '수급 기반',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'gap_down_reversal': {
        'name': 'BNF 급락 반등',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'squeeze_momentum': {
        'name': '압축 모멘텀',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'ema_squeeze': {
        'name': '200/20 이평선 스퀴즈',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'testa_3sma': {
        'name': '테스타 3중 이평선',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'rsi_reversal': {
        'name': 'RSI 필터 반전',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'volume_breakout_v2': {
        'name': '거래량 돌파',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'mach7_pullback': {
        'name': '마하7 이평선 눌림목',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    }
}

# ═══════════════════════════════════════════════════════
# 🎮 봇 상태 관리
# ═══════════════════════════════════════════════════════

def create_bot_state():
    """사용자별 독립 봇 상태 생성"""
    return {
        'running': False,
        'mode': 'practice',
        'upbit': None,
        'thread': None,
        
        # 시뮬레이션
        'simulation_seed': 1000000,
        'simulation_krw': 1000000,
        'simulation_holdings': {},
        'simulation_start_seed': 1000000,
        
        # 복구 모드
        'recovery_mode_active': False,
        'recovery_seed': 0,
        'recovery_target_amount': 0,
        'recovery_trades': 0,
        'recovery_success_trades': 0,
        'recovery_total_profit': 0,
        'frozen_holdings': {},
        'last_loss_time': None,
        
        # 학습
        'pattern_history': deque(maxlen=LEARNING_CONFIG['pattern_history_size']),
        'trade_results': deque(maxlen=LEARNING_CONFIG['pattern_history_size']),
        'strategy_performance': {k: v.copy() for k, v in STRATEGIES.items()},
        'current_patterns': {},
        
        # 통계
        'statistics': {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'best_strategy': None,
            'recovery_progress': 0,
        },
        
        # 거래 내역 (최근 50개)
        'recent_trades': deque(maxlen=50),
        'recent_signals': deque(maxlen=50),
        
        'user_id': None,  # 사용자 ID 추가
        'last_update': None,
        'start_time': None,
    }

# 전역 봇 상태 (하위 호환성 유지)
bot_state = create_bot_state()

def get_user_bot_state(user_id):
    """사용자 ID로 봇 상태 조회 또는 생성"""
    if user_id not in user_bots:
        user_bots[user_id] = create_bot_state()
        user_bots[user_id]['user_id'] = user_id  # user_id 설정
    return user_bots[user_id]

# ═══════════════════════════════════════════════════════
# 📝 로깅
# ═══════════════════════════════════════════════════════
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "SUCCESS": "\033[92m", "ERROR": "\033[91m", "WARNING": "\033[93m",
        "INFO": "\033[96m", "PATTERN": "\033[95m", "LEARN": "\033[94m",
        "RECOVERY": "\033[95m", "URGENT": "\033[91m\033[1m"
    }
    color = colors.get(level, "\033[0m")
    print(f"{color}[{timestamp}] {level}: {message}\033[0m")

def log_separator():
    print("\n" + "="*80 + "\n")

# ═══════════════════════════════════════════════════════
# 💾 거래 히스토리 DB 저장
# ═══════════════════════════════════════════════════════
def save_trade_to_db(user_id, trade_data):
    """거래 내역을 DB에 영구 저장"""
    try:
        import sqlite3
        import json
        
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        # trades 테이블이 없으면 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                ticker TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                amount REAL,
                price REAL,
                invested REAL,
                fee REAL,
                net_invested REAL,
                entry_price REAL,
                sell_value REAL,
                net_proceeds REAL,
                profit REAL,
                profit_rate REAL,
                strategy TEXT,
                reason TEXT,
                mode TEXT,
                patterns TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인덱스 생성 (검색 속도 향상)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trade_user_time 
            ON trade_history(user_id, timestamp DESC)
        ''')
        
        # 데이터 삽입
        cursor.execute('''
            INSERT INTO trade_history (
                user_id, ticker, trade_type, amount, price,
                invested, fee, net_invested, entry_price, sell_value,
                net_proceeds, profit, profit_rate, strategy, reason,
                mode, patterns, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            trade_data.get('ticker'),
            trade_data.get('type'),
            trade_data.get('amount'),
            trade_data.get('price'),
            trade_data.get('invested', 0),
            trade_data.get('fee', 0),
            trade_data.get('net_invested', 0),
            trade_data.get('entry_price', 0),
            trade_data.get('sell_value', 0),
            trade_data.get('net_proceeds', 0),
            trade_data.get('profit', 0),
            trade_data.get('profit_rate', 0),
            trade_data.get('strategy', ''),
            trade_data.get('reason', ''),
            trade_data.get('mode', 'practice'),
            json.dumps(trade_data.get('patterns', []), ensure_ascii=False),
            trade_data.get('timestamp')
        ))
        
        conn.commit()
        conn.close()
        
        log(f"[DB] 거래 저장: {user_id} | {trade_data.get('type')} | {trade_data.get('ticker')}", "INFO")
        return True
    except Exception as e:
        log(f"거래 DB 저장 오류: {e}", "ERROR")
        return False

def save_bot_state_to_db(user_id, bot_state):
    """봇 상태를 DB에 저장 (simulation_holdings, simulation_krw 등)"""
    try:
        import sqlite3
        import json
        
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        # simulation_holdings를 JSON으로 변환
        holdings_json = json.dumps(bot_state.get('simulation_holdings', {}), ensure_ascii=False, default=str)
        
        # bot_states 업데이트
        cursor.execute("""
            UPDATE bot_states
            SET 
                simulation_krw = ?,
                simulation_holdings = ?,
                recovery_mode_active = ?,
                last_update = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (
            bot_state.get('simulation_krw', 0),
            holdings_json,
            bot_state.get('recovery_mode_active', False),
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        log(f"봇 상태 DB 저장 오류: {e}", "ERROR")
        return False

def append_trade_to_csv(user_id, trade_data, holding_info=None):
    """거래 내역을 imei_os/TRADING_LOG.csv에 기록"""
    try:
        import csv
        from pathlib import Path
        
        csv_path = Path('imei_os/TRADING_LOG.csv')
        csv_path.parent.mkdir(exist_ok=True)
        
        # 첫 진입 시 헤더 확인/생성
        if not csv_path.exists() or csv_path.stat().st_size == 0:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'user_id', 'ticker', 'action', 'strategy',
                    'amount', 'entry_price', 'exit_price', 'profit_rate',
                    'hold_time_seconds', 'reason', 'detected_patterns'
                ])
        
        # 거래 데이터 추출
        action = trade_data.get('type', 'UNKNOWN')  # BUY or SELL
        ticker = trade_data.get('ticker', '')
        strategy = trade_data.get('strategy', '')
        amount = trade_data.get('amount', 0)
        price = trade_data.get('price', 0)
        reason = trade_data.get('reason', '')
        timestamp = trade_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 패턴 정보 (BUY 시)
        patterns_str = ''
        if action == 'BUY' and trade_data.get('patterns'):
            patterns_list = trade_data.get('patterns', [])
            if isinstance(patterns_list, list):
                patterns_str = '|'.join(patterns_list)
            else:
                patterns_str = str(patterns_list)
        
        # SELL 시 추가 정보
        entry_price = trade_data.get('entry_price', '') if action == 'SELL' else price
        exit_price = price if action == 'SELL' else ''
        profit_rate = trade_data.get('profit_rate', '') if action == 'SELL' else ''
        hold_time_seconds = int(trade_data.get('hold_time', 0) * 60) if action == 'SELL' else ''
        
        # CSV 라인 추가
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, user_id, ticker, action, strategy,
                amount, entry_price, exit_price, profit_rate,
                hold_time_seconds, reason, patterns_str
            ])
        
        log(f"[CSV] 거래 기록: {user_id} | {action} | {ticker}", "INFO")
        return True
    except Exception as e:
        log(f"CSV 로그 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

# ═══════════════════════════════════════════════════════
# 📊 기술적 지표 계산
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

def calculate_volume_spike(df):
    """거래량 급증 계산"""
    try:
        if len(df) < 10:
            return 1.0
        avg_volume = df['volume'].iloc[-10:-1].mean()
        current_volume = df['volume'].iloc[-1]
        return (current_volume / avg_volume) if avg_volume > 0 else 1.0
    except:
        return 1.0

def calculate_ema(df, period=25):
    """EMA 계산"""
    try:
        return df['close'].ewm(span=period, adjust=False).mean().iloc[-1]
    except:
        return df['close'].iloc[-1]

def calculate_macd(df):
    """MACD 계산 (12, 26, 9)"""
    try:
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1],
            'prev_histogram': histogram.iloc[-2] if len(histogram) > 1 else 0
        }
    except:
        return {'macd': 0, 'signal': 0, 'histogram': 0, 'prev_histogram': 0}

def calculate_bollinger_keltner(df, bb_period=20, kc_period=20):
    """Bollinger Bands와 Keltner Channels 계산 (Squeeze Momentum용)"""
    try:
        # Bollinger Bands
        sma = df['close'].rolling(window=bb_period).mean()
        std = df['close'].rolling(window=bb_period).std()
        bb_upper = sma + (std * 2)
        bb_lower = sma - (std * 2)
        
        # Keltner Channels (ATR 기반)
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=kc_period).mean()
        
        kc_middle = df['close'].rolling(window=kc_period).mean()
        kc_upper = kc_middle + (atr * 1.5)
        kc_lower = kc_middle - (atr * 1.5)
        
        # Squeeze 감지 (BB가 KC 안에 있을 때)
        squeeze_on = (bb_lower.iloc[-1] > kc_lower.iloc[-1]) and (bb_upper.iloc[-1] < kc_upper.iloc[-1])
        
        # Momentum 계산
        highest = df['high'].rolling(window=kc_period).max()
        lowest = df['low'].rolling(window=kc_period).min()
        avg_hl = (highest + lowest) / 2
        momentum = df['close'] - avg_hl
        
        return {
            'squeeze_on': squeeze_on,
            'momentum': momentum.iloc[-1],
            'prev_momentum': momentum.iloc[-2] if len(momentum) > 1 else 0
        }
    except:
        return {'squeeze_on': False, 'momentum': 0, 'prev_momentum': 0}

# ═══════════════════════════════════════════════════════
# 🚀 급등 감지
# ═══════════════════════════════════════════════════════
def detect_surge_signal(ticker):
    """급등 신호 감지"""
    try:
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
        if df_1m is None or len(df_1m) < 10:
            return None
        
        price_before = df_1m['close'].iloc[-2]
        price_now = df_1m['close'].iloc[-1]
        change_1m = ((price_now - price_before) / price_before) * 100
        vol_spike = calculate_volume_spike(df_1m)
        
        if change_1m >= SURGE_CONFIG['surge_threshold_1m'] and vol_spike >= SURGE_CONFIG['volume_spike_ratio']:
            return {
                'type': 'SURGE',
                'ticker': ticker,
                'current_price': price_now,
                'change_pct': change_1m,
                'vol_spike': vol_spike,
                'signals': [f'급등 +{change_1m:.2f}%', f'거래량 {vol_spike:.1f}배'],
                'score': 5
            }
        
        return None
    except:
        return None

# ═══════════════════════════════════════════════════════
# 📉 급락 감지
# ═══════════════════════════════════════════════════════
def detect_dip_signal(ticker):
    """급락 신호 감지 - 원가 복귀 전략"""
    try:
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
        if df_1m is None or len(df_1m) < 15:
            return None
        
        # 급락 전 평균가
        price_before_dip = df_1m['close'].iloc[-12:-2].mean()
        price_now = df_1m['close'].iloc[-1]
        price_prev = df_1m['close'].iloc[-2]
        
        change_1m = ((price_now - price_prev) / price_prev) * 100
        dip_from_peak = ((price_now - price_before_dip) / price_before_dip) * 100
        
        vol_spike = calculate_volume_spike(df_1m)
        rsi = calculate_rsi(df_1m)
        
        score = 0
        signals = []
        
        if change_1m <= SURGE_CONFIG['dip_threshold_1m']:
            score += 3
            signals.append(f'급락 {change_1m:.2f}%')
        
        if vol_spike >= SURGE_CONFIG['dip_volume_spike']:
            score += 2
            signals.append(f'거래량 {vol_spike:.1f}배')
        
        if rsi <= SURGE_CONFIG['dip_oversold_rsi']:
            score += 2
            signals.append(f'RSI {rsi:.1f}')
        
        if dip_from_peak <= -3.0:
            score += 2
            signals.append(f'피크대비 {dip_from_peak:.2f}%')
        
        if score >= 5:
            return {
                'type': 'DIP',
                'ticker': ticker,
                'current_price': price_now,
                'price_before_dip': price_before_dip,
                'change_1m': change_1m,
                'dip_from_peak': dip_from_peak,
                'vol_spike': vol_spike,
                'rsi': rsi,
                'signals': signals,
                'score': score
            }
        
        return None
    except:
        return None

# ═══════════════════════════════════════════════════════
# 📊 패턴 분석
# ═══════════════════════════════════════════════════════
def detect_box_range(ticker):
    """박스권 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=50)
        if df is None or len(df) < 30:
            return None
        
        recent_high = df['high'].iloc[-6:].max()
        recent_low = df['low'].iloc[-6:].min()
        range_pct = ((recent_high - recent_low) / recent_low) * 100
        
        if range_pct <= PATTERN_CONFIG['box_range_threshold']:
            current_price = df['close'].iloc[-1]
            box_position = (current_price - recent_low) / (recent_high - recent_low)
            
            return {
                'type': 'BOX_RANGE',
                'high': recent_high,
                'low': recent_low,
                'position': box_position,
                'confidence': 1.0 - (range_pct / PATTERN_CONFIG['box_range_threshold']),
                'action': 'BUY' if box_position < 0.3 else 'SELL' if box_position > 0.7 else 'HOLD'
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
        
        ma_short = df['close'].rolling(window=PATTERN_CONFIG['trend_ma_short']).mean()
        ma_long = df['close'].rolling(window=PATTERN_CONFIG['trend_ma_long']).mean()
        
        ma_short_now = ma_short.iloc[-1]
        ma_long_now = ma_long.iloc[-1]
        trend_strength = ((ma_short_now - ma_long_now) / ma_long_now) * 100
        
        if trend_strength >= PATTERN_CONFIG['uptrend_threshold']:
            return {
                'type': 'UPTREND',
                'strength': trend_strength,
                'confidence': min(trend_strength / 5.0, 1.0),
                'action': 'BUY'
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
        
        if vol_ratio >= PATTERN_CONFIG['volume_surge_ratio']:
            price_change = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            return {
                'type': 'VOLUME_SURGE',
                'ratio': vol_ratio,
                'price_change': price_change,
                'confidence': min(vol_ratio / 5.0, 1.0),
                'action': 'BUY' if price_change > 0 else 'WATCH'
            }
        return None
    except:
        return None

def detect_gap_down_reversal(ticker):
    """BNF Gap-Down Mean Reversion 전략 (급락 후 반등)"""
    try:
        # 1시간봉 데이터 (25개 필요)
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count=30)
        if df is None or len(df) < 26:
            return None
        
        current_price = df['close'].iloc[-1]
        ema_25 = calculate_ema(df, 25)
        
        # 1. Disparity 계산 (가격이 EMA보다 얼마나 떨어졌는지)
        disparity = ((current_price - ema_25) / ema_25) * 100
        
        # 2. 20% 이상 급락 조건 (암호화폐는 25%로 조정)
        if disparity > -25:
            return None
        
        # 3. RSI 과매도 확인
        rsi = calculate_rsi(df)
        if rsi > 30:
            return None
        
        # 4. MACD 반전 확인
        macd_data = calculate_macd(df)
        macd_reversal = (macd_data['prev_histogram'] < 0 and macd_data['histogram'] > 0)
        
        if macd_reversal:
            return {
                'type': 'GAP_DOWN_REVERSAL',
                'disparity': disparity,
                'rsi': rsi,
                'ema_25': ema_25,
                'macd_histogram': macd_data['histogram'],
                'confidence': min(abs(disparity) / 25.0, 1.0),
                'action': 'BUY',
                'stop_loss_price': df['low'].iloc[-5:].min(),  # 최근 5개 저점
                'target_price': current_price * 1.15  # 15% 목표 (1:3 위험 보상)
            }
        return None
    except Exception as e:
        log(f"Gap-Down 감지 오류: {e}", "ERROR")
        return None

def detect_squeeze_momentum(ticker):
    """Squeeze Momentum 전략 (4시간봉 모멘텀 추세)"""
    try:
        # 4시간봉 데이터
        df = pyupbit.get_ohlcv(ticker, interval="minute240", count=30)
        if df is None or len(df) < 25:
            return None
        
        # Bollinger Bands + Keltner Channels + Momentum
        squeeze_data = calculate_bollinger_keltner(df)
        
        # Momentum 방향 전환 감지 (빨강→초록)
        momentum_now = squeeze_data['momentum']
        momentum_prev = squeeze_data['prev_momentum']
        
        # 양수 모멘텀으로 전환 (상승 신호)
        if momentum_prev < 0 and momentum_now > 0:
            return {
                'type': 'SQUEEZE_MOMENTUM',
                'momentum': momentum_now,
                'squeeze_on': squeeze_data['squeeze_on'],
                'confidence': min(abs(momentum_now) / 1000, 1.0),
                'action': 'BUY',
                'exit_condition': 'momentum_turns_negative'
            }
        
        # 음수 모멘텀으로 전환 (하락 신호 - 청산용)
        if momentum_prev > 0 and momentum_now < 0:
            return {
                'type': 'SQUEEZE_MOMENTUM_EXIT',
                'momentum': momentum_now,
                'action': 'SELL'
            }
        
        return None
    except Exception as e:
        log(f"Squeeze Momentum 감지 오류: {e}", "ERROR")
        return None

def detect_ema_squeeze(ticker):
    """200/20 EMA Squeeze 전략 - SMA(200)과 SMA(20)의 스퀴즈 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute15", count=220)
        if df is None or len(df) < 220:
            return None
        
        df['sma_200'] = df['close'].rolling(window=200).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        
        current_price = df['close'].iloc[-1]
        sma_200 = df['sma_200'].iloc[-1]
        sma_20 = df['sma_20'].iloc[-1]
        
        # 조건 1: 가격이 SMA(200) 위 + SMA(200) 상승 중
        if current_price < sma_200 or pd.isna(sma_200):
            return None
        if df['sma_200'].iloc[-1] <= df['sma_200'].iloc[-10]:
            return None
        
        # 조건 2: SMA(20)이 SMA(200)에 근접 (5% 이내)
        squeeze_ratio = abs(sma_20 - sma_200) / sma_200
        if squeeze_ratio > 0.05:
            return None
        
        # 조건 3: 최근 캔들이 긴 양봉으로 SMA(20) 돌파
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        body_size = abs(last_candle['close'] - last_candle['open'])
        candle_range = last_candle['high'] - last_candle['low']
        
        if candle_range == 0 or body_size / candle_range < 0.6:
            return None
        
        if last_candle['close'] <= last_candle['open']:
            return None
        
        if prev_candle['close'] < sma_20 and last_candle['close'] > sma_20:
            return {
                'type': 'EMA_SQUEEZE',
                'confidence': 0.85,
                'sma_200': sma_200,
                'sma_20': sma_20,
                'squeeze_ratio': squeeze_ratio,
                'action': 'BUY'
            }
        
        return None
    except Exception as e:
        log(f"EMA Squeeze 감지 오류: {e}", "ERROR")
        return None

def detect_testa_3sma(ticker):
    """테스타의 3중 이평선 정배열 전략"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=80)
        if df is None or len(df) < 80:
            return None
        
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_25'] = df['close'].rolling(window=25).mean()
        df['sma_75'] = df['close'].rolling(window=75).mean()
        
        current_price = df['close'].iloc[-1]
        sma_5 = df['sma_5'].iloc[-1]
        sma_25 = df['sma_25'].iloc[-1]
        sma_75 = df['sma_75'].iloc[-1]
        
        if pd.isna(sma_5) or pd.isna(sma_25) or pd.isna(sma_75):
            return None
        
        # 조건 1: SMA(75) 상승 중
        if df['sma_75'].iloc[-1] <= df['sma_75'].iloc[-10]:
            return None
        
        # 조건 2: 정배열 (SMA(25) > SMA(75))
        if sma_25 <= sma_75:
            return None
        
        # 조건 3: 양봉이 SMA(5) 돌파 + 거래량 증가
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        avg_volume = df['volume'].iloc[-10:-1].mean()
        if avg_volume == 0:
            return None
        
        volume_ratio = last_candle['volume'] / avg_volume
        
        if volume_ratio < 1.2:
            return None
        
        if last_candle['close'] <= last_candle['open']:
            return None
        
        if prev_candle['close'] < sma_5 and last_candle['close'] > sma_5:
            return {
                'type': 'TESTA_3SMA',
                'confidence': 0.9,
                'sma_5': sma_5,
                'sma_25': sma_25,
                'sma_75': sma_75,
                'volume_ratio': volume_ratio,
                'entry_candle_low': last_candle['low'],
                'action': 'BUY'
            }
        
        return None
    except Exception as e:
        log(f"Testa 3SMA 감지 오류: {e}", "ERROR")
        return None

def detect_rsi_reversal(ticker):
    """RSI 필터 + 볼린저 밴드 + Engulfing 패턴 (Ross Cameron)"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute15", count=30)
        if df is None or len(df) < 30:
            return None
        
        # RSI 계산
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 볼린저 밴드 계산
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        current_rsi = df['rsi'].iloc[-1]
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        if pd.isna(current_rsi) or pd.isna(df['bb_lower'].iloc[-1]):
            return None
        
        # 조건 1: RSI < 30 (과매도)
        if current_rsi >= 30:
            return None
        
        # 조건 2: 가격이 볼린저 하단 터치
        if last_candle['low'] > df['bb_lower'].iloc[-1]:
            return None
        
        # 조건 3: Bullish Engulfing 패턴
        is_engulfing = (
            prev_candle['close'] < prev_candle['open'] and
            last_candle['close'] > last_candle['open'] and
            last_candle['close'] > prev_candle['open'] and
            last_candle['open'] < prev_candle['close']
        )
        
        if is_engulfing:
            return {
                'type': 'RSI_REVERSAL',
                'confidence': 0.88,
                'rsi': current_rsi,
                'bb_lower': df['bb_lower'].iloc[-1],
                'bb_upper': df['bb_upper'].iloc[-1],
                'pattern': 'Bullish Engulfing',
                'action': 'BUY'
            }
        
        return None
    except Exception as e:
        log(f"RSI Reversal 감지 오류: {e}", "ERROR")
        return None

def detect_volume_breakout_v2(ticker):
    """거래량 감소 → 급증 + 고점 돌파"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=30)
        if df is None or len(df) < 30:
            return None
        
        # 거래량 감소 → 급증 패턴
        volume_avg = df['volume'].iloc[-10:-2].mean()
        prev_volume = df['volume'].iloc[-2]
        current_volume = df['volume'].iloc[-1]
        
        if volume_avg == 0:
            return None
        
        # 조건 1: 이전 거래량이 평균보다 감소
        if prev_volume > volume_avg * 0.8:
            return None
        
        # 조건 2: 현재 거래량이 급증 (평균의 150% 이상)
        if current_volume < volume_avg * 1.5:
            return None
        
        # 조건 3: 현재 캔들이 이전 캔들의 고점 돌파
        if df['close'].iloc[-1] <= df['high'].iloc[-2]:
            return None
        
        # 조건 4: 양봉이어야 함
        if df['close'].iloc[-1] <= df['open'].iloc[-1]:
            return None
        
        return {
            'type': 'VOLUME_BREAKOUT_V2',
            'confidence': 0.82,
            'volume_ratio': current_volume / volume_avg,
            'breakout_price': df['high'].iloc[-2],
            'action': 'BUY'
        }
    except Exception as e:
        log(f"Volume Breakout V2 감지 오류: {e}", "ERROR")
        return None

def detect_mach7_pullback(ticker):
    """마하7의 이평선 눌림목 스캘핑 (1분봉)"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=120)
        if df is None or len(df) < 120:
            return None
        
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_100'] = df['close'].ewm(span=100, adjust=False).mean()
        
        current_price = df['close'].iloc[-1]
        ema_20 = df['ema_20'].iloc[-1]
        ema_50 = df['ema_50'].iloc[-1]
        ema_100 = df['ema_100'].iloc[-1]
        
        if pd.isna(ema_20) or pd.isna(ema_50) or pd.isna(ema_100):
            return None
        
        # 조건 1: 정배열 (EMA(20) > EMA(50) > EMA(100))
        if not (ema_20 > ema_50 > ema_100):
            return None
        
        # 조건 2: 가격이 EMA(100) 위에 있음
        if current_price < ema_100:
            return None
        
        # 조건 3: 눌림목 (이전에 EMA(20) 아래로 내려갔다가 다시 위로)
        prev_price = df['close'].iloc[-2]
        if prev_price >= ema_20:
            return None
        
        if current_price <= ema_20:
            return None
        
        # 조건 4: Williams Fractal 시뮬레이션 (최근 7개 캔들 중 최저점)
        recent_lows = df['low'].iloc[-7:]
        is_fractal = df['low'].iloc[-4] == recent_lows.min()
        
        if is_fractal:
            return {
                'type': 'MACH7_PULLBACK',
                'confidence': 0.92,
                'ema_20': ema_20,
                'ema_50': ema_50,
                'ema_100': ema_100,
                'stop_loss': ema_50,
                'action': 'BUY'
            }
        
        return None
    except Exception as e:
        log(f"Mach7 Pullback 감지 오류: {e}", "ERROR")
        return None

def analyze_all_patterns(ticker):
    """모든 패턴 종합 분석"""
    patterns = {}
    
    # 급등/급락 우선
    surge = detect_surge_signal(ticker)
    if surge:
        patterns['surge'] = surge
    
    dip = detect_dip_signal(ticker)
    if dip:
        patterns['dip'] = dip
    
    # 새로운 전략들
    gap_down = detect_gap_down_reversal(ticker)
    if gap_down:
        patterns['gap_down'] = gap_down
    
    squeeze = detect_squeeze_momentum(ticker)
    if squeeze:
        patterns['squeeze'] = squeeze
    
    # 기타 패턴
    box = detect_box_range(ticker)
    if box:
        patterns['box'] = box
    
    trend = detect_trend(ticker)
    if trend:
        patterns['trend'] = trend
    
    volume = detect_volume_pattern(ticker)
    if volume:
        patterns['volume'] = volume
    
    # v10.24 신규 전략들
    ema_squeeze = detect_ema_squeeze(ticker)
    if ema_squeeze:
        patterns['ema_squeeze'] = ema_squeeze
    
    testa = detect_testa_3sma(ticker)
    if testa:
        patterns['testa'] = testa
    
    rsi_rev = detect_rsi_reversal(ticker)
    if rsi_rev:
        patterns['rsi_reversal'] = rsi_rev
    
    vol_break = detect_volume_breakout_v2(ticker)
    if vol_break:
        patterns['volume_breakout_v2'] = vol_break
    
    mach7 = detect_mach7_pullback(ticker)
    if mach7:
        patterns['mach7'] = mach7
    
    return patterns

# ═══════════════════════════════════════════════════════
# 🏆 전략 선택
# ═══════════════════════════════════════════════════════
def select_best_strategy(ticker, patterns):
    """최적 전략 선택"""
    strategy_scores = {}
    
    for strategy_id, strategy in bot_state['strategy_performance'].items():
        if not strategy['enabled']:
            continue
        
        score = 0.0
        perf = strategy['performance']
        
        # 과거 성과
        if perf['trades'] > 0:
            win_rate = perf['wins'] / perf['trades']
            avg_profit = perf['total_profit'] / perf['trades']
            score += (win_rate * avg_profit * strategy['weight']) * 0.5
        
        # 패턴 매칭
        if 'surge' in patterns and strategy_id == 'surge_hunter':
            score += patterns['surge'].get('score', 5) * 0.5
        elif 'dip' in patterns and strategy_id == 'dip_hunter':
            score += patterns['dip'].get('score', 5) * 0.5
        elif 'gap_down' in patterns and strategy_id == 'gap_down_reversal':
            score += patterns['gap_down'].get('confidence', 0.5) * 5 * 0.5
        elif 'squeeze' in patterns and strategy_id == 'squeeze_momentum':
            score += patterns['squeeze'].get('confidence', 0.5) * 5 * 0.5
        elif 'box' in patterns and strategy_id == 'box_trader':
            score += patterns['box']['confidence'] * 5 * 0.5
        elif 'trend' in patterns and strategy_id == 'trend_follower':
            score += patterns['trend']['confidence'] * 5 * 0.5
        elif 'volume' in patterns and strategy_id == 'volume_hunter':
            score += patterns['volume']['confidence'] * 5 * 0.5
        # v10.24 신규 전략 매핑
        elif 'ema_squeeze' in patterns and strategy_id == 'ema_squeeze':
            score += patterns['ema_squeeze'].get('confidence', 0.5) * 5 * 0.5
        elif 'testa' in patterns and strategy_id == 'testa_3sma':
            score += patterns['testa'].get('confidence', 0.5) * 5 * 0.5
        elif 'rsi_reversal' in patterns and strategy_id == 'rsi_reversal':
            score += patterns['rsi_reversal'].get('confidence', 0.5) * 5 * 0.5
        elif 'volume_breakout_v2' in patterns and strategy_id == 'volume_breakout_v2':
            score += patterns['volume_breakout_v2'].get('confidence', 0.5) * 5 * 0.5
        elif 'mach7' in patterns and strategy_id == 'mach7_pullback':
            score += patterns['mach7'].get('confidence', 0.5) * 5 * 0.5
        
        strategy_scores[strategy_id] = score
    
    if strategy_scores:
        best = max(strategy_scores, key=strategy_scores.get)
        return best, strategy_scores[best]
    
    return None, 0.0

# ═══════════════════════════════════════════════════════
# 🧠 학습 시스템
# ═══════════════════════════════════════════════════════
def learn_from_trade(trade_result):
    """거래 결과 학습"""
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
            
            win_rate = (perf['wins'] / perf['trades'] * 100) if perf['trades'] > 0 else 0
            log(f"🧠 학습: {STRATEGIES[strategy_id]['name']} | 거래: {perf['trades']}회 | 승률: {win_rate:.1f}%", "LEARN")
        
        bot_state['trade_results'].append(trade_result)
        
        if len(bot_state['trade_results']) % LEARNING_CONFIG['learning_interval'] == 0:
            optimize_strategies()
    except:
        pass

def optimize_strategies():
    """전략 최적화"""
    try:
        log("🔄 전략 최적화 시작...", "LEARN")
        
        for strategy_id, strategy in bot_state['strategy_performance'].items():
            perf = strategy['performance']
            
            if perf['trades'] >= 5:
                win_rate = perf['wins'] / perf['trades']
                avg_profit = perf['total_profit'] / perf['trades']
                
                if win_rate >= 0.7 or avg_profit >= 3.0:
                    strategy['weight'] = min(strategy['weight'] * 1.1, 2.0)
                elif win_rate < 0.4 and avg_profit < 1.0:
                    strategy['weight'] = max(strategy['weight'] * 0.9, 0.5)
        
        best = max(bot_state['strategy_performance'].items(),
                   key=lambda x: (x[1]['performance']['wins'] / max(x[1]['performance']['trades'], 1)))
        bot_state['statistics']['best_strategy'] = best[0]
        
        log(f"✅ 최적 전략: {STRATEGIES[best[0]]['name']}", "SUCCESS")
    except:
        pass

# ═══════════════════════════════════════════════════════
# 🛡️ 복구 모드
# ═══════════════════════════════════════════════════════
def recover_funds_from_minus_coins():
    """
    ✅ 마이너스 코인 10%씩 매도해서 시드 확보
    - 실전 모드에서만 작동
    - 마이너스 포지션만 타겟팅
    - 각 코인의 10%씩 매도
    - 매도 대금을 현금으로 확보
    """
    if bot_state['mode'] != 'live':
        log("⚠️ 연습 모드에서는 복구 매도를 실행하지 않습니다", "WARNING")
        return 0
    
    total_recovered = 0
    upbit = bot_state.get('upbit')
    
    if not upbit:
        log("❌ Upbit API 객체가 없습니다", "ERROR")
        return 0
    
    log("="*80, "URGENT")
    log("🚨 마이너스 코인 복구 매도 시작", "URGENT")
    log("="*80, "URGENT")
    
    try:
        for ticker, holding in list(bot_state['simulation_holdings'].items()):
            # 마이너스 포지션만 처리
            if holding.get('profit', 0) >= 0:
                continue
            
            # 10% 매도 수량 계산
            sell_amount = holding['amount'] * 0.10
            current_price = pyupbit.get_current_price(ticker)
            
            if not current_price or sell_amount < 0.00001:
                continue
            
            # 수수료 0.05% 계산
            fee_rate = 0.0005
            sell_value = sell_amount * current_price
            fee = sell_value * fee_rate
            net_proceeds = sell_value - fee
            
            # 실제 매도 실행 (실전 모드)
            try:
                result = upbit.sell_market_order(ticker, sell_amount)
                
                if result:
                    log(f"✅ 복구 매도 성공: {ticker}", "SUCCESS")
                    log(f"   수량: {sell_amount:.6f}개", "INFO")
                    log(f"   매도가: {current_price:,.0f}원", "INFO")
                    log(f"   총액: {sell_value:,.0f}원", "INFO")
                    log(f"   수수료: {fee:,.0f}원 (0.05%)", "INFO")
                    log(f"   실수령: {net_proceeds:,.0f}원", "SUCCESS")
                    
                    # 보유량 갱신
                    holding['amount'] -= sell_amount
                    
                    # 현금 증가
                    bot_state['simulation_krw'] += net_proceeds
                    total_recovered += net_proceeds
                    
                    # 거래 기록
                    bot_state['recent_trades'].append({
                        'ticker': ticker,
                        'type': 'SELL (Recovery)',
                        'amount': sell_amount,
                        'price': current_price,
                        'fee': fee,
                        'net': net_proceeds,
                        'reason': f'마이너스 복구 (손실 {holding["profit_rate"]:.2f}%)',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    time.sleep(0.3)  # API 호출 제한 대비
                    
            except Exception as e:
                log(f"❌ {ticker} 매도 실패: {e}", "ERROR")
    
    except Exception as e:
        log(f"❌ 복구 매도 오류: {e}", "ERROR")
    
    log("="*80, "URGENT")
    log(f"✅ 복구 완료: 총 {total_recovered:,.0f}원 확보", "SUCCESS")
    log("="*80, "URGENT")
    
    return total_recovered

def check_recovery_mode_activation(bot_state):
    """복구 모드 활성화 체크"""
    try:
        if bot_state['recovery_mode_active']:
            return
        
        current_krw = bot_state['simulation_krw']
        holdings_value = sum(
            h['amount'] * (pyupbit.get_current_price(ticker) or h['avg_price'])
            for ticker, h in bot_state['simulation_holdings'].items()
        )
        total_value = current_krw + holdings_value
        
        initial_seed = bot_state['simulation_start_seed']
        loss_rate = ((total_value - initial_seed) / initial_seed) * 100
        
        if loss_rate <= RECOVERY_CONFIG['activate_loss_threshold']:
            log_separator()
            log(f"🛡️ 손실 복구 모드 활성화! 손실: {loss_rate:.2f}%", "URGENT")
            log_separator()
            
            # ✅ 실전 모드에서는 마이너스 코인 10% 매도로 시드 확보
            if bot_state['mode'] == 'live':
                recovered = recover_funds_from_minus_coins()
                current_krw = bot_state['simulation_krw']
                log(f"💰 복구 후 현금: {current_krw:,.0f}원", "SUCCESS")
            
            available_cash = current_krw
            recovery_seed = max(available_cash * RECOVERY_CONFIG['recovery_cash_ratio'], 50000)
            
            loss_amount = abs(total_value - initial_seed)
            recovery_target = loss_amount * RECOVERY_CONFIG['recovery_target_rate']
            
            bot_state['recovery_mode_active'] = True
            bot_state['recovery_seed'] = recovery_seed
            bot_state['recovery_target_amount'] = recovery_target
            bot_state['recovery_trades'] = 0
            bot_state['recovery_success_trades'] = 0
            bot_state['recovery_total_profit'] = 0
            
            bot_state['frozen_holdings'] = bot_state['simulation_holdings'].copy()
            bot_state['simulation_holdings'] = {}
            
            log(f"💰 복구 시드: {recovery_seed:,.0f}원", "RECOVERY")
            log(f"🎯 복구 목표: {recovery_target:,.0f}원", "RECOVERY")
            log(f"❄️ 기존 코인: {len(bot_state['frozen_holdings'])}개 동결", "RECOVERY")
    except:
        pass

def find_recovery_opportunity(tickers, bot_state):
    """복구용 초단타 기회"""
    opportunities = []
    
    for ticker in tickers:
        try:
            df = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
            if df is None or len(df) < 15:
                continue
            
            current_price = df['close'].iloc[-1]
            rsi = calculate_rsi(df)
            vol_spike = calculate_volume_spike(df)
            
            score = 0
            signals = []
            
            if 25 <= rsi <= 35 and vol_spike >= 1.5:
                score += 5
                signals.append(f"RSI {rsi:.1f}")
            
            change_1m = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            if vol_spike >= 2.5 and change_1m > 0.5:
                score += 4
                signals.append(f"수급 {vol_spike:.1f}배")
            
            if score >= 7:
                opportunities.append({
                    'ticker': ticker,
                    'price': current_price,
                    'score': score,
                    'signals': signals
                })
            
            time.sleep(0.05)
        except:
            continue
    
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    return opportunities

# ═══════════════════════════════════════════════════════
# 💰 거래 실행
# ═══════════════════════════════════════════════════════
def execute_trade(ticker, strategy_id, patterns, bot_state):
    """거래 실행 (수수료 0.05% 포함)"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            invest_amount = bot_state['recovery_seed']
        else:
            invest_amount = min(bot_state['simulation_krw'] * 0.15, 150000)
        
        if invest_amount < 5000:
            return None
        
        # ✅ 수수료 0.05% 계산
        FEE_RATE = 0.0005
        fee = invest_amount * FEE_RATE
        net_invest = invest_amount - fee  # 실제 매수에 사용되는 금액
        
        buy_amount = net_invest / current_price  # 수수료 제외 후 실제 매수 수량
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            bot_state['recovery_seed'] -= invest_amount
            bot_state['recovery_trades'] += 1
        else:
            bot_state['simulation_krw'] -= invest_amount
        
        holding_info = {
            'amount': buy_amount,
            'avg_price': current_price,
            'invested': invest_amount,
            'fee_paid': fee,  # ✅ 지불한 수수료 기록
            'net_invested': net_invest,  # ✅ 실제 투자 금액
            'entry_time': datetime.now(),
            'strategy': strategy_id,
            'patterns': patterns,
            'peak_price': current_price,
            'type': 'RECOVERY' if bot_state['recovery_mode_active'] else patterns.get('type', 'NORMAL')
        }
        
        # 급락 매수인 경우 원가 저장
        if 'dip' in patterns:
            holding_info['price_before_dip'] = patterns['dip'].get('price_before_dip', current_price)
        
        bot_state['simulation_holdings'][ticker] = holding_info
        
        # ✅ 상세 로그
        coin_name = ticker.replace('KRW-', '')
        log("="*60, "SUCCESS")
        log(f"💰 {'[복구]' if bot_state['recovery_mode_active'] else ''} 매수: {coin_name}", "SUCCESS")
        log(f"   수량: {buy_amount:.6f}개", "INFO")
        log(f"   매수가: {current_price:,.0f}원", "INFO")
        log(f"   투자금: {invest_amount:,.0f}원", "INFO")
        log(f"   수수료: {fee:,.0f}원 (0.05%)", "INFO")
        log(f"   실투자: {net_invest:,.0f}원", "INFO")
        log(f"   전략: {STRATEGIES[strategy_id]['name']}", "INFO")
        log("="*60, "SUCCESS")
        
        # 거래 내역 추가 (상세 이유 포함)
        buy_reason = f"전략: {STRATEGIES[strategy_id]['name']}"
        
        # 패턴 정보 추가
        pattern_details = []
        if patterns.get('rsi'):
            rsi_val = patterns['rsi'].get('value', 0)
            if rsi_val < 30:
                pattern_details.append(f"RSI 과매도({rsi_val:.1f})")
            elif rsi_val > 70:
                pattern_details.append(f"RSI 과매수({rsi_val:.1f})")
        
        if patterns.get('volume_surge'):
            vol_change = patterns['volume_surge'].get('volume_change_pct', 0)
            pattern_details.append(f"거래량 급증(+{vol_change:.0f}%)")
        
        if patterns.get('dip'):
            dip_pct = patterns['dip'].get('dip_percent', 0)
            pattern_details.append(f"급락 후 반등({dip_pct:.1f}%)")
        
        if patterns.get('trend'):
            trend = patterns['trend'].get('trend', '')
            if trend:
                pattern_details.append(f"추세: {trend}")
        
        if pattern_details:
            buy_reason += " | " + ", ".join(pattern_details)
        
        bot_state['recent_trades'].append({
            'ticker': ticker,
            'type': 'BUY',
            'amount': buy_amount,
            'price': current_price,
            'invested': invest_amount,
            'fee': fee,
            'net_invested': net_invest,
            'strategy': STRATEGIES[strategy_id]['name'],
            'reason': buy_reason,
            'patterns': pattern_details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mode': bot_state.get('mode', 'practice')
        })
        
        # DB에 영구 저장
        user_id = bot_state.get('user_id', 'unknown')
        save_trade_to_db(user_id, bot_state['recent_trades'][-1])
        
        # CSV 로그에도 기록
        append_trade_to_csv(user_id, bot_state['recent_trades'][-1], holding_info)
        
        # 봇 상태도 DB에 저장 (simulation_holdings 포함)
        save_bot_state_to_db(user_id, bot_state)
        
        return True
    except Exception as e:
        log(f"거래 오류: {e}", "ERROR")
        return None

def check_exit(ticker, holding, bot_state):
    """청산 조건 체크"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return False, None
        
        entry_price = holding['avg_price']
        profit_rate = (current_price - entry_price) / entry_price * 100
        strategy_id = holding.get('strategy')
        trade_type = holding.get('type')
        
        if current_price > holding.get('peak_price', 0):
            holding['peak_price'] = current_price
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            if profit_rate >= RECOVERY_CONFIG['recovery_target_profit']:
                return True, f"복구 익절 (+{profit_rate:.2f}%)"
            if profit_rate <= RECOVERY_CONFIG['recovery_stop_loss']:
                return True, f"복구 손절 ({profit_rate:.2f}%)"
            
            hold_time = (datetime.now() - holding['entry_time']).total_seconds() / 60
            if hold_time >= RECOVERY_CONFIG['recovery_max_hold_time']:
                return True, "복구 시간초과"
        
        # 급락 매수 (원가 복귀)
        elif trade_type == 'DIP':
            price_before_dip = holding.get('price_before_dip', entry_price)
            back_to_original = (current_price - price_before_dip) / price_before_dip * 100
            
            if profit_rate <= SURGE_CONFIG['dip_emergency_stop']:
                return True, "급락 긴급손절"
            
            if back_to_original >= SURGE_CONFIG['dip_recovery_threshold']:
                return True, f"원가 복귀! (+{profit_rate:.2f}%)"
            
            hold_time = (datetime.now() - holding['entry_time']).total_seconds() / 60
            if hold_time >= SURGE_CONFIG['dip_max_hold_time']:
                return True, "급락 최대시간"
        
        # 일반
        else:
            # Squeeze Momentum 전략의 경우 모멘텀 반전 체크
            if strategy_id == 'squeeze_momentum':
                try:
                    squeeze_check = detect_squeeze_momentum(ticker)
                    if squeeze_check and squeeze_check.get('type') == 'SQUEEZE_MOMENTUM_EXIT':
                        return True, f"모멘텀 반전 ({profit_rate:+.2f}%)"
                except:
                    pass
            
            # Gap-Down Reversal 전략의 목표가 체크
            if strategy_id == 'gap_down_reversal':
                target_price = holding.get('target_price')
                if target_price and current_price >= target_price:
                    return True, f"목표가 도달 (+{profit_rate:.2f}%)"
            
            # 🔥 시간 기반 강제 청산 (6시간 초과)
            hold_time_minutes = (datetime.now() - holding['entry_time']).total_seconds() / 60
            if hold_time_minutes >= 360:  # 6시간
                return True, f"시간초과 청산 ({profit_rate:+.2f}%, {hold_time_minutes/60:.1f}시간)"
            
            # 기본 익절/손절 (더 빠른 청산)
            if profit_rate >= 2.0:  # 3.0 -> 2.0 (더 빠른 익절)
                return True, f"익절 (+{profit_rate:.2f}%)"
            if profit_rate <= SURGE_CONFIG['stop_loss']:  # -2.0%
                return True, f"손절 ({profit_rate:.2f}%)"
        
        return False, None
    except:
        return False, None

def execute_exit(ticker, holding, reason, bot_state):
    """청산 실행 (수수료 0.05% 포함)"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        amount = holding['amount']
        entry_price = holding['avg_price']
        strategy_id = holding.get('strategy')
        invested = holding['invested']
        
        # ✅ 수수료 0.05% 계산
        FEE_RATE = 0.0005
        sell_value = amount * current_price  # 매도 총액
        fee = sell_value * FEE_RATE  # 수수료
        net_proceeds = sell_value - fee  # 실제 받는 금액
        
        profit_krw = net_proceeds - invested  # 순수익 = 실수령액 - 투자금
        profit_rate = (current_price - entry_price) / entry_price * 100
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            bot_state['recovery_seed'] += net_proceeds
            if profit_rate > 0:
                bot_state['recovery_success_trades'] += 1
                bot_state['recovery_total_profit'] += profit_krw
            else:
                bot_state['last_loss_time'] = datetime.now()
            
            progress = (bot_state['recovery_total_profit'] / bot_state['recovery_target_amount']) * 100
            bot_state['statistics']['recovery_progress'] = progress
            
            log(f"{'✅' if profit_rate > 0 else '❌'} 복구: {ticker} | {profit_rate:+.2f}% | {reason}", "RECOVERY" if profit_rate > 0 else "WARNING")
            log(f"📊 복구 진행: {progress:.1f}%", "RECOVERY")
            
            # 복구 완료
            if bot_state['recovery_total_profit'] >= bot_state['recovery_target_amount']:
                log_separator()
                log("🎉 복구 목표 달성!", "SUCCESS")
                log_separator()
                bot_state['recovery_mode_active'] = False
                bot_state['simulation_holdings'].update(bot_state['frozen_holdings'])
                bot_state['frozen_holdings'] = {}
        else:
            bot_state['simulation_krw'] += net_proceeds
            
            # ✅ 상세 로그
            coin_name = ticker.replace('KRW-', '')
            log("="*60, "SUCCESS" if profit_rate > 0 else "WARNING")
            log(f"💸 매도: {coin_name}", "SUCCESS" if profit_rate > 0 else "WARNING")
            log(f"   수량: {amount:.6f}개", "INFO")
            log(f"   매도가: {current_price:,.0f}원", "INFO")
            log(f"   매도액: {sell_value:,.0f}원", "INFO")
            log(f"   수수료: {fee:,.0f}원 (0.05%)", "INFO")
            log(f"   실수령: {net_proceeds:,.0f}원", "INFO")
            log(f"   순수익: {profit_krw:+,.0f}원 ({profit_rate:+.2f}%)", "SUCCESS" if profit_krw > 0 else "WARNING")
            log(f"   사유: {reason}", "INFO")
            log("="*60, "SUCCESS" if profit_rate > 0 else "WARNING")
            
            # 거래 내역 추가 (상세 이유 포함)
            hold_time = (datetime.now() - holding['entry_time']).total_seconds() / 60
            hold_time_str = f"{int(hold_time//60)}시간 {int(hold_time%60)}분" if hold_time >= 60 else f"{int(hold_time)}분"
            
            sell_reason = f"{reason}"
            if profit_rate > 0:
                sell_reason += f" | 목표 달성 (+{profit_rate:.2f}%)"
            else:
                sell_reason += f" | 손절 ({profit_rate:.2f}%)"
            
            sell_reason += f" | 보유: {hold_time_str}"
            
            bot_state['recent_trades'].append({
                'ticker': ticker,
                'type': 'SELL',
                'amount': holding['amount'],
                'price': current_price,
                'entry_price': entry_price,
                'sell_value': sell_value,
                'fee': fee,
                'net_proceeds': net_proceeds,
                'profit': profit_krw,
                'profit_rate': profit_rate,
                'reason': sell_reason,
                'hold_time': hold_time,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'mode': bot_state.get('mode', 'practice')
            })
            
            # DB에 영구 저장
            user_id = bot_state.get('user_id', 'unknown')
            save_trade_to_db(user_id, bot_state['recent_trades'][-1])
            
            # CSV 로그에도 기록
            append_trade_to_csv(user_id, bot_state['recent_trades'][-1], holding)
            
            # 봇 상태도 DB에 저장 (simulation_holdings 업데이트)
            save_bot_state_to_db(user_id, bot_state)
        
        del bot_state['simulation_holdings'][ticker]
        
        # 매도 후 DB에 한 번 더 저장 (holdings 업데이트 반영)
        save_bot_state_to_db(user_id, bot_state)
        
        # 학습
        trade_result = {
            'ticker': ticker,
            'strategy': strategy_id,
            'profit_rate': profit_rate,
            'profit_krw': profit_krw,
            'patterns': holding.get('patterns', {}),
            'timestamp': datetime.now()
        }
        learn_from_trade(trade_result)
        
        # 통계
        bot_state['statistics']['total_trades'] += 1
        if profit_rate > 0:
            bot_state['statistics']['winning_trades'] += 1
        else:
            bot_state['statistics']['losing_trades'] += 1
        bot_state['statistics']['total_profit'] += profit_rate
        
        return True
    except Exception as e:
        log(f"청산 오류: {e}", "ERROR")
        return None

# ═══════════════════════════════════════════════════════
# 🔐 영구 세션 관리 시스템 (서버 재시작해도 로그인 유지)
# ═══════════════════════════════════════════════════════

def init_persistent_sessions():
    """영구 세션 테이블 초기화"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS persistent_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    # 만료된 세션 정리 (30일 이상 접속 없음)
    conn.execute("""
        DELETE FROM persistent_sessions 
        WHERE datetime(last_accessed) < datetime('now', '-30 days')
    """)
    conn.commit()
    conn.close()

def save_persistent_session(user_id: str) -> str:
    """영구 세션 생성 및 저장"""
    session_id = hashlib.sha256(f"{user_id}-{time.time()}-{os.urandom(16).hex()}".encode()).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO persistent_sessions (session_id, user_id, expires_at)
        VALUES (?, ?, datetime('now', '+30 days'))
    """, (session_id, user_id))
    conn.commit()
    conn.close()
    return session_id

def load_persistent_session(session_id: str) -> str:
    """영구 세션에서 user_id 복원"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT user_id FROM persistent_sessions
        WHERE session_id = ? AND datetime(expires_at) > datetime('now')
    """, (session_id,))
    row = cur.fetchone()
    
    if row:
        # 마지막 접속 시간 업데이트
        conn.execute("""
            UPDATE persistent_sessions 
            SET last_accessed = CURRENT_TIMESTAMP,
                expires_at = datetime('now', '+30 days')
            WHERE session_id = ?
        """, (session_id,))
        conn.commit()
        conn.close()
        return row[0]
    
    conn.close()
    return None

def delete_persistent_session(session_id: str):
    """로그아웃 시 세션 삭제"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM persistent_sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════
# 🚀 Flask 웹 서버
# ═══════════════════════════════════════════════════════
app = Flask(__name__)

# ✅ 고정된 SECRET_KEY (환경변수 또는 파일에서 로드)
SECRET_KEY_FILE = "/home/user/webapp/.secret_key"
if os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, "rb") as f:
        app.secret_key = f.read()
else:
    # 처음 실행 시 키 생성 및 저장
    app.secret_key = os.urandom(32)
    with open(SECRET_KEY_FILE, "wb") as f:
        f.write(app.secret_key)
    os.chmod(SECRET_KEY_FILE, 0o600)  # 소유자만 읽기/쓰기

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

CORS(app)

# UserManager 초기화
user_manager = UserManager()

# 🔧 bot_states 테이블 초기화
init_bot_state_table()

# 🔐 영구 세션 테이블 초기화
init_persistent_sessions()

# 사용자별 봇 상태 저장 (user_id를 키로 사용)
user_bots = {}

# ✅ 자동 세션 복원 미들웨어
@app.before_request
def restore_session():
    """서버 재시작 후 쿠키에서 세션 자동 복원"""
    # 이미 로그인되어 있으면 패스
    if 'user_id' in session:
        session.permanent = True  # 영구 세션 활성화
        return
    
    # 쿠키에서 persistent_session_id 확인
    persistent_id = request.cookies.get('persistent_session_id')
    if persistent_id:
        user_id = load_persistent_session(persistent_id)
        if user_id:
            # 세션 복원 성공
            session['user_id'] = user_id
            session.permanent = True
            log(f"🔓 세션 자동 복원: {user_id}", "INFO")

@app.route('/')
def index():
    # 세션 확인
    if 'user_id' not in session:
        return redirect('/login')
    
    response = make_response(render_template('dashboard-new-ui.html'))
    # 캐시 방지
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/status')
def api_status():
    try:
        # 세션 확인 - Guest 자동 생성하지 않음
        if 'user_id' not in session:
            # 로그인 필요
            return jsonify({
                'success': False,
                'message': '로그인이 필요합니다',
                'running': False,
                'current_krw': 0,
                'start_seed': 1000000,
                'current_seed': 1000000,
                'total_profit': 0,
                'profit_rate': 0,
                'win_rate': 0,
                'strategies': {},
                'holdings': [],
                'recent_surges': [],
                'recent_trades': []
            })
        
        # ✅ user_id는 숫자, 하지만 bot_state는 username(문자열)을 키로 사용
        username = session.get('username')
        if not username:
            return jsonify({
                'success': False,
                'message': '로그인이 필요합니다',
                'running': False,
                'current_krw': 0,
                'start_seed': 1000000,
                'current_seed': 1000000,
                'total_profit': 0,
                'profit_rate': 0,
                'win_rate': 0,
                'strategies': {},
                'holdings': [],
                'recent_surges': [],
                'recent_trades': []
            })
        
        bot_state = get_user_bot_state(username)
        
        # 봇이 실행 중이 아니면 초기 상태 반환
        if not bot_state['running']:
            return jsonify({
                'running': False,
                'current_krw': bot_state.get('simulation_seed', 1000000),
                'start_seed': bot_state.get('simulation_start_seed', bot_state.get('simulation_seed', 1000000)),
                'current_seed': bot_state.get('simulation_seed', 1000000),
                'total_profit': 0,
                'profit_rate': 0,
                'win_rate': 0,
                'strategies': bot_state['strategy_performance'],
                'holdings': [],
                'recent_surges': [],
                'recent_trades': []
            })
        
        # 봇 실행 중일 때만 실제 계산
        current_krw = bot_state['simulation_krw']
        
        # 보유 코인 가치 계산 + 상세 정보
        holdings_value = 0
        holdings_list = []
        
        if bot_state['simulation_holdings']:
            for ticker, h in bot_state['simulation_holdings'].items():
                try:
                    current_price = pyupbit.get_current_price(ticker)
                    if not current_price:
                        current_price = h['avg_price']
                    
                    coin_value = h['amount'] * current_price
                    holdings_value += coin_value
                    
                    # 평가 손익
                    profit = coin_value - (h['amount'] * h['avg_price'])
                    profit_rate = (profit / (h['amount'] * h['avg_price'])) * 100
                    
                    holdings_list.append({
                        'ticker': ticker,
                        'coin_name': ticker.replace('KRW-', ''),
                        'amount': h['amount'],
                        'avg_price': h['avg_price'],
                        'current_price': current_price,
                        'value': coin_value,
                        'profit': profit,
                        'profit_rate': profit_rate
                    })
                except:
                    holdings_value += h['amount'] * h['avg_price']
        
        # 동결 코인 가치 계산
        frozen_value = 0
        if bot_state['frozen_holdings']:
            for ticker, h in bot_state['frozen_holdings'].items():
                try:
                    current_price = pyupbit.get_current_price(ticker)
                    if current_price:
                        frozen_value += h['amount'] * current_price
                    else:
                        frozen_value += h['amount'] * h['avg_price']
                except:
                    frozen_value += h['amount'] * h['avg_price']
        
        total_value = current_krw + holdings_value + frozen_value
        
        total_trades = bot_state['statistics']['total_trades']
        winning_trades = bot_state['statistics']['winning_trades']
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        profit = total_value - bot_state['simulation_start_seed']
        profit_rate = (profit / bot_state['simulation_start_seed']) * 100 if bot_state['simulation_start_seed'] > 0 else 0
        
        # 최근 거래 내역 변환
        recent_trades = []
        for trade in list(bot_state.get('recent_trades', []))[-10:]:
            recent_trades.append({
                'ticker': trade['ticker'],
                'type': trade['type'],
                'amount': trade['amount'],
                'price': trade['price'],
                'timestamp': trade.get('timestamp', '')
            })
        
        return jsonify({
            'running': True,
            'current_krw': current_krw,
            'holdings_value': holdings_value,
            'total_value': total_value,
            'start_seed': bot_state.get('simulation_start_seed', bot_state.get('simulation_seed', 1000000)),
            'current_seed': bot_state.get('simulation_seed', 1000000),
            'total_profit': profit,
            'profit_rate': profit_rate,
            'win_rate': win_rate,
            'strategies': bot_state['strategy_performance'],
            'holdings': holdings_list,
            'recent_surges': [],
            'recent_trades': recent_trades
        })
    except Exception as e:
        log(f"API 상태 조회 오류: {e}", "ERROR")
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history_page():
    """거래 히스토리 페이지"""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('history.html')

@app.route('/api/history')
def api_history():
    """거래 히스토리 API (DB에서 영구 저장된 데이터 조회)"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        username = session['username']
        mode = request.args.get('mode', 'practice')
        
        # DB에서 거래 내역 조회
        import sqlite3
        conn = sqlite3.connect('upbit_bot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trade_history
            WHERE user_id = ? AND mode = ?
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', (username, mode))
        
        db_trades = cursor.fetchall()
        conn.close()
        
        # 통계 계산
        total_trades = 0
        winning_trades = 0
        losing_trades = 0
        total_profit_rate = 0
        
        for trade in db_trades:
            if trade['trade_type'] == 'SELL':
                total_trades += 1
                profit_rate = trade['profit_rate'] or 0
                total_profit_rate += profit_rate
                
                if profit_rate >= 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_profit = (total_profit_rate / total_trades) if total_trades > 0 else 0
        
        # 거래 내역 변환
        trades_list = []
        for trade in db_trades:
            trade_data = {
                'ticker': trade['ticker'],
                'type': trade['trade_type'],
                'amount': trade['amount'],
                'price': trade['price'],
                'fee': trade['fee'] or 0,
                'timestamp': trade['timestamp'],
                'reason': trade['reason'] or '',
                'strategy': trade['strategy'] or '전략 미상',
                'mode': trade['mode']
            }
            
            if trade['trade_type'] == 'BUY':
                trade_data['invested'] = trade['invested'] or 0
                trade_data['net_invested'] = trade['net_invested'] or 0
            else:  # SELL
                trade_data['entry_price'] = trade['entry_price'] or 0
                trade_data['sell_value'] = trade['sell_value'] or 0
                trade_data['net_proceeds'] = trade['net_proceeds'] or 0
                trade_data['profit'] = trade['profit'] or 0
                trade_data['profit_rate'] = trade['profit_rate'] or 0
            
            trades_list.append(trade_data)
        
        return jsonify({
            'success': True,
            'trades': trades_list,
            'stats': {
                'total': total_trades,
                'winning': winning_trades,
                'losing': losing_trades,
                'win_rate': win_rate,
                'avg_profit': avg_profit
            },
            'mode': mode
        })
    except Exception as e:
        log(f"히스토리 API 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start():
    try:
        # ✅ 사용자별 독립 봇 상태 가져오기
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        username = session['username']
        
        log(f"[START] username: {username}", "INFO")
        bot_state = get_user_bot_state(username)
        
        # ✅ 이 사용자의 봇이 실행 중인지 체크
        if bot_state['running']:
            return jsonify({'success': False, 'message': '이미 실행 중입니다. 먼저 정지해주세요.'})
        
        data = request.json or {}
        mode = data.get('mode', 'practice')
        seed = data.get('seed', 1000000)
        txid = data.get('txid', '')
        
        # 기존 시작 시드와 비교
        old_start_seed = bot_state.get('simulation_start_seed', None)
        seed_changed = (old_start_seed is not None and old_start_seed != seed)
        
        # 실전 모드 검증
        if mode == 'live':
            # 라이선스 검증 (TODO: TronScan API 연동)
            if not txid or len(txid) < 40:
                return jsonify({
                    'success': False, 
                    'message': '⚠️ 실전 모드는 라이선스 인증이 필요합니다!\n\n1. TXID를 입력하세요\n2. "🔐 라이선스 인증" 버튼을 클릭하세요'
                })
            
            # API 키 확인
            if not bot_state.get('upbit'):
                # config.json에서 API 키 로드 시도
                try:
                    import json
                    with open('config.json', 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        access_key = config.get('upbit_access_key', '')
                        secret_key = config.get('upbit_secret_key', '')
                        
                        if not access_key or not secret_key:
                            return jsonify({
                                'success': False,
                                'message': '⚠️ API 키를 먼저 설정해주세요!\n\n1. Access Key 입력\n2. Secret Key 입력\n3. "💾 저장" 클릭'
                            })
                        
                        # Upbit 객체 생성
                        bot_state['upbit'] = pyupbit.Upbit(access_key, secret_key)
                        log("실전 모드: API 키 로드 완료", "SUCCESS")
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'❌ API 키 로드 실패: {str(e)}'
                    })
            
            # 실전 모드 시드는 실제 잔고에서 가져오기
            try:
                real_balance = bot_state['upbit'].get_balance('KRW')
                if real_balance < 100000:  # 최소 10만원
                    return jsonify({
                        'success': False,
                        'message': f'⚠️ 잔고 부족!\n\n현재 잔고: {real_balance:,.0f}원\n최소 필요: 100,000원'
                    })
                seed = real_balance
                log(f"실전 모드: 실제 잔고 {seed:,}원", "SUCCESS")
                
                # ✅ 실전 모드: 현재 보유 코인 스캔 및 분석
                balances = bot_state['upbit'].get_balances()
                total_holdings_value = 0
                minus_count = 0
                
                for balance in balances:
                    ticker_code = balance['currency']
                    if ticker_code == 'KRW':
                        continue
                    
                    ticker = f'KRW-{ticker_code}'
                    amount = float(balance['balance'])
                    avg_price = float(balance['avg_buy_price'])
                    
                    if amount > 0:
                        current_price = pyupbit.get_current_price(ticker)
                        if current_price:
                            holding_value = amount * current_price
                            total_holdings_value += holding_value
                            
                            profit = (current_price - avg_price) * amount
                            profit_rate = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
                            
                            # 봇 상태에 기록
                            bot_state['simulation_holdings'][ticker] = {
                                'amount': amount,
                                'avg_price': avg_price,
                                'current_price': current_price,
                                'profit': profit,
                                'profit_rate': profit_rate
                            }
                            
                            # 마이너스 포지션 카운트
                            if profit < 0:
                                minus_count += 1
                                log(f"⚠️ 마이너스 포지션 발견: {ticker} | {profit:,.0f}원 ({profit_rate:.2f}%)", "WARNING")
                            else:
                                log(f"✅ 플러스 포지션: {ticker} | +{profit:,.0f}원 (+{profit_rate:.2f}%)", "SUCCESS")
                
                log(f"📊 현재 보유 분석 완료: 총 {len(bot_state['simulation_holdings'])}개 코인, 마이너스 {minus_count}개", "INFO")
                log(f"💰 보유 코인 가치: {total_holdings_value:,.0f}원", "INFO")
                
                # 복구 모드 자동 활성화 (마이너스 포지션이 3개 이상이면)
                if minus_count >= 3:
                    bot_state['recovery_mode_active'] = True
                    log(f"🚨 복구 모드 자동 활성화 (마이너스 {minus_count}개)", "URGENT")
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'❌ 잔고 조회 실패: {str(e)}\n\nAPI 키를 확인하세요.'
                })
        
        # 시드 변경 시에만 완전 초기화
        if seed_changed:
            log(f"[{user_id}] 시드 변경 감지: {old_start_seed:,}원 → {seed:,}원 (데이터 초기화)", "WARNING")
            
            # 완전 초기화
            bot_state['simulation_seed'] = seed
            bot_state['simulation_krw'] = seed
            bot_state['simulation_start_seed'] = seed
            bot_state['simulation_holdings'] = {}
            bot_state['frozen_holdings'] = {}
            bot_state['recovery_mode_active'] = False
            bot_state['recovery_seed'] = 0
            bot_state['recovery_target_amount'] = 0
            bot_state['recovery_trades'] = 0
            bot_state['recovery_success_trades'] = 0
            bot_state['recovery_total_profit'] = 0
            
            # 통계 초기화
            bot_state['recent_trades'].clear()
            bot_state['recent_signals'].clear()
            bot_state['statistics'] = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_profit': 0,
                'best_strategy': None,
                'recovery_progress': 0,
            }
            
            # 전략 성과 초기화
            for strategy_key in bot_state['strategy_performance']:
                bot_state['strategy_performance'][strategy_key]['performance'] = {
                    'trades': 0,
                    'wins': 0,
                    'total_profit': 0
                }
        else:
            # 같은 시드로 재시작 (데이터 보존)
            log(f"[{user_id}] 기존 데이터 유지 재시작: {seed:,}원", "INFO")
            
            # 기존 simulation_start_seed가 없으면 현재 시드를 시작 시드로 설정
            if bot_state.get('simulation_start_seed') is None:
                bot_state['simulation_start_seed'] = seed
            
            # 현재 시드만 업데이트 (보유 코인, 거래 내역 등은 보존)
            if bot_state.get('simulation_seed') != seed:
                bot_state['simulation_seed'] = seed
        
        bot_state['mode'] = mode
        
        bot_state['running'] = True
        bot_state['start_time'] = datetime.now()
        
        # 💾 DB에 봇 상태 저장
        save_bot_state(user_id, bot_state)
        
        # ✅ 사용자별 독립 스레드 시작 (user_id와 bot_state 전달)
        thread = threading.Thread(target=bot_main_loop, args=(user_id, bot_state), daemon=True)
        thread.start()
        bot_state['thread'] = thread
        
        mode_text = "💎 실전 모드" if mode == 'live' else "연습 모드"
        log(f"[{user_id}] 봇 시작! {mode_text}, 시드: {seed:,}원", "SUCCESS")
        
        return jsonify({'success': True, 'message': f'✅ 봇 시작! ({mode_text})'})
    except Exception as e:
        log(f"시작 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    try:
        # ✅ 사용자별 독립 봇 상태 가져오기
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        username = session['username']
        
        log(f"[STOP] username: {username}", "INFO")
        bot_state = get_user_bot_state(username)
        
        bot_state['running'] = False
        
        # 💾 DB에 봇 상태 저장
        save_bot_state(username, bot_state)
        
        # 스레드가 종료될 때까지 대기 (최대 5초)
        if 'thread' in bot_state and bot_state['thread'] and bot_state['thread'].is_alive():
            bot_state['thread'].join(timeout=5)
        log(f"[{username}] 봇이 정지되었습니다", "INFO")
        return jsonify({'success': True, 'message': '봇 중지'})
    except Exception as e:
        log(f"정지 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/user/referral-link')
def api_get_referral_link():
    """사용자의 추천 링크 가져오기"""
    try:
        # 사용자 ID 가져오기
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        user_id = session['user_id']
        username = session.get('username', 'unknown')
        
        # DB에서 추천 코드 가져오기
        import sqlite3
        import hashlib
        
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        # username으로 추천 코드 조회
        cursor.execute("SELECT referral_code FROM users WHERE username = ?", (user_id,))
        result = cursor.fetchone()
        
        # 추천 코드가 없으면 생성
        if not result or not result[0]:
            referral_code = hashlib.md5(user_id.encode()).hexdigest()[:8].upper()
            
            # DB에 저장 시도
            try:
                # 사용자가 이미 존재하는지 확인
                cursor.execute("SELECT username FROM users WHERE username = ?", (user_id,))
                if cursor.fetchone():
                    # 기존 사용자 업데이트
                    cursor.execute("""
                        UPDATE users SET referral_code = ? WHERE username = ?
                    """, (referral_code, user_id))
                else:
                    # 새 사용자 삽입
                    cursor.execute("""
                        INSERT INTO users (username, referral_code, created_at)
                        VALUES (?, ?, datetime('now'))
                    """, (user_id, referral_code))
                
                conn.commit()
            except Exception as e:
                log(f"추천 코드 저장 오류: {e}", "ERROR")
                conn.rollback()
        else:
            referral_code = result[0]
        
        conn.close()
        
        # 전체 추천 링크 생성
        referral_link = f"{request.host_url.rstrip('/')}/?ref={referral_code}"
        
        return jsonify({
            'success': True,
            'referral_code': referral_code,
            'referral_link': referral_link
        })
        
    except Exception as e:
        log(f"추천 링크 로드 오류: {e}", "ERROR")
        return jsonify({
            'success': False,
            'message': str(e),
            'referral_link': f"{request.host_url.rstrip('/')}/?ref=LOADING"
        }), 500

@app.route('/api/verify-license', methods=['POST'])
def api_verify_license():
    """라이선스 검증 API - USDT TRC-20 기반"""
    try:
        data = request.json or {}
        txid = data.get('txid', '').strip()
        
        if not txid:
            return jsonify({'success': False, 'message': 'TXID를 입력해주세요'})
        
        # TXID 기본 검증
        if len(txid) < 20:
            return jsonify({'success': False, 'message': 'TXID가 너무 짧습니다. 올바른 트론 TXID를 입력하세요.'})
        
        # TODO: TronScan API로 실제 USDT 금액 확인
        # 예시: https://api.trongrid.io/v1/transactions/{txid}
        # 입금 주소: TLb5D3uDQjPQt6CzATM21t21etxGsSvtbt
        # USDT 금액에 따라 만료일 계산:
        # - 50 USDT = 1개월
        # - 250 USDT = 6개월
        # - 500 USDT = 평생
        
        log(f"라이선스 검증 시도: {txid[:10]}...", "INFO")
        
        # 데모용: TXID가 64자 이상이면 인증 성공
        if len(txid) >= 40:
            # 실제로는 TronScan API로 금액 확인 후 만료일 계산
            return jsonify({
                'success': True, 
                'message': '라이선스 인증 완료',
                'license_type': 'premium',
                'expires_at': '2027-12-31',
                'usdt_amount': 0  # TODO: 실제 금액
            })
        else:
            return jsonify({'success': False, 'message': '유효하지 않은 TXID입니다. 트론스캔에서 확인 후 다시 입력하세요.'})
            
    except Exception as e:
        log(f"라이선스 검증 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def api_config():
    """API 키 설정"""
    try:
        data = request.json or {}
        access_key = data.get('access_key', '').strip()
        secret_key = data.get('secret_key', '').strip()
        
        if not access_key or not secret_key:
            return jsonify({'success': False, 'message': 'Access Key와 Secret Key를 모두 입력해주세요'})
        
        # config.json 업데이트
        try:
            import json
            config_path = 'config.json'
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            config['upbit_access_key'] = access_key
            config['upbit_secret_key'] = secret_key
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            log("API 키가 저장되었습니다", "SUCCESS")
            return jsonify({'success': True, 'message': 'API 키 저장 완료'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'저장 실패: {str(e)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ═══════════════════════════════════════════════════════
# 🔄 메인 봇 루프
# ═══════════════════════════════════════════════════════
def bot_main_loop(user_id, bot_state):
    """메인 루프 (완전체) - 사용자별 독립 실행"""
    import sys
    import traceback
    
    try:
        # 로그 파일 열기
        log_file = open(f'/tmp/bot_{user_id}_debug.log', 'a', buffering=1)
        log_file.write(f"\n{'='*80}\n")
        log_file.write(f"[{datetime.now()}] 봇 시작: {user_id}\n")
        log_file.flush()
        
        log_separator()
        log(f"🚀 [{user_id}] AI 트레이딩 봇 v8.0 ULTIMATE 시작!", "SUCCESS")
        log_separator()
        
        bot_state['start_time'] = datetime.now()
        
        # 초기 안정화 대기 (5초)
        log(f"[{user_id}] ⏱️ 초기화 중... (5초 대기)", "INFO")
        log_file.write(f"[{datetime.now()}] 초기화 중... 5초 대기\n")
        log_file.flush()
        
        time.sleep(5)
        
        log_file.write(f"[{datetime.now()}] 5초 대기 완료\n")
        log_file.flush()
        
        log(f"[{user_id}] ✅ 스캔 시작!", "SUCCESS")
        log_file.write(f"[{datetime.now()}] 스캔 시작 메시지 출력 완료\n")
        log_file.flush()
        
        # 거래량 기반 동적 티커 선정 (빠른 버전 - 고정 목록 사용)
        def get_top_volume_tickers_fast(count=50):
            """인기 코인 목록 반환 (API 호출 없음, 즉시 반환)"""
            popular_coins = [
                'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
                'KRW-ADA', 'KRW-AVAX', 'KRW-DOT', 'KRW-MATIC', 'KRW-LINK',
                'KRW-ATOM', 'KRW-ETC', 'KRW-NEAR', 'KRW-HBAR', 'KRW-APT',
                'KRW-SUI', 'KRW-TRX', 'KRW-SHIB', 'KRW-TON', 'KRW-PEPE',
                'KRW-ARB', 'KRW-OP', 'KRW-IMX', 'KRW-AAVE', 'KRW-ALGO',
                'KRW-SEI', 'KRW-STRK', 'KRW-ORDI', 'KRW-PYTH', 'KRW-MANTA',
                'KRW-MEME', 'KRW-WLD', 'KRW-JUP', 'KRW-ONDO', 'KRW-DYM',
                'KRW-BLUR', 'KRW-PENDLE', 'KRW-WIF', 'KRW-BONK', 'KRW-JITO',
                'KRW-MYRO', 'KRW-INJ', 'KRW-TIA', 'KRW-BEAM', 'KRW-MINA',
                'KRW-OCEAN', 'KRW-CRV', 'KRW-SAND', 'KRW-AXS', 'KRW-FLOW'
            ]
            return popular_coins[:count]
        
        log_file.write(f"[{datetime.now()}] get_top_volume_tickers_fast 함수 정의 완료\n")
        log_file.flush()
        
        # 초기 티커 목록 (고정 목록으로 즉시 시작)
        popular_tickers = get_top_volume_tickers_fast(50)
        log(f"[{user_id}] 📊 {len(popular_tickers)}개 인기 코인으로 시작", "INFO")
        log_file.write(f"[{datetime.now()}] 티커 목록 로드 완료: {len(popular_tickers)}개\n")
        log_file.flush()
        
        last_ticker_update = datetime.now()
        
        loop_count = 0  # 루프 카운터 추가
        
        log_file.write(f"[{datetime.now()}] while 루프 진입 준비, bot_state['running'] = {bot_state['running']}\n")
        log_file.flush()
        
        while bot_state['running']:
            try:
                loop_count += 1
                log_file.write(f"[{datetime.now()}] 루프 #{loop_count} 시작\n")
                log_file.flush()
                
                log(f"[{user_id}] 🔄 루프 #{loop_count} 시작", "INFO")
                
                # 0. 티커 목록 갱신 (30분마다) - 스킵 (고정 목록 사용)
                # time_since_update = (datetime.now() - last_ticker_update).total_seconds() / 60
                # if time_since_update >= 30:
                #     log(f"[{user_id}] 📊 거래량 기반 티커 목록 갱신 중...", "INFO")
                #     popular_tickers = get_top_volume_tickers_fast(50)
                #     last_ticker_update = datetime.now()
                #     log(f"[{user_id}] ✅ 티커 목록 갱신 완료 (50개)", "SUCCESS")
                
                # 1. 복구 모드 체크
                log_file.write(f"[{datetime.now()}] 복구 모드 체크 시작\n")
                log_file.flush()
                
                if not bot_state['recovery_mode_active']:
                    check_recovery_mode_activation(bot_state)
                
                log_file.write(f"[{datetime.now()}] 복구 모드 체크 완료\n")
                log_file.flush()
                
                # 2. 보유 포지션 관리
                log_file.write(f"[{datetime.now()}] 보유 포지션 관리 시작, holdings count: {len(bot_state['simulation_holdings'])}\n")
                log_file.flush()
                
                for ticker, holding in list(bot_state['simulation_holdings'].items()):
                    log_file.write(f"[{datetime.now()}]   - {ticker} check_exit 호출\n")
                    log_file.flush()
                    
                    should_exit, reason = check_exit(ticker, holding, bot_state)
                    
                    log_file.write(f"[{datetime.now()}]   - {ticker} check_exit 결과: {should_exit}\n")
                    log_file.flush()
                    
                    if should_exit:
                        execute_exit(ticker, holding, reason, bot_state)
                
                log_file.write(f"[{datetime.now()}] 보유 포지션 관리 완료\n")
                log_file.flush()
                
                # 3. 신규 진입
                log_file.write(f"[{datetime.now()}] 신규 진입 체크 시작\n")
                log_file.flush()
                
                max_positions = 1 if bot_state['recovery_mode_active'] else 3
                current_holdings = len(bot_state['simulation_holdings'])
                
                log_file.write(f"[{datetime.now()}] max_positions={max_positions}, current_holdings={current_holdings}, recovery_mode={bot_state['recovery_mode_active']}\n")
                log_file.flush()
                
                log(f"[{user_id}] 📈 보유: {current_holdings}개 / 최대: {max_positions}개 (복구모드: {bot_state['recovery_mode_active']})", "INFO")
                
                log_file.write(f"[{datetime.now()}] 진입 조건 체크: {current_holdings} < {max_positions} = {current_holdings < max_positions}\n")
                log_file.flush()
                
                if current_holdings < max_positions:
                    log_file.write(f"[{datetime.now()}] 신규 진입 조건 충족! 진입 가능\n")
                    log_file.flush()
                    
                    # 복구 모드
                    if bot_state['recovery_mode_active']:
                        log_file.write(f"[{datetime.now()}] 복구 모드 진입 로직\n")
                        log_file.flush()
                        # 쿨다운
                        if bot_state['last_loss_time']:
                            cooldown = (datetime.now() - bot_state['last_loss_time']).total_seconds()
                            if cooldown < 120:
                                time.sleep(5)
                                continue
                        
                        opportunities = find_recovery_opportunity(popular_tickers[:10], bot_state)
                        if opportunities:
                            best = opportunities[0]
                            execute_trade(best['ticker'], 'surge_hunter', {'recovery': best}, bot_state)
                    
                    # 일반 모드 - 더 많은 코인을 스캔하여 거래 기회 증가
                    else:
                        log_file.write(f"[{datetime.now()}] 일반 모드 스캔 시작\n")
                        log_file.flush()
                        
                        import random
                        # 15개 → 더 많은 기회
                        scan_tickers = random.sample(popular_tickers, min(15, len(popular_tickers)))
                        
                        log_file.write(f"[{datetime.now()}] 스캔 티커 선택 완료: {len(scan_tickers)}개 - {scan_tickers[:5]}\n")
                        log_file.flush()
                        
                        log(f"[{user_id}] 📊 {len(scan_tickers)}개 티커 스캔 중...", "INFO")  # 재활성화
                        
                        log_file.write(f"[{datetime.now()}] 스캔 루프 시작\n")
                        log_file.flush()
                        
                        best_opportunity = None
                        best_score = 0.0
                        
                        for ticker in scan_tickers:
                            log_file.write(f"[{datetime.now()}]   스캔: {ticker}\n")
                            log_file.flush()
                            
                            try:
                                patterns = analyze_all_patterns(ticker)
                                log_file.write(f"[{datetime.now()}]   {ticker} patterns: {patterns is not None}\n")
                                log_file.flush()
                                
                                if patterns:
                                    bot_state['current_patterns'][ticker] = patterns
                                    best_strategy, score = select_best_strategy(ticker, patterns)
                                    
                                    # 점수가 0.01 이상이면 후보로 저장 (매우 낮은 진입 장벽)
                                    if best_strategy and score > 0.01:
                                        if score > best_score:
                                            best_score = score
                                            best_opportunity = (ticker, best_strategy, patterns, score)
                            except Exception as ticker_error:
                                log(f"[{user_id}] ⚠️ {ticker} 분석 오류: {ticker_error}", "WARNING")
                                continue
                        
                        # 최고 점수 기회로 진입
                        if best_opportunity:
                            ticker, strategy, patterns, score = best_opportunity
                            log(f"[{user_id}] 🎯 {ticker} 매수 신호 감지 (전략: {strategy}, 점수: {score:.2f})", "SUCCESS")
                            execute_trade(ticker, strategy, patterns, bot_state)
                            time.sleep(2)
                        else:
                            log(f"[{user_id}] ⏳ 거래 기회 없음, 대기 중...", "INFO")
                        
                        log(f"[{user_id}] ✅ 스캔 완료", "INFO")
                
                bot_state['last_update'] = datetime.now()
                sleep_time = 15 if bot_state['recovery_mode_active'] else 20
                log(f"[{user_id}] 💤 {sleep_time}초 대기...", "INFO")
                time.sleep(sleep_time)
                
            except Exception as e:
                log(f"[{user_id}] ❌ 메인 루프 오류: {e}", "ERROR")
                import traceback
                traceback.print_exc()
                log(f"[{user_id}] 🔄 10초 후 재시도...", "WARNING")
                time.sleep(10)
        
        log("🛑 봇 중지", "WARNING")
        log_file.write(f"[{datetime.now()}] 봇 정상 종료\n")
        log_file.close()
    
    except Exception as e:
        error_msg = f"[{user_id}] ❌ 치명적 오류 발생: {e}"
        log(error_msg, "ERROR")
        
        # 파일에도 기록
        try:
            log_file.write(f"\n{'='*80}\n")
            log_file.write(f"[{datetime.now()}] 치명적 오류:\n")
            log_file.write(f"{error_msg}\n")
            log_file.write(traceback.format_exc())
            log_file.write(f"{'='*80}\n")
            log_file.close()
        except:
            pass
        
        import traceback
        traceback.print_exc()
        bot_state['running'] = False

# ═══════════════════════════════════════════════════════
# 🔐 사용자 인증 API
# ═══════════════════════════════════════════════════════

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    """회원가입"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': '사용자명을 입력해주세요'})
        
        ip_address = request.remote_addr
        result = user_manager.create_user(username, email, ip_address)
        
        if result['success']:
            session['user_id'] = result['user_id']
            session['username'] = result['username']
            session.permanent = True  # 영구 세션 활성화
            
            # 영구 세션 ID 생성 및 쿠키 설정
            persistent_id = save_persistent_session(result['user_id'])
            log(f"✨ 새 사용자 등록: {username} (ID: {result['user_id']})", "SUCCESS")
            
            response = make_response(jsonify(result))
            response.set_cookie(
                'persistent_session_id', 
                persistent_id,
                max_age=30*24*60*60,  # 30일
                httponly=True,
                samesite='Lax'
            )
            return response
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """로그인"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': '사용자명을 입력해주세요'})
        
        user = user_manager.get_user_by_username(username)
        
        if not user:
            return jsonify({'success': False, 'message': '존재하지 않는 사용자입니다'})
        
        if not user['is_active']:
            return jsonify({'success': False, 'message': '비활성화된 계정입니다'})
        
        # 세션 저장
        session['user_id'] = user['id']
        session['username'] = user['username']
        session.permanent = True  # 영구 세션 활성화
        
        # 영구 세션 ID 생성 및 쿠키 설정
        persistent_id = save_persistent_session(user['id'])
        
        # 마지막 로그인 업데이트
        user_manager.update_last_login(user['id'], request.remote_addr)
        
        log(f"👤 로그인: {username} (ID: {user['id']})", "INFO")
        
        response = make_response(jsonify({
            'success': True,
            'user_id': user['id'],
            'username': user['username']
        }))
        
        response.set_cookie(
            'persistent_session_id', 
            persistent_id,
            max_age=30*24*60*60,  # 30일
            httponly=True,
            samesite='Lax'
        )
        
        return response
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """로그아웃"""
    username = session.get('username', 'Unknown')
    
    # 영구 세션 삭제
    persistent_id = request.cookies.get('persistent_session_id')
    if persistent_id:
        delete_persistent_session(persistent_id)
    
    session.clear()
    
    response = make_response(jsonify({
        'success': True, 
        'message': f'{username}님 로그아웃'
    }))
    
    # 쿠키 삭제
    response.set_cookie('persistent_session_id', '', max_age=0)
    
    return response

@app.route('/api/user/info')
def api_user_info():
    """현재 로그인한 사용자 정보 반환"""
    if 'user_id' in session and 'username' in session:
        return jsonify({
            'success': True,
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session['username']
        })
    else:
        return jsonify({
            'success': True,
            'logged_in': False,
            'username': 'Guest'
        })

# ═══════════════════════════════════════════════════════
# 👨‍💼 관리자 API
# ═══════════════════════════════════════════════════════

# 관리자 권한 체크 데코레이터
def admin_required(f):
    """관리자 권한 필요 (wordycow, lee1만 허용)"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'}), 401
        
        username = session['username']
        if username not in ['wordycow', 'lee1']:
            return jsonify({
                'success': False, 
                'message': f'⛔ 접근 거부: 관리자 권한이 필요합니다 (현재 사용자: {username})'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/admin')
def admin_page():
    """관리자 페이지 - wordycow와 lee1만 접근 가능"""
    # 로그인 체크
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    
    # 관리자 권한 체크
    if username not in ['wordycow', 'lee1']:
        return '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>접근 거부</title>
                <style>
                    body {
                        font-family: 'Inter', sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .error-box {
                        background: white;
                        padding: 60px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        text-align: center;
                        max-width: 500px;
                    }
                    h1 {
                        font-size: 72px;
                        margin: 0 0 20px 0;
                        color: #e74c3c;
                    }
                    h2 {
                        font-size: 28px;
                        margin: 0 0 20px 0;
                        color: #333;
                    }
                    p {
                        font-size: 16px;
                        color: #666;
                        margin-bottom: 30px;
                    }
                    a {
                        display: inline-block;
                        padding: 12px 30px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: 600;
                        transition: transform 0.2s;
                    }
                    a:hover {
                        transform: scale(1.05);
                    }
                </style>
            </head>
            <body>
                <div class="error-box">
                    <h1>🚫</h1>
                    <h2>접근 거부</h2>
                    <p>관리자 페이지는 wordycow와 lee1만 접근할 수 있습니다.</p>
                    <p style="color: #999; font-size: 14px;">현재 사용자: ''' + username + '''</p>
                    <a href="/">대시보드로 돌아가기</a>
                </div>
            </body>
            </html>
        ''', 403
    
    return render_template('admin.html')

# ═══════════════════════════════════════════════════════
# 📊 포트폴리오 API
# ═══════════════════════════════════════════════════════

@app.route('/api/portfolio/get')
def api_get_portfolio():
    """사용자 포트폴리오 조회"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다'}), 401
    
    try:
        portfolio = user_manager.get_user_portfolio(session['user_id'])
        available_coins = get_available_coins()
        
        return jsonify({
            'success': True,
            'portfolio': portfolio,
            'available_coins': available_coins
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/portfolio/update', methods=['POST'])
def api_update_portfolio():
    """포트폴리오 설정 업데이트"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다'}), 401
    
    try:
        data = request.json
        result = user_manager.update_portfolio(
            session['user_id'],
            data.get('coin_1'),
            data.get('coin_2'),
            data.get('coin_3'),
            data.get('coin_4'),
            data.get('investment_per_coin', 10000)
        )
        
        log(f"📊 포트폴리오 업데이트: {session['username']}", "INFO")
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ═══════════════════════════════════════════════════════
# 🔧 관리자 API
# ═══════════════════════════════════════════════════════

@app.route('/admin')
def admin_dashboard():
    """관리자 대시보드 페이지"""
    # 관리자 확인 (세션에 admin 권한이 있거나, 특정 user_id)
    if 'user_id' not in session:
        # 개발 편의: 누구나 접근 가능 (나중에 관리자 로그인 추가)
        pass
    
    return render_template('admin.html')

@app.route('/api/admin/users')
@admin_required
def api_admin_users():
    """전체 사용자 목록 및 통계 (DB + 실행 중인 봇 통합)"""
    try:
        from datetime import datetime  # ✅ 함수 시작 부분에서 import
        
        # 관리자 권한 체크 (TODO: 실제 권한 확인 추가)
        # if session.get('role') != 'admin':
        #     return jsonify({'error': '권한 없음'}), 403
        
        users_list = []
        total_profit_rate = 0
        running_count = 0
        active_subscriptions = 0
        
        # ✅ 1. DB에서 모든 등록 사용자 조회
        import sqlite3
        try:
            conn = sqlite3.connect('upbit_bot.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            db_users = cursor.fetchall()
            conn.close()
        except Exception as db_error:
            log(f"DB 조회 오류 (무시됨): {db_error}", "WARNING")
            db_users = []
        
        # ✅ 2. DB 사용자와 실행 중인 봇 매칭
        processed_users = set()
        
        # DB 사용자 우선 처리
        for db_user in db_users:
            # 기존 DB 스키마: username을 user_id로 사용
            db_dict = dict(db_user)  # ✅ Row를 dict로 변환
            user_id = db_dict.get('user_id') or db_dict.get('username') or f"user_{db_dict.get('id')}"
            if not user_id:
                continue
            
            processed_users.add(user_id)
            
            # DB에서 봇 상태 가져오기 (정확한 seed_amount 사용)
            try:
                conn2 = sqlite3.connect('upbit_bot.db')
                cursor2 = conn2.cursor()
                cursor2.execute('''
                    SELECT running, seed_amount, simulation_krw, simulation_holdings
                    FROM bot_states 
                    WHERE user_id = ?
                ''', (user_id,))
                bot_row = cursor2.fetchone()
                conn2.close()
                
                if bot_row:
                    bot_running, seed, current_krw, holdings_json = bot_row
                    
                    # 보유 코인 가치 계산
                    holdings_value = 0
                    if holdings_json:
                        import json
                        holdings = json.loads(holdings_json)
                        for ticker, holding in holdings.items():
                            try:
                                current_price = pyupbit.get_current_price(ticker)
                                if current_price:
                                    holdings_value += holding['amount'] * current_price
                                else:
                                    holdings_value += holding['amount'] * holding.get('avg_price', 0)
                            except:
                                holdings_value += holding['amount'] * holding.get('avg_price', 0)
                    
                    total_value = current_krw + holdings_value
                    profit = total_value - seed
                    profit_rate = (profit / seed * 100) if seed > 0 else 0
                else:
                    # 봇 상태가 없는 경우
                    seed = 0
                    current_krw = 0
                    total_value = 0
                    profit_rate = 0
                    bot_running = False
            except Exception as e:
                # DB 오류 시 기본값
                seed = 0
                current_krw = 0
                total_value = 0
                profit_rate = 0
                bot_running = False
            
            # 추천 코드 생성
            import hashlib
            referral_code = hashlib.md5(user_id.encode()).hexdigest()[:8].upper()
            
            # DB에서 가져오기 (있으면)
            subscription_expires_at = db_dict.get('subscription_expires_at')
            created_at = db_dict.get('created_at')
            username_display = db_dict.get('username') or user_id.replace('guest_', '게스트_')[:20]
            
            if db_dict.get('referral_code'):
                referral_code = db_dict['referral_code']
            
            user_info = {
                'user_id': user_id,
                'username': username_display,
                'bot_running': bot_running,
                'seed_amount': seed,
                'current_balance': total_value,
                'profit_rate': profit_rate,
                'subscription_expires_at': subscription_expires_at,
                'referral_code': referral_code,
                'created_at': created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            users_list.append(user_info)
            total_profit_rate += profit_rate
            
            if bot_running:
                running_count += 1
            
            # 구독 활성 확인
            if db_dict.get('subscription_expires_at'):
                try:
                    expires = datetime.fromisoformat(db_dict['subscription_expires_at'])
                    if expires > datetime.now():
                        active_subscriptions += 1
                except:
                    pass
        
        # ✅ 3. 게스트 사용자 (DB에 없지만 봇만 실행 중)
        for user_id, bot_state in user_bots.items():
            if user_id in processed_users:
                continue  # 이미 처리됨
            # 현재 잔고 계산
            current_krw = bot_state.get('simulation_krw', 0)
            
            # 보유 코인 가치
            holdings_value = 0
            for ticker, holding in bot_state.get('simulation_holdings', {}).items():
                try:
                    current_price = pyupbit.get_current_price(ticker)
                    if current_price:
                        holdings_value += holding['amount'] * current_price
                    else:
                        holdings_value += holding['amount'] * holding['avg_price']
                except:
                    holdings_value += holding['amount'] * holding.get('avg_price', 0)
            
            total_value = current_krw + holdings_value
            seed = bot_state.get('simulation_start_seed', 1000000)
            profit = total_value - seed
            profit_rate = (profit / seed * 100) if seed > 0 else 0
            
            # 사용자 정보
            # 추천 코드 생성 (user_id 기반)
            import hashlib
            referral_code = hashlib.md5(user_id.encode()).hexdigest()[:8].upper()
            
            user_info = {
                'user_id': user_id,
                'username': user_id.replace('guest_', '게스트_')[:20],
                'bot_running': bot_state.get('running', False),
                'seed_amount': seed,
                'current_balance': total_value,
                'profit_rate': profit_rate,
                'subscription_expires_at': None,  # TODO: DB에서 조회
                'referral_code': referral_code,
                'created_at': bot_state.get('start_time', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if bot_state.get('start_time') else None
            }
            
            users_list.append(user_info)
            total_profit_rate += profit_rate
            
            if bot_state.get('running'):
                running_count += 1
        
        # 통계 계산 (가중평균)
        total_users = len(users_list)
        
        # 금액 비율 가중평균 계산
        total_seed = sum(u['seed_amount'] for u in users_list if u['seed_amount'] > 0)
        weighted_profit_rate = 0
        
        if total_seed > 0:
            for user in users_list:
                if user['seed_amount'] > 0:
                    weight = user['seed_amount'] / total_seed
                    weighted_profit_rate += user['profit_rate'] * weight
        
        # 단순 평균도 계산 (비교용)
        simple_average_profit_rate = (total_profit_rate / total_users) if total_users > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'running_bots': running_count,
                'active_subscriptions': active_subscriptions,
                'average_profit_rate': weighted_profit_rate,  # 가중평균
                'simple_average_profit_rate': simple_average_profit_rate,  # 단순평균
                'total_seed': total_seed
            },
            'users': users_list
        })
        
    except Exception as e:
        log(f"관리자 API 오류: {e}", "ERROR")
        return jsonify({'error': str(e)}), 500

@admin_required
@app.route('/api/admin/subscription/set-date', methods=['POST'])
def api_admin_set_subscription_date():
    """구독 만료일 설정 (관리자 전용)"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        expires_at = data.get('expires_at')  # 'YYYY-MM-DD' 형식
        
        if not user_id or not expires_at:
            return jsonify({'success': False, 'message': '사용자 ID와 날짜 필요'}), 400
        
        # DB에 저장
        import sqlite3
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        # 사용자 존재 확인 및 업데이트
        cursor.execute('''
            UPDATE users 
            SET subscription_expires_at = ?
            WHERE username = ?
        ''', (expires_at, user_id))
        
        if cursor.rowcount == 0:
            # 사용자가 없으면 생성
            cursor.execute('''
                INSERT INTO users (username, subscription_expires_at, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (user_id, expires_at))
        
        conn.commit()
        conn.close()
        
        log(f"[Admin] {user_id} 구독 만료일 설정: {expires_at}", "SUCCESS")
        
        return jsonify({
            'success': True,
            'message': f'{user_id} 구독 만료일이 {expires_at}로 설정되었습니다'
        })
        
    except Exception as e:
        log(f"날짜 설정 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_required
@app.route('/api/admin/subscription/add-days', methods=['POST'])
def api_admin_add_days():
    """구독 일수 추가 (관리자 전용)"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        days = data.get('days', 1)  # 기본 1일
        
        if not user_id:
            return jsonify({'success': False, 'message': '사용자 ID 필요'}), 400
        
        if days <= 0:
            return jsonify({'success': False, 'message': '유효한 일수를 입력하세요'}), 400
        
        # DB에서 현재 만료일 조회 후 +days
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT subscription_expires_at FROM users
            WHERE username = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result and result[0]:
            # 기존 만료일이 있으면 거기에 추가
            current_expires = datetime.strptime(result[0], '%Y-%m-%d')
            new_expires = current_expires + timedelta(days=days)
        else:
            # 만료일이 없으면 오늘부터 계산
            new_expires = datetime.now() + timedelta(days=days)
        
        new_expires_str = new_expires.strftime('%Y-%m-%d')
        
        # 업데이트
        cursor.execute('''
            UPDATE users 
            SET subscription_expires_at = ?
            WHERE username = ?
        ''', (new_expires_str, user_id))
        
        if cursor.rowcount == 0:
            # 사용자가 없으면 생성
            cursor.execute('''
                INSERT INTO users (username, subscription_expires_at, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (user_id, new_expires_str))
        
        conn.commit()
        conn.close()
        
        log(f"[Admin] {user_id}에게 +{days}일 추가 → {new_expires_str}", "SUCCESS")
        
        return jsonify({
            'success': True,
            'message': f'{user_id}에게 {days}일이 추가되었습니다 (만료일: {new_expires_str})'
        })
        
    except Exception as e:
        log(f"일수 추가 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_required
@app.route('/api/admin/bot/stop', methods=['POST'])
def api_admin_stop_bot():
    """관리자가 특정 사용자 봇 정지"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '사용자 ID 필요'}), 400
        
        # 봇 상태 가져오기
        bot_state = user_bots.get(user_id)
        
        if not bot_state:
            return jsonify({'success': False, 'message': f'{user_id} 봇을 찾을 수 없습니다'}), 404
        
        if not bot_state.get('running'):
            return jsonify({'success': False, 'message': f'{user_id} 봇이 이미 정지되어 있습니다'}), 400
        
        # 봇 정지
        bot_state['running'] = False
        save_bot_state_to_db(user_id, bot_state)
        
        # 스레드 대기 (최대 5초)
        thread = bot_state.get('thread')
        if thread and thread.is_alive():
            thread.join(timeout=5)
        
        log(f"[Admin] {user_id} 봇 정지됨", "WARNING")
        
        return jsonify({
            'success': True,
            'message': f'{user_id} 봇이 정지되었습니다'
        })
        
    except Exception as e:
        log(f"관리자 봇 정지 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_required
@app.route('/api/admin/bot/start', methods=['POST'])
def api_admin_start_bot():
    """관리자가 특정 사용자 봇 시작"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '사용자 ID 필요'}), 400
        
        # 봇 상태 가져오기
        bot_state = get_user_bot_state(user_id)
        
        if bot_state.get('running'):
            return jsonify({'success': False, 'message': f'{user_id} 봇이 이미 실행 중입니다'}), 400
        
        # 봇 시작
        bot_state['running'] = True
        save_bot_state_to_db(user_id, bot_state)
        
        # 스레드 시작
        thread = threading.Thread(target=bot_main_loop, args=(user_id, bot_state), daemon=True)
        thread.start()
        bot_state['thread'] = thread
        
        log(f"[Admin] {user_id} 봇 시작됨", "SUCCESS")
        
        return jsonify({
            'success': True,
            'message': f'{user_id} 봇이 시작되었습니다'
        })
        
    except Exception as e:
        log(f"관리자 봇 시작 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


# ═══════════════════════════════════════════════════════
# 🧠 이메이 AI 학습 시스템
# ═══════════════════════════════════════════════════════

@app.route('/api/debug/rag_test', methods=['POST'])
def api_debug_rag_test():
    """RAG 디버그 테스트 엔드포인트"""
    try:
        import time
        start_time = time.time()
        
        data = request.json or {}
        query = data.get('query', '').strip()
        mode = data.get('mode', 'auto')  # auto, character, trading
        
        if not query:
            return jsonify({'error': 'Query required'}), 400
        
        # RAG 검색
        retrieved = emei_router._retrieve_best(query, topk=4)
        
        # Context 생성
        context_blocks = []
        if retrieved:
            for i, (score, _id, qtext, atext, qscore, use_count) in enumerate(retrieved):
                context_blocks.append(f"[{i+1}] Q: {qtext[:100]}... A: {atext[:100]}... (score: {score:.4f})")
        
        context_str = "\n".join(context_blocks)
        context_length = len(context_str)
        
        # Best score 계산
        best_score = retrieved[0][0] if retrieved else 0.0  # score is first element
        threshold = float(os.getenv('EMIE_DB_THRESHOLD', '0.62'))
        
        # Answer 생성 (간단하게 top-1 사용)
        if best_score >= threshold and retrieved:
            answer = retrieved[0][3]  # atext from top result
            answer_source = 'db'
        else:
            answer = f"(DB threshold {threshold} not met, would fallback to Ollama with context)"
            answer_source = 'ollama_context'
        
        # Retrieved sources 상세 정보
        sources_list = []
        for idx, (score, _id, qtext, atext, qscore, use_count) in enumerate(retrieved):
            sources_list.append({
                'rank': idx + 1,
                'id': _id,
                'question': qtext[:200],
                'answer': atext[:200],
                'score': round(score, 4),
                'quality_score': round(qscore, 2),
                'use_count': use_count
            })
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            'query': query,
            'mode': mode,
            'answer': answer,
            'answer_source': answer_source,
            'retrieved_sources': sources_list,
            'context_length': context_length,
            'db_threshold': threshold,
            'best_score': round(best_score, 4),
            'latency_ms': round(latency_ms, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        log(f"[RAG_TEST] query='{query}' | top_score={best_score:.4f} | sources={len(sources_list)} | latency={latency_ms:.0f}ms", "INFO")
        
        return jsonify(result)
        
    except Exception as e:
        log(f"RAG 테스트 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/emei/chat', methods=['POST'])
def api_emei_chat():
    """이메이 채팅 - 새 Router 시스템"""
    try:
        # 세션 확인
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '로그인 필요'}), 401
        
        user_id = session.get('user_id')
        data = request.json or {}
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'message': '메시지를 입력해주세요'}), 400
        
        # 🧠 새로운 Router 시스템 사용 (DB → Ollama 폴백)
        result = emei_router.chat(user_id=user_id, message=message)
        
        return jsonify({
            'success': True,
            'response': result['response'],
            'learned': result.get('learned', False),
            'response_time': result.get('response_time', 0)
        })
        
    except Exception as e:
        log(f"이메이 채팅 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/emei/stats')
def api_emei_stats():
    """이메이 학습 통계 (Enhanced)"""
    try:
        emei = get_enhanced_emei()
        user_id = session.get('user_id', 'guest')
        stats = emei.get_user_stats(user_id)
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/debug/rag_test')
def debug_rag_test():
    """🔍 RAG 작동 검증 엔드포인트 (STEP 1)"""
    try:
        import time
        query = request.args.get('query', '급등 포착하는 방법')
        
        t0 = time.time()
        
        # 1. DB 검색 수행
        best = emei_router._retrieve_best(query, topk=4)
        
        # 2. 검색 결과 정리
        retrieved_sources = []
        for score, _id, q, a, qscore, use_count in best:
            retrieved_sources.append({
                'id': _id,
                'question': q,
                'answer': a[:100] + '...' if len(a) > 100 else a,
                'score': round(score, 4),
                'quality': qscore,
                'use_count': use_count
            })
        
        # 3. 컨텍스트 생성 (LLM에 주입될 내용)
        context_blocks = []
        if best:
            lines = ["[참고 지식 후보 Top]"]
            for score, _id, q, a, qscore, use_count in best:
                lines.append(f"- Q: {q}\n  A: {a}")
            context_blocks.append("\n".join(lines))
        
        injected_context = context_blocks[0] if context_blocks else ""
        
        # 4. LLM 호출 (실제 답변 생성)
        user_pattern = {'formality_level': 'casual', 'emotion': 'neutral'}
        system = emei_router._emei_system_prompt(user_pattern, user_id='debug_user')
        
        try:
            answer = emei_router._ollama_chat(
                system=system,
                user=query,
                context_blocks=context_blocks,
                temperature=0.4
            )
        except Exception as e:
            answer = f"[Ollama 오류: {e}]"
        
        latency = round(time.time() - t0, 3)
        
        return jsonify({
            'success': True,
            'query': query,
            'retrieved_sources': retrieved_sources,
            'injected_context': injected_context[:500] + '...' if len(injected_context) > 500 else injected_context,
            'context_length': len(injected_context),
            'answer': answer,
            'latency_seconds': latency,
            'db_threshold': float(os.getenv("EMEI_DB_THRESHOLD", "0.62")),
            'top_score': best[0][0] if best else 0.0
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == "__main__":
    log_separator()
    log("🚀 업비트 AI 트레이딩 봇 v8.0 ULTIMATE", "SUCCESS")
    log("💎 급등/급락 + AI학습 + 손실복구 = 완전체!", "INFO")
    log_separator()
    
    # 🔄 서버 시작 시 실행 중이던 봇 자동 복구
    try:
        running_bots = get_all_running_bots()
        if running_bots:
            log(f"🔄 {len(running_bots)}개의 봇 자동 복구 중...", "INFO")
            for bot_data in running_bots:
                user_id = bot_data['user_id']
                
                # 봇 상태 복원
                bot_state = get_user_bot_state(user_id)
                bot_state['running'] = True
                bot_state['mode'] = bot_data['mode']
                bot_state['simulation_start_seed'] = bot_data['seed_amount']
                bot_state['simulation_krw'] = bot_data['simulation_krw']
                
                # simulation_holdings 복원 및 entry_time 변환
                holdings = json.loads(bot_data['simulation_holdings'])
                for ticker, holding in holdings.items():
                    # entry_time이 문자열이면 datetime 객체로 변환
                    if isinstance(holding.get('entry_time'), str):
                        holding['entry_time'] = datetime.strptime(holding['entry_time'], '%Y-%m-%d %H:%M:%S.%f')
                
                bot_state['simulation_holdings'] = holdings
                bot_state['recovery_mode_active'] = bool(bot_data['recovery_mode_active'])
                
                # 스레드 시작
                thread = threading.Thread(target=bot_main_loop, args=(user_id, bot_state), daemon=True)
                thread.start()
                bot_state['thread'] = thread
                
                log(f"  ✅ [{user_id}] 봇 복구 완료 (모드: {bot_data['mode']}, 시드: {bot_data['seed_amount']:,}원)", "SUCCESS")
            
            log(f"🎉 모든 봇 복구 완료!", "SUCCESS")
        else:
            log("📭 복구할 봇 없음", "INFO")
    except Exception as e:
        log(f"❌ 봇 복구 실패: {e}", "ERROR")
        import traceback
        traceback.print_exc()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
