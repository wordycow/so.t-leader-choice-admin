#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 초기화 스크립트
사용자 계정, 구독, 포트폴리오, 거래 내역 관리
"""

import sqlite3
from datetime import datetime

def init_database():
    conn = sqlite3.connect('upbit_bot.db')
    cursor = conn.cursor()
    
    # ═══════════════════════════════════════════════════════
    # 📋 테이블 1: 사용자 (users)
    # ═══════════════════════════════════════════════════════
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        ip_address TEXT,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # ═══════════════════════════════════════════════════════
    # 📋 테이블 2: 구독 정보 (subscriptions)
    # ═══════════════════════════════════════════════════════
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        txid TEXT,
        usdt_amount REAL,
        subscription_type TEXT,  -- 1month, 6months, lifetime
        start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_date TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # ═══════════════════════════════════════════════════════
    # 📋 테이블 3: 포트폴리오 설정 (portfolios)
    # ═══════════════════════════════════════════════════════
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        coin_1 TEXT DEFAULT 'KRW-BTC',
        coin_2 TEXT DEFAULT 'KRW-XRP',
        coin_3 TEXT DEFAULT 'KRW-SOL',
        coin_4 TEXT DEFAULT 'KRW-SHIB',
        investment_per_coin INTEGER DEFAULT 10000,
        is_active BOOLEAN DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # ═══════════════════════════════════════════════════════
    # 📋 테이블 4: 거래 내역 (trades)
    # ═══════════════════════════════════════════════════════
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ticker TEXT NOT NULL,
        trade_type TEXT NOT NULL,  -- BUY, SELL
        amount REAL NOT NULL,
        price REAL NOT NULL,
        strategy TEXT,
        reason TEXT,  -- 매수/매도 이유
        profit_rate REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # ═══════════════════════════════════════════════════════
    # 📋 테이블 5: API 키 (api_keys) - 암호화 필요
    # ═══════════════════════════════════════════════════════
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        access_key TEXT,
        secret_key TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # ═══════════════════════════════════════════════════════
    # 📋 인덱스 생성
    # ═══════════════════════════════════════════════════════
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)')
    
    conn.commit()
    conn.close()
    
    print("✅ 데이터베이스 초기화 완료!")
    print("📊 생성된 테이블: users, subscriptions, portfolios, trades, api_keys")

if __name__ == '__main__':
    init_database()
