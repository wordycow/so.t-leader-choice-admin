# 🔄 자동 복구 시스템 완전 가이드

## ✅ **문제 해결: 업데이트 후 봇이 멈추는 문제**

### 🐛 **이전 문제**
```
1. 사용자가 봇 시작
2. PM2 reload (업데이트)
3. 봇 스레드 종료
4. 사용자가 수동으로 재시작 필요 ❌
```

### ✅ **해결책: DB 기반 자동 복구**
```
1. 사용자가 봇 시작 → DB에 저장 (running=1)
2. PM2 reload (업데이트) → 프로세스 재시작
3. 서버 시작 시 → DB 조회
4. 자동으로 모든 봇 재시작 ✅
```

---

## 🎯 **핵심 기능**

### 1️⃣ **봇 상태 영구 저장**

**DB 스키마 (`bot_states` 테이블)**
```sql
CREATE TABLE bot_states (
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
```

**저장 시점:**
- ✅ 봇 시작 시
- ✅ 봇 정지 시
- ✅ 매 거래 후 (선택사항)

---

### 2️⃣ **자동 복구 프로세스**

```python
# 서버 시작 시 자동 실행
1. get_all_running_bots()  # DB에서 running=1인 봇 조회
   └─> [{user_id: 'guest_10.64.13.98', mode: 'practice', seed: 2000000}]

2. 각 봇에 대해:
   - bot_state 복원
   - 스레드 시작
   - 로그 출력: "✅ [user_id] 봇 복구 완료"

3. 결과:
   - 사용자는 아무것도 할 필요 없음
   - 봇이 자동으로 거래 재개
```

---

## 📊 **작동 시나리오**

### **시나리오 1: 일반 업데이트**

```bash
# 1. 사용자 A가 봇 시작
사용자: "🚀 봇 시작" 클릭
서버: save_bot_state(user_A, {running: true, seed: 2000000})
DB: INSERT user_A running=1

# 2. 개발자가 업데이트
개발자: ./update.sh 실행
PM2: reload → 프로세스 재시작

# 3. 서버 시작
서버: get_all_running_bots() → [user_A]
서버: 봇 자동 재시작
로그: ✅ [user_A] 봇 복구 완료

# 4. 사용자 관점
사용자: (아무것도 모름)
대시보드: 계속 거래 중 ✅
```

---

### **시나리오 2: 서버 재부팅**

```bash
# 1. 서버 재부팅 (예: PM2 startup)
시스템: 재부팅
PM2: 자동으로 upbit-bot 시작

# 2. 봇 서버 시작
서버: get_all_running_bots()
서버: DB에서 5개 봇 발견
서버: 5개 봇 모두 자동 재시작
로그: 🎉 모든 봇 복구 완료!

# 3. 사용자들
사용자 A, B, C, D, E: 계속 거래 중 ✅
```

---

### **시나리오 3: 긴급 수정**

```bash
# 1. 버그 발견
개발자: 코드 수정
개발자: git push

# 2. 무중단 업데이트
서버: cd /home/user/webapp && ./update.sh
PM2: reload (0초 중단)
서버: 실행 중이던 50개 봇 자동 복구
로그: ✅ 50개 봇 복구 완료

# 3. 사용자들
50명의 사용자: 아무도 불편함 없음 ✅
```

---

## 🔧 **API 변경 사항**

### **Before (v10.4)**
```python
# /api/start
bot_state['running'] = True
thread.start()
# DB 저장 없음 ❌
```

### **After (v10.5)**
```python
# /api/start
bot_state['running'] = True
save_bot_state(user_id, bot_state)  # ✅ DB 저장
thread.start()

# 서버 시작 시
running_bots = get_all_running_bots()  # ✅ DB 조회
for bot in running_bots:
    # 자동 복구
    thread.start()
```

---

## 🧪 **테스트 방법**

### **테스트 1: 기본 자동 복구**

```bash
# 1. 브라우저에서 봇 시작
https://5000-xxx.sandbox.novita.ai
"🚀 봇 시작" 클릭

# 2. DB 확인
cd /home/user/webapp
python3 bot_state_manager.py
# 출력: 📊 실행 중인 봇: 1개

# 3. 업데이트
./update.sh

# 4. 로그 확인
pm2 logs upbit-bot --lines 50 | grep "봇 복구"
# 출력: ✅ [guest_10.64.13.98] 봇 복구 완료

# 5. 브라우저 확인
# → 여전히 거래 중 ✅
```

---

### **테스트 2: 다중 사용자**

```bash
# 1. 3명의 사용자가 봇 시작
사용자 A: 1,000,000원
사용자 B: 2,000,000원
사용자 C: 5,000,000원

# 2. DB 확인
python3 bot_state_manager.py
# 출력: 📊 실행 중인 봇: 3개

# 3. PM2 재시작
pm2 restart upbit-bot

# 4. 로그 확인
pm2 logs upbit-bot | grep "봇 복구"
# 출력:
# ✅ [user_A] 봇 복구 완료 (모드: practice, 시드: 1,000,000원)
# ✅ [user_B] 봇 복구 완료 (모드: practice, 시드: 2,000,000원)
# ✅ [user_C] 봇 복구 완료 (모드: practice, 시드: 5,000,000원)
```

---

## 📝 **주요 파일**

| 파일 | 설명 |
|------|------|
| `bot_state_manager.py` | DB 저장/로드 모듈 |
| `upbit_bot.db` | SQLite 데이터베이스 (bot_states 테이블) |
| `upbit-smart-bot-v8.0-ULTIMATE.py` | 메인 봇 (자동 복구 로직 포함) |

---

## 🎉 **결과**

### **Before (v10.4)**
```
업데이트 → 봇 중단 → 사용자 불만 → 수동 재시작
```

### **After (v10.5)**
```
업데이트 → 자동 복구 → 사용자 무감각 → 완료! 🎊
```

---

## 💡 **추가 개선 사항 (선택)**

### 1️⃣ **주기적 상태 저장**
```python
# bot_main_loop 안에서
if loop_count % 10 == 0:  # 10번마다
    save_bot_state(user_id, bot_state)
```

### 2️⃣ **상태 동기화 API**
```python
@app.route('/api/sync-state', methods=['POST'])
def api_sync_state():
    # 현재 봇 상태를 강제로 DB에 저장
    pass
```

### 3️⃣ **복구 실패 알림**
```python
# 복구 실패 시 관리자에게 알림
if recovery_failed:
    send_notification(admin_email, "봇 복구 실패")
```

---

## 🔗 **관련 문서**

- `ZERO_DOWNTIME_DEPLOYMENT.md` - 무중단 배포 가이드
- `PM2_GUIDE.md` - PM2 사용 가이드
- `bot_state_manager.py` - DB 관리 모듈

---

## 🎊 **축하합니다!**

이제 **업데이트해도 봇이 절대 멈추지 않습니다!** 🚀

- ✅ 자동 복구 시스템 구축 완료
- ✅ DB 기반 상태 영구 저장
- ✅ 무중단 배포 + 자동 복구 = 완벽!

**다음 업데이트부터:**
```bash
./update.sh  # 끝!
```

사용자들은 **아무것도 몰라도 됩니다!** 😊
