# 🔐 영구 세션 시스템 가이드

## 📌 문제 해결

### **이전 문제**:
```
코드 업데이트 → 서버 재시작 → 세션 만료 → 강제 로그아웃
→ 거래 중단 → 사용자 재로그인 필요 😤
```

### **해결 방법**:
```
✅ 영구 세션 저장소 (SQLite)
✅ 고정 SECRET_KEY
✅ 자동 세션 복원
✅ 30일 유효기간
```

---

## 🔧 적용된 기술

### 1️⃣ **SQLite 기반 세션 저장소**

**새 테이블**: `persistent_sessions`
```sql
CREATE TABLE persistent_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
)
```

**작동 원리**:
- 로그인 시 영구 세션 ID 생성 (SHA256 해시)
- 쿠키에 `persistent_session_id` 저장 (30일 유효)
- 서버 재시작 후 자동 복원

---

### 2️⃣ **고정 SECRET_KEY**

**이전 문제**:
```python
app.secret_key = os.urandom(24)  # ❌ 재시작마다 변경
```

**해결**:
```python
SECRET_KEY_FILE = "/home/user/webapp/.secret_key"
if os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, "rb") as f:
        app.secret_key = f.read()
else:
    # 처음 실행 시 키 생성 및 저장
    app.secret_key = os.urandom(32)
    with open(SECRET_KEY_FILE, "wb") as f:
        f.write(app.secret_key)
    os.chmod(SECRET_KEY_FILE, 0o600)
```

**효과**:
- ✅ 서버 재시작 후에도 동일한 키 사용
- ✅ 기존 세션 쿠키 유효성 유지

---

### 3️⃣ **자동 세션 복원 미들웨어**

```python
@app.before_request
def restore_session():
    """서버 재시작 후 쿠키에서 세션 자동 복원"""
    if 'user_id' in session:
        session.permanent = True
        return
    
    persistent_id = request.cookies.get('persistent_session_id')
    if persistent_id:
        user_id = load_persistent_session(persistent_id)
        if user_id:
            session['user_id'] = user_id
            session.permanent = True
            log(f"🔓 세션 자동 복원: {user_id}", "INFO")
```

**작동 흐름**:
1. 모든 요청마다 자동 실행
2. Flask 세션에 `user_id` 없으면 쿠키 확인
3. `persistent_session_id`로 DB 조회
4. 유효하면 자동 로그인

---

### 4️⃣ **로그인/로그아웃 개선**

#### **로그인 시**:
```python
# 영구 세션 ID 생성
persistent_id = save_persistent_session(user['id'])

# 쿠키에 저장 (30일)
response.set_cookie(
    'persistent_session_id', 
    persistent_id,
    max_age=30*24*60*60,
    httponly=True,
    samesite='Lax'
)
```

#### **로그아웃 시**:
```python
# DB에서 세션 삭제
persistent_id = request.cookies.get('persistent_session_id')
if persistent_id:
    delete_persistent_session(persistent_id)

# 쿠키 삭제
response.set_cookie('persistent_session_id', '', max_age=0)
```

---

## 📊 비교표

| 항목 | 이전 | 개선 후 |
|------|------|---------|
| **서버 재시작** | ❌ 로그아웃 | ✅ 로그인 유지 |
| **세션 유효기간** | 브라우저 닫으면 만료 | 30일 (자동 연장) |
| **거래 중단** | ❌ 멈춤 | ✅ 계속 진행 |
| **사용자 경험** | 😤 재로그인 스트레스 | 😊 투명한 업데이트 |
| **SECRET_KEY** | ❌ 매번 변경 | ✅ 고정 |
| **세션 저장소** | 메모리 (휘발성) | SQLite (영구) |

---

## 🚀 사용 방법

### **1단계: 로그인**
```
https://5000-imdh8jpm1izc140vdjj3t-3844e1b6.sandbox.novita.ai/login
```
- 아이디: `wordycow` / 비밀번호: `1234`
- 로그인 시 쿠키에 `persistent_session_id` 자동 저장

### **2단계: 거래 시작**
- "매매 시작" 버튼 클릭
- 봇이 자동 거래 시작

### **3단계: 서버 재시작 테스트**
```bash
# 서버 재시작
pkill -9 -f "python3.*upbit-smart-bot"
python3 upbit-smart-bot-v8.0-ULTIMATE.py &
```

