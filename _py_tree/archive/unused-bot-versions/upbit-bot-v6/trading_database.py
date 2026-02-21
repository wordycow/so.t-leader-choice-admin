#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 트레이딩 데이터베이스 및 학습 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
모든 거래의 이유와 결과를 기록하고 학습합니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class TradingDatabase:
    """트레이딩 데이터베이스 관리"""
    
    def __init__(self, db_path="trading_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 시뮬레이션 세션 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulation_sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                initial_seed INTEGER NOT NULL,
                final_balance INTEGER,
                profit INTEGER,
                profit_rate REAL,
                total_trades INTEGER DEFAULT 0,
                win_trades INTEGER DEFAULT 0,
                lose_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                strategy_config TEXT,
                status TEXT DEFAULT 'running'
            )
        """)
        
        # 거래 내역 테이블 (매수/매도의 명확한 이유 포함)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                ticker TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL,
                
                -- 매수 이유
                buy_reason TEXT,
                buy_stage INTEGER,
                rsi_value REAL,
                rsi_range_min REAL,
                rsi_range_max REAL,
                drop_percent REAL,
                bollinger_position TEXT,
                volume_change REAL,
                
                -- 매도 이유
                sell_reason TEXT,
                sell_stage INTEGER,
                profit REAL,
                profit_rate REAL,
                hold_time INTEGER,
                target_profit REAL,
                
                -- 시장 상황
                market_condition TEXT,
                price_change_24h REAL,
                volume_24h REAL,
                
                -- 결과
                is_successful BOOLEAN,
                lesson_learned TEXT,
                
                FOREIGN KEY (session_id) REFERENCES simulation_sessions(session_id)
            )
        """)
        
        # 전략 성과 분석 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                buy_config TEXT NOT NULL,
                sell_config TEXT NOT NULL,
                test_count INTEGER DEFAULT 0,
                avg_profit_rate REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                max_profit REAL DEFAULT 0,
                max_loss REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                is_best BOOLEAN DEFAULT 0
            )
        """)
        
        # 학습 데이터 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                condition_type TEXT NOT NULL,
                condition_data TEXT NOT NULL,
                action TEXT NOT NULL,
                result REAL NOT NULL,
                success_rate REAL DEFAULT 0,
                sample_count INTEGER DEFAULT 1
            )
        """)
        
        conn.commit()
        conn.close()
    
    def start_session(self, session_id: str, initial_seed: int, strategy_config: Dict) -> bool:
        """시뮬레이션 세션 시작"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO simulation_sessions 
                (session_id, start_time, initial_seed, strategy_config, status)
                VALUES (?, ?, ?, ?, 'running')
            """, (
                session_id,
                datetime.now().isoformat(),
                initial_seed,
                json.dumps(strategy_config, ensure_ascii=False)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"세션 시작 오류: {e}")
            return False
    
    def record_trade(self, session_id: str, trade_data: Dict) -> bool:
        """
        거래 기록 (명확한 이유 포함)
        
        trade_data = {
            'timestamp': '2026-02-15 10:30:00',
            'trade_type': 'BUY' or 'SELL',
            'ticker': 'KRW-BTC',
            'amount': 0.001,
            'price': 50000000,
            'total': 50000,
            
            # 매수 시
            'buy_reason': 'RSI 과매도 구간 진입',
            'buy_stage': 1,
            'rsi_value': 28.5,
            'rsi_range': (28, 30),
            'drop_percent': 0,
            'bollinger_position': 'lower',
            'volume_change': 150.0,
            
            # 매도 시
            'sell_reason': '목표 수익률 달성',
            'sell_stage': 1,
            'profit': 5000,
            'profit_rate': 2.5,
            'hold_time': 3600,
            'target_profit': 2.5,
            
            # 시장 상황
            'market_condition': 'bearish',
            'price_change_24h': -5.2,
            'volume_24h': 1000000,
            
            # 결과
            'is_successful': True,
            'lesson_learned': '낮은 RSI에서 매수가 효과적'
        }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO trades (
                    session_id, timestamp, trade_type, ticker, amount, price, total,
                    buy_reason, buy_stage, rsi_value, rsi_range_min, rsi_range_max,
                    drop_percent, bollinger_position, volume_change,
                    sell_reason, sell_stage, profit, profit_rate, hold_time, target_profit,
                    market_condition, price_change_24h, volume_24h,
                    is_successful, lesson_learned
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                trade_data.get('timestamp', datetime.now().isoformat()),
                trade_data['trade_type'],
                trade_data['ticker'],
                trade_data['amount'],
                trade_data['price'],
                trade_data['total'],
                
                trade_data.get('buy_reason'),
                trade_data.get('buy_stage'),
                trade_data.get('rsi_value'),
                trade_data.get('rsi_range', (0, 0))[0],
                trade_data.get('rsi_range', (0, 0))[1],
                trade_data.get('drop_percent'),
                trade_data.get('bollinger_position'),
                trade_data.get('volume_change'),
                
                trade_data.get('sell_reason'),
                trade_data.get('sell_stage'),
                trade_data.get('profit'),
                trade_data.get('profit_rate'),
                trade_data.get('hold_time'),
                trade_data.get('target_profit'),
                
                trade_data.get('market_condition'),
                trade_data.get('price_change_24h'),
                trade_data.get('volume_24h'),
                
                trade_data.get('is_successful'),
                trade_data.get('lesson_learned')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"거래 기록 오류: {e}")
            return False
    
    def end_session(self, session_id: str, final_balance: int) -> bool:
        """시뮬레이션 세션 종료"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 세션 정보 가져오기
            cursor.execute("""
                SELECT initial_seed FROM simulation_sessions WHERE session_id = ?
            """, (session_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            initial_seed = result[0]
            profit = final_balance - initial_seed
            profit_rate = (profit / initial_seed * 100) if initial_seed > 0 else 0
            
            # 거래 통계 계산
            cursor.execute("""
                SELECT COUNT(*), 
                       SUM(CASE WHEN is_successful = 1 THEN 1 ELSE 0 END),
                       SUM(CASE WHEN is_successful = 0 THEN 1 ELSE 0 END)
                FROM trades 
                WHERE session_id = ? AND trade_type = 'SELL'
            """, (session_id,))
            
            stats = cursor.fetchone()
            total_trades = stats[0] or 0
            win_trades = stats[1] or 0
            lose_trades = stats[2] or 0
            win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
            
            # 세션 업데이트
            cursor.execute("""
                UPDATE simulation_sessions
                SET end_time = ?,
                    final_balance = ?,
                    profit = ?,
                    profit_rate = ?,
                    total_trades = ?,
                    win_trades = ?,
                    lose_trades = ?,
                    win_rate = ?,
                    status = 'completed'
                WHERE session_id = ?
            """, (
                datetime.now().isoformat(),
                final_balance,
                profit,
                profit_rate,
                total_trades,
                win_trades,
                lose_trades,
                win_rate,
                session_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"세션 종료 오류: {e}")
            return False
    
    def get_session_history(self, limit: int = 10) -> List[Dict]:
        """최근 세션 히스토리 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM simulation_sessions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                session = dict(zip(columns, row))
                if session['strategy_config']:
                    session['strategy_config'] = json.loads(session['strategy_config'])
                sessions.append(session)
            
            conn.close()
            return sessions
        except Exception as e:
            print(f"히스토리 조회 오류: {e}")
            return []
    
    def get_trades_by_session(self, session_id: str) -> List[Dict]:
        """특정 세션의 거래 내역 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM trades
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (session_id,))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            trades = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            return trades
        except Exception as e:
            print(f"거래 내역 조회 오류: {e}")
            return []
    
    def analyze_buy_reasons(self) -> Dict:
        """매수 이유별 성공률 분석"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    buy_reason,
                    COUNT(*) as total_count,
                    AVG(CASE WHEN is_successful = 1 THEN 1.0 ELSE 0.0 END) * 100 as success_rate,
                    AVG(profit_rate) as avg_profit_rate,
                    MAX(profit_rate) as max_profit_rate,
                    MIN(profit_rate) as min_profit_rate
                FROM trades
                WHERE trade_type = 'SELL' AND buy_reason IS NOT NULL
                GROUP BY buy_reason
                ORDER BY success_rate DESC
            """)
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            analysis = {}
            for row in rows:
                reason = row[0]
                analysis[reason] = {
                    'total_count': row[1],
                    'success_rate': row[2],
                    'avg_profit_rate': row[3],
                    'max_profit_rate': row[4],
                    'min_profit_rate': row[5]
                }
            
            conn.close()
            return analysis
        except Exception as e:
            print(f"매수 이유 분석 오류: {e}")
            return {}
    
    def analyze_rsi_effectiveness(self) -> Dict:
        """RSI 범위별 효과 분석"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    CAST(rsi_value / 5 AS INTEGER) * 5 as rsi_bucket,
                    COUNT(*) as total_count,
                    AVG(CASE WHEN is_successful = 1 THEN 1.0 ELSE 0.0 END) * 100 as success_rate,
                    AVG(profit_rate) as avg_profit_rate
                FROM trades
                WHERE trade_type = 'SELL' AND rsi_value IS NOT NULL
                GROUP BY rsi_bucket
                ORDER BY rsi_bucket ASC
            """)
            
            rows = cursor.fetchall()
            
            analysis = {}
            for row in rows:
                rsi_range = f"{row[0]}-{row[0]+5}"
                analysis[rsi_range] = {
                    'total_count': row[1],
                    'success_rate': row[2],
                    'avg_profit_rate': row[3]
                }
            
            conn.close()
            return analysis
        except Exception as e:
            print(f"RSI 분석 오류: {e}")
            return {}
    
    def get_best_performing_conditions(self, min_samples: int = 10) -> List[Dict]:
        """가장 성공적인 조건들 찾기"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    buy_reason,
                    buy_stage,
                    CAST(rsi_value / 5 AS INTEGER) * 5 as rsi_bucket,
                    COUNT(*) as sample_count,
                    AVG(CASE WHEN is_successful = 1 THEN 1.0 ELSE 0.0 END) * 100 as success_rate,
                    AVG(profit_rate) as avg_profit_rate
                FROM trades
                WHERE trade_type = 'SELL' AND is_successful = 1
                GROUP BY buy_reason, buy_stage, rsi_bucket
                HAVING sample_count >= ?
                ORDER BY success_rate DESC, avg_profit_rate DESC
                LIMIT 10
            """, (min_samples,))
            
            columns = ['buy_reason', 'buy_stage', 'rsi_range', 'sample_count', 'success_rate', 'avg_profit_rate']
            rows = cursor.fetchall()
            
            best_conditions = []
            for row in rows:
                condition = dict(zip(columns, row))
                condition['rsi_range'] = f"{row[2]}-{row[2]+5}"
                best_conditions.append(condition)
            
            conn.close()
            return best_conditions
        except Exception as e:
            print(f"최적 조건 분석 오류: {e}")
            return []

