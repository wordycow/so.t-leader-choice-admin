#!/usr/bin/env python3
"""
봇 상태 영구 저장 모듈
- 재시작 시 자동 복구
- DB에 bot_state 저장
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = 'upbit_bot.db'

def init_bot_state_table():
    """bot_states 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_states (
            user_id TEXT PRIMARY KEY,
            running BOOLEAN DEFAULT 0,
            mode TEXT DEFAULT 'practice',
            seed_amount INTEGER DEFAULT 1000000,
            simulation_krw REAL DEFAULT 0,
            simulation_holdings TEXT DEFAULT '{}',
            recovery_mode_active BOOLEAN DEFAULT 0,
            last_update TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ bot_states 테이블 초기화 완료")

def save_bot_state(user_id, bot_state):
    """봇 상태 저장"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bot_states 
            (user_id, running, mode, seed_amount, simulation_krw, simulation_holdings, 
             recovery_mode_active, last_update)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            bot_state.get('running', False),
            bot_state.get('mode', 'practice'),
            bot_state.get('simulation_start_seed', 1000000),
            bot_state.get('simulation_krw', 0),
            json.dumps(bot_state.get('simulation_holdings', {})),
            bot_state.get('recovery_mode_active', False),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 봇 상태 저장 실패: {e}")
        return False

def load_bot_state(user_id):
    """봇 상태 로드"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM bot_states WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # simulation_holdings 로드 후 entry_time을 datetime으로 변환
            holdings = json.loads(row['simulation_holdings'])
            for ticker, holding in holdings.items():
                if 'entry_time' in holding and isinstance(holding['entry_time'], str):
                    from datetime import datetime
                    holding['entry_time'] = datetime.fromisoformat(holding['entry_time'])
            
            return {
                'running': bool(row['running']),
                'mode': row['mode'],
                'simulation_start_seed': row['seed_amount'],
                'simulation_krw': row['simulation_krw'],
                'simulation_holdings': holdings,
                'recovery_mode_active': bool(row['recovery_mode_active']),
                'last_update': row['last_update']
            }
        return None
    except Exception as e:
        print(f"❌ 봇 상태 로드 실패: {e}")
        return None

def get_all_running_bots():
    """실행 중인 모든 봇 목록"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM bot_states WHERE running = 1')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ 실행 중인 봇 조회 실패: {e}")
        return []

if __name__ == '__main__':
    # 테스트
    init_bot_state_table()
    
    # 실행 중인 봇 확인
    running_bots = get_all_running_bots()
    print(f"\n📊 실행 중인 봇: {len(running_bots)}개")
    for bot in running_bots:
        print(f"  - {bot['user_id']}: {bot['mode']} 모드, {bot['seed_amount']:,}원")
