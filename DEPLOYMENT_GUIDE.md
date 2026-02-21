# 🚀 실제 배포 가이드 - 다중 사용자 서비스

## 현재 상태 vs 실제 배포 필요 사항

### ❌ **현재 문제점**
```
1. 임시 샌드박스 URL (1시간 후 종료)
2. 여러 사람 접속 시 데이터 공유됨 (독립 아님)
3. SQLite 파일 DB (동시 접속 제한)
4. 로그인 UI만 있고 실제 독립 세션 미완성
5. 관리자 대시보드 있지만 실제 구독 관리 안됨
```

### ✅ **배포 후 목표**
```
1. 24/7 항상 켜진 서버
2. 각 사용자별 완전 독립 봇 (A의 거래 ≠ B의 거래)
3. PostgreSQL/MySQL (수천 명 동시 접속 가능)
4. 회원가입 → 로그인 → 개인 대시보드
5. 관리자 페이지 → 구독자 명단, 만료일 관리
```

---

## 🎯 배포 옵션 비교

| 옵션 | 비용 | 난이도 | 소요시간 | 추천 |
|-----|------|--------|---------|------|
| **Railway** | $5~20/월 | ⭐⭐ | 1~2시간 | ✅ 최고 추천 |
| **Heroku** | $7~25/월 | ⭐⭐ | 2시간 | ✅ 추천 |
| **DigitalOcean** | $6~12/월 | ⭐⭐⭐⭐ | 4~6시간 | 전문가용 |
| **AWS EC2** | $5~30/월 | ⭐⭐⭐⭐⭐ | 6~8시간 | 대규모용 |
| **Vercel (프론트)** | 무료~$20 | ⭐⭐ | 3시간 | API 분리 필요 |

---

## 🏆 **추천: Railway 배포 (가장 쉬움)**

### Railway 장점
- ✅ **무료 시작** (월 $5 크레딧 제공)
- ✅ **PostgreSQL 자동 제공**
- ✅ **GitHub 연동 자동 배포**
- ✅ **도메인 무료** (예: your-bot.up.railway.app)
- ✅ **HTTPS 자동 설정**

### Railway 단계별 가이드

#### 1단계: Railway 준비 (5분)
```bash
# Railway 가입
https://railway.app

# GitHub 연동
→ "New Project" → "Deploy from GitHub"
→ wordycow/so.t-leader-choice 선택
```

#### 2단계: 파일 준비 (10분)
Railway 배포를 위해 다음 파일 필요:

**requirements.txt** (의존성)
```
Flask==3.0.0
Flask-CORS==4.0.0
pyupbit==0.2.31
pandas==2.1.3
numpy==1.26.2
python-dotenv==1.0.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
```

**Procfile** (시작 명령)
```
web: gunicorn upbit-smart-bot-v8.0-ULTIMATE:app
```

**railway.json** (설정)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn upbit-smart-bot-v8.0-ULTIMATE:app --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 3단계: PostgreSQL 연결 (15분)
```python
# upbit-smart-bot-v8.0-ULTIMATE.py 상단에 추가
import os
from urllib.parse import urlparse

# Railway PostgreSQL 자동 연결
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # PostgreSQL 사용
    import psycopg2
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
else:
    # 로컬 개발 시 SQLite
    import sqlite3
    conn = sqlite3.connect('upbit_bot.db')
```

#### 4단계: 환경 변수 설정 (5분)
Railway 대시보드에서:
```
SECRET_KEY = your-secret-key-here
DATABASE_URL = (자동 생성됨)
FLASK_ENV = production
```

#### 5단계: 배포! (자동)
```bash
git push origin main
→ Railway가 자동으로 감지하고 배포
→ https://your-bot.up.railway.app 생성됨
```

---

## 🔐 **사용자별 독립 시스템 완성**

### 현재 상태 (80% 완료)
```python
# 이미 구현된 것
user_bots = {}  # 사용자별 봇 상태

def get_user_bot_state(user_id):
    if user_id not in user_bots:
        user_bots[user_id] = create_bot_state()
    return user_bots[user_id]
```