### **4단계: 자동 복원 확인**
- 브라우저 새로고침 (`F5`)
- ✅ 자동 로그인됨
- ✅ 거래 상태 유지
- ✅ 봇 계속 작동

---

## 🧪 테스트 시나리오

### **시나리오 1: 정상 재시작**
```bash
# 1. 로그인 후 거래 시작
# 2. 서버 재시작
pkill -9 -f "python3.*upbit-smart-bot"
python3 upbit-smart-bot-v8.0-ULTIMATE.py &

# 3. 브라우저 새로고침
# ✅ 예상 결과: 자동 로그인, 거래 계속
```

### **시나리오 2: 쿠키 삭제 테스트**
```javascript
// 브라우저 콘솔에서
document.cookie = "persistent_session_id=; max-age=0";
location.reload();

// ❌ 예상 결과: 로그인 페이지로 이동
```

### **시나리오 3: 만료된 세션**
```sql
-- 30일 이상 접속 없음
UPDATE persistent_sessions 
SET last_accessed = datetime('now', '-31 days')
WHERE user_id = 'wordycow';

-- 다음 요청 시 자동 삭제됨
```

---

## 🔐 보안 고려사항

### **1. HttpOnly 쿠키**
```python
httponly=True  # JavaScript로 접근 불가 (XSS 방지)
```

### **2. SameSite 설정**
```python
samesite='Lax'  # CSRF 공격 방지
```

### **3. SECRET_KEY 파일 권한**
```bash
chmod 600 .secret_key  # 소유자만 읽기/쓰기
```

### **4. 세션 ID 강도**
```python
session_id = hashlib.sha256(
    f"{user_id}-{time.time()}-{os.urandom(16).hex()}".encode()
).hexdigest()
# → 64자 SHA256 해시 (충돌 확률 극히 낮음)
```

---

## 📁 관련 파일

- **메인 코드**: `/home/user/webapp/upbit-smart-bot-v8.0-ULTIMATE.py`
- **SECRET_KEY**: `/home/user/webapp/.secret_key` (자동 생성)
- **DB 테이블**: `persistent_sessions` in `upbit_bot.db`

---

## 🎯 기대 효과

### **개발자 입장**:
```
✅ 코드 업데이트 자유롭게 가능
✅ 서버 재시작해도 사용자 영향 없음
✅ 긴급 버그 수정 시 빠른 배포
```

### **사용자 입장**:
```
✅ 거래 중단 없음
✅ 재로그인 스트레스 제거
✅ 투명한 업데이트 경험
✅ 30일간 자동 로그인 유지
```

---

## 💡 추가 개선 가능 사항

### **1. Redis 세션 저장소** (고성능)
```python
from flask_session import Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
```

### **2. JWT 토큰 기반 인증**
```python
import jwt
token = jwt.encode({'user_id': user_id}, SECRET_KEY, algorithm='HS256')
```

### **3. 무중단 배포 (Blue-Green)**
```bash
# 새 서버 시작 (포트 5001)
python3 upbit-smart-bot-v8.0-ULTIMATE.py --port 5001 &

# Nginx 트래픽 전환
nginx -s reload

# 구 서버 종료 (포트 5000)
```

---

## ✅ 완료 체크리스트

- [x] SQLite 세션 테이블 생성
- [x] 고정 SECRET_KEY 파일 저장
- [x] 자동 세션 복원 미들웨어
- [x] 로그인/로그아웃 쿠키 처리
- [x] 30일 자동 만료 정책
- [x] HttpOnly + SameSite 보안 설정
- [x] 서버 재시작 후 테스트 완료

---

## 🔗 서버 정보

| 항목 | 정보 |
|------|------|
| 🌐 **서버 URL** | https://5000-imdh8jpm1izc140vdjj3t-3844e1b6.sandbox.novita.ai |
| 🔑 **로그인** | `wordycow` / `1234` |
| 🔐 **SECRET_KEY** | `/home/user/webapp/.secret_key` (자동 생성) |
| 💾 **세션 DB** | `upbit_bot.db` → `persistent_sessions` 테이블 |
| ⏰ **세션 유효기간** | 30일 (자동 연장) |

---

**🎉 이제 서버 재시작해도 사용자는 로그인 상태 유지됩니다!**
