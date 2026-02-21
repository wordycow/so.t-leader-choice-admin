import sqlite3
from datetime import datetime, timedelta
import secrets

def init_database():
    """데이터베이스 초기화 - v2 (추천 시스템 포함)"""
    conn = sqlite3.connect('upbit_bot.db')
    cursor = conn.cursor()
    
    # 사용자 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        username TEXT,
        email TEXT,
        password_hash TEXT,
        referral_code TEXT UNIQUE,
        referred_by TEXT,
        subscription_expires_at TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 추천 내역 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id TEXT NOT NULL,
        referred_user_id TEXT NOT NULL,
        bonus_days INTEGER DEFAULT 5,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (referrer_id) REFERENCES users(user_id),
        FOREIGN KEY (referred_user_id) REFERENCES users(user_id)
    )
    ''')
    
    # 구독 변경 내역 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscription_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        old_expires_at TEXT,
        new_expires_at TEXT,
        change_reason TEXT,
        changed_by TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ 데이터베이스 초기화 완료 (추천 시스템 포함)")

def generate_referral_code():
    """고유 추천 코드 생성"""
    return secrets.token_urlsafe(8).upper()[:8]

def add_referral_bonus(referrer_id, referred_user_id, bonus_days=5):
    """추천 보너스 지급"""
    conn = sqlite3.connect('upbit_bot.db')
    cursor = conn.cursor()
    
    try:
        # 추천인 현재 만료일 조회
        cursor.execute('SELECT subscription_expires_at FROM users WHERE user_id = ?', (referrer_id,))
        result = cursor.fetchone()
        
        if result:
            current_expires = result[0]
            if current_expires:
                # 기존 만료일에서 +5일
                expires_dt = datetime.fromisoformat(current_expires)
            else:
                # 만료일 없으면 오늘부터 +5일
                expires_dt = datetime.now()
            
            new_expires = expires_dt + timedelta(days=bonus_days)
            
            # 업데이트
            cursor.execute('''
                UPDATE users 
                SET subscription_expires_at = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (new_expires.isoformat(), referrer_id))
            
            # 추천 내역 기록
            cursor.execute('''
                INSERT INTO referrals (referrer_id, referred_user_id, bonus_days)
                VALUES (?, ?, ?)
            ''', (referrer_id, referred_user_id, bonus_days))
            
            # 변경 로그
            cursor.execute('''
                INSERT INTO subscription_logs (user_id, old_expires_at, new_expires_at, change_reason, changed_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (referrer_id, current_expires, new_expires.isoformat(), f'추천 보너스 (+{bonus_days}일)', 'SYSTEM'))
            
            conn.commit()
            print(f"✅ {referrer_id}에게 {bonus_days}일 보너스 지급")
            return True
    
    except Exception as e:
        print(f"❌ 보너스 지급 실패: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