### 추가 필요 (20%)
```python
# 1. 세션 IP 기반 → 실제 user_id 기반으로 변경
@app.route('/api/start', methods=['POST'])
def api_start():
    # ❌ 현재: 테스트용 user_id
    user_id = 'test_user'
    
    # ✅ 변경: 세션에서 실제 user_id
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401
    user_id = session['user_id']
    
    bot_state = get_user_bot_state(user_id)
    # ...

# 2. 로그인 시 세션 저장
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # DB에서 사용자 확인
    user = user_manager.authenticate(username, password)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'success': True})
    else:
        return jsonify({'error': '로그인 실패'}), 401
```

---

## 📊 **관리자 대시보드 완성**

### 현재 상태
- `/admin` 페이지 UI 존재 ✅
- SQLite 테이블 구조 완성 ✅
- 구독자 조회 API 미완성 ❌

### 완성 코드
```python
@app.route('/admin')
def admin():
    # 관리자 확인
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    
    return render_template('admin.html')

@app.route('/api/admin/users')
def api_admin_users():
    # 관리자만 접근
    if session.get('role') != 'admin':
        return jsonify({'error': '권한 없음'}), 403
    
    # 모든 사용자 조회
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.created_at,
               s.tier, s.expires_at, s.is_active
        FROM users u
        LEFT JOIN subscriptions s ON u.id = s.user_id
        ORDER BY u.created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'users': [dict(user) for user in users],
        'total': len(users)
    })
```

---

## 💳 **구독/결제 시스템 (선택)**

### 옵션 A: 수동 관리 (무료)
```
1. 사용자가 USDT 전송
2. TXID를 입력
3. 관리자가 수동으로 구독 활성화
4. expires_at 수동 설정
```

### 옵션 B: 자동 결제 (개발 필요)
```python
# Stripe, PayPal, Toss 등 연동
@app.route('/api/subscribe', methods=['POST'])
def api_subscribe():
    data = request.json
    plan = data.get('plan')  # '1month', '6months', 'lifetime'
    
    # 결제 API 호출
    payment = stripe.PaymentIntent.create(
        amount=get_plan_price(plan),
        currency='krw',
        metadata={'user_id': session['user_id'], 'plan': plan}
    )
    
    return jsonify({'client_secret': payment.client_secret})
```

---

## 🛠️ **지금 당장 배포하려면?**

### 최소 작업 (2~3시간)

1. **Railway 배포** (1시간)
   ```bash
   # requirements.txt, Procfile, railway.json 생성
   git add -A
   git commit -m "Railway 배포 설정"
   git push origin main
   # Railway에서 GitHub 연동 → 자동 배포
   ```

2. **사용자 독립 시스템 완성** (1시간)
   ```python
   # session['user_id'] 기반으로 모든 API 수정
   # 테스트용 'test_user' → 실제 user_id
   ```

3. **관리자 대시보드 연결** (30분)
   ```python
   # /api/admin/users 구현
   # 구독자 목록 표시
   ```

4. **테스트** (30분)
   ```
   - 사용자 A 로그인 → 봇 시작 → 거래 확인
   - 사용자 B 로그인 → 별도 봇 동작 확인
   - 관리자 로그인 → 사용자 목록 확인
   ```

---

## 📞 **다음 단계 선택**

### 옵션 1: **Railway 즉시 배포** (추천)
- 지금 바로 2~3시간 작업
- 오늘 안에 실제 서비스 가능
- URL: https://your-bot.up.railway.app

### 옵션 2: **완벽 준비 후 배포**
- 결제 시스템 추가 (1~2일)
- 커스텀 도메인 (tradingbot.com)
- 대규모 사용자 대비 최적화

### 옵션 3: **테스트 먼저**
- 현재 샌드박스에서 더 테스트
- 친구/지인에게 먼저 공유
- 안정성 확인 후 배포

---

## 💡 **제 추천**

**지금 당장 배포하고 싶다면?**
→ **Railway 선택** (1~2시간이면 완료)

**아직 테스트가 필요하다면?**
→ 현재 코드 더 다듬기 → 1~2일 후 배포

**어떤 방식으로 진행할까요?** 🤔

---

**요약**:
- ❌ 지금 Live Demo는 테스트용 (여러 명 접속 시 데이터 공유됨)
- ✅ 실제 배포 시 Railway 사용 추천 (가장 쉽고 빠름)
- 🔧 추가 작업: 사용자 독립 시스템 완성 (2~3시간)
- 🎯 목표: 각 사용자가 독립적인 봇 운영