# ═══════════════════════════════════════════════════════
# 🧪 테스트
# ═══════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 60)
    print("📊 트레이딩 데이터베이스 테스트")
    print("=" * 60)
    print()
    
    db = TradingDatabase("test_trading.db")
    
    # 세션 시작
    session_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    strategy = {
        'buy_stages': {1: {'amount': 6000, 'rsi_range': (28, 30)}},
        'sell_stages': {1: {'ratio': 0.5, 'profit_target': 2.5}}
    }
    
    print(f"세션 시작: {session_id}")
    db.start_session(session_id, 1000000, strategy)
    
    # 매수 기록
    buy_trade = {
        'trade_type': 'BUY',
        'ticker': 'KRW-BTC',
        'amount': 0.001,
        'price': 50000000,
        'total': 50000,
        'buy_reason': 'RSI 과매도 구간 진입 (28.5)',
        'buy_stage': 1,
        'rsi_value': 28.5,
        'rsi_range': (28, 30),
        'drop_percent': 0,
        'bollinger_position': 'lower',
        'volume_change': 150.0,
        'market_condition': 'bearish',
        'price_change_24h': -5.2
    }
    
    print("매수 기록...")
    db.record_trade(session_id, buy_trade)
    
    # 매도 기록
    sell_trade = {
        'trade_type': 'SELL',
        'ticker': 'KRW-BTC',
        'amount': 0.001,
        'price': 51250000,
        'total': 51250,
        'sell_reason': '목표 수익률 달성 (2.5%)',
        'sell_stage': 1,
        'profit': 1250,
        'profit_rate': 2.5,
        'hold_time': 3600,
        'target_profit': 2.5,
        'market_condition': 'neutral',
        'price_change_24h': 0.5,
        'is_successful': True,
        'lesson_learned': 'RSI 28-30 구간에서 매수가 효과적'
    }
    
    print("매도 기록...")
    db.record_trade(session_id, sell_trade)
    
    # 세션 종료
    print("세션 종료...")
    db.end_session(session_id, 1001250)
    
    # 히스토리 조회
    print("\n최근 세션 히스토리:")
    sessions = db.get_session_history(5)
    for sess in sessions:
        print(f"  - {sess['session_id']}: 수익률 {sess['profit_rate']:.2f}%")
    
    print("\n✅ 테스트 완료!")
