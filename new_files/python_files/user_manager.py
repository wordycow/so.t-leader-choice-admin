#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자 관리 모듈
계정 생성, 로그인, 세션 관리, 구독 확인
"""

import sqlite3
from datetime import datetime, timedelta
import hashlib
import secrets

class UserManager:
    def __init__(self, db_path='upbit_bot.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def create_user(self, username, email=None, ip_address=None):
        """사용자 계정 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, ip_address, created_at, last_login)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, ip_address, datetime.now(), datetime.now()))
            
            user_id = cursor.lastrowid
            
            # 기본 포트폴리오 설정 추가
            cursor.execute('''
                INSERT INTO portfolios (user_id, coin_1, coin_2, coin_3, coin_4)
                VALUES (?, 'KRW-BTC', 'KRW-XRP', 'KRW-SOL', 'KRW-SHIB')
            ''', (user_id,))
            
            conn.commit()
            return {'success': True, 'user_id': user_id, 'username': username}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': '이미 존재하는 사용자명입니다.'}
        finally:
            conn.close()
    
    def get_user_by_username(self, username):
        """사용자명으로 사용자 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'created_at': user[3],
                'last_login': user[4],
                'ip_address': user[5],
                'is_active': user[6]
            }
        return None
    
    def update_last_login(self, user_id, ip_address):
        """마지막 로그인 시간 업데이트"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET last_login = ?, ip_address = ?
            WHERE id = ?
        ''', (datetime.now(), ip_address, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_portfolio(self, user_id):
        """사용자 포트폴리오 설정 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT coin_1, coin_2, coin_3, coin_4, investment_per_coin
            FROM portfolios
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        
        portfolio = cursor.fetchone()
        conn.close()
        
        if portfolio:
            return {
                'coin_1': portfolio[0],
                'coin_2': portfolio[1],
                'coin_3': portfolio[2],
                'coin_4': portfolio[3],
                'investment_per_coin': portfolio[4]
            }
        return None
    
    def update_portfolio(self, user_id, coin_1, coin_2, coin_3, coin_4, investment_per_coin=10000):
        """포트폴리오 설정 업데이트"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE portfolios
            SET coin_1 = ?, coin_2 = ?, coin_3 = ?, coin_4 = ?, 
                investment_per_coin = ?, updated_at = ?
            WHERE user_id = ?
        ''', (coin_1, coin_2, coin_3, coin_4, investment_per_coin, datetime.now(), user_id))
        
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def add_subscription(self, user_id, txid, usdt_amount, subscription_type):
        """구독 추가"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 구독 기간 계산
        start_date = datetime.now()
        if subscription_type == '1month':
            end_date = start_date + timedelta(days=30)
        elif subscription_type == '6months':
            end_date = start_date + timedelta(days=180)
        elif subscription_type == 'lifetime':
            end_date = start_date + timedelta(days=36500)  # 100년
        else:
            end_date = start_date + timedelta(days=30)
        
        cursor.execute('''
            INSERT INTO subscriptions (user_id, txid, usdt_amount, subscription_type, start_date, end_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (user_id, txid, usdt_amount, subscription_type, start_date, end_date))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'end_date': end_date.isoformat()}
    
    def check_subscription(self, user_id):
        """구독 상태 확인"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT subscription_type, end_date, is_active
            FROM subscriptions
            WHERE user_id = ? AND is_active = 1 AND end_date > ?
            ORDER BY end_date DESC
            LIMIT 1
        ''', (user_id, datetime.now()))
        
        sub = cursor.fetchone()
        conn.close()
        
        if sub:
            return {
                'is_subscribed': True,
                'subscription_type': sub[0],
                'end_date': sub[1]
            }
        return {'is_subscribed': False}
    
    def log_trade(self, user_id, ticker, trade_type, amount, price, strategy, reason, profit_rate=None):
        """거래 내역 기록"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (user_id, ticker, trade_type, amount, price, strategy, reason, profit_rate, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, ticker, trade_type, amount, price, strategy, reason, profit_rate, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        """모든 사용자 목록 조회 (관리자용)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.created_at, u.last_login, u.is_active,
                   s.subscription_type, s.end_date, s.is_active as sub_active
            FROM users u
            LEFT JOIN subscriptions s ON u.id = s.user_id AND s.is_active = 1
            ORDER BY u.created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        return [{
            'id': u[0],
            'username': u[1],
            'email': u[2],
            'created_at': u[3],
            'last_login': u[4],
            'is_active': u[5],
            'subscription_type': u[6],
            'subscription_end': u[7],
            'is_subscribed': bool(u[8])
        } for u in users]
