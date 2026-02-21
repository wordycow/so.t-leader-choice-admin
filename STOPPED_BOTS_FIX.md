# 🔧 봇이 정지된 사용자 해결 가이드

## 📋 **문제 상황**

**증상:**
- 관리자 페이지에서 `lee1`, `wordycow`의 봇 상태가 "⚪ 정지"로 표시
- 게스트 사용자만 "🟢 실행" 상태

**원인:**
- 이전 버전(v10.4 이하)에서 봇을 시작한 사용자
- DB 저장 기능이 없어서 `bot_states` 테이블에 기록되지 않음
- 새 버전(v10.5)에서는 DB에 기록이 없으면 자동 복구 불가

---

## ✅ **해결 방법**

### **방법 1: 사용자가 직접 재시작 (권장) ⭐**

**단계:**
1. 브라우저에서 해당 계정으로 로그인
   - `wordycow` 계정: https://5000-xxx.sandbox.novita.ai
   - `lee1` 계정: 동일 URL

2. 대시보드에서 시드 금액 입력
   ```
   예: 2,000,000원
   ```

3. "🚀 봇 시작" 버튼 클릭

4. 완료!
   - 자동으로 DB에 저장됨
   - 다음 업데이트부터 자동 복구됨

---

### **방법 2: 관리자가 강제 시작 (임시)**

**현재는 불가능 (기능 없음)**

하지만 다음 기능을 추가할 수 있습니다:

#### **A. 관리자 페이지에 "강제 시작" 버튼 추가**
```javascript
// admin.html에 추가
function forceStartBot(userId) {
  fetch('/api/admin/force-start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      user_id: userId,
      seed: 1000000  // 기본 시드
    })
  }).then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('✅ 봇 강제 시작 성공!');
        loadUsers();
      }
    });
}
```

#### **B. 백엔드 API 추가**
```python
@app.route('/api/admin/force-start', methods=['POST'])
def api_admin_force_start():
    data = request.json
    user_id = data.get('user_id')
    seed = data.get('seed', 1000000)
    
    # 봇 시작 로직
    bot_state = get_user_bot_state(user_id)
    bot_state['running'] = True
    bot_state['simulation_start_seed'] = seed
    
    save_bot_state(user_id, bot_state)
    thread = threading.Thread(target=bot_main_loop, args=(user_id, bot_state), daemon=True)
    thread.start()
    
    return jsonify({'success': True})
```

---

### **방법 3: 직접 DB 수정 (고급)**

**주의:** 권장하지 않음 (데이터 손실 위험)

```bash
cd /home/user/webapp
python3 << 'EOF'
import sqlite3
from bot_state_manager import save_bot_state, get_user_bot_state

# wordycow 봇 시작
user_id = 'wordycow'
bot_state = get_user_bot_state(user_id)
bot_state['running'] = True
bot_state['mode'] = 'practice'
bot_state['simulation_start_seed'] = 2000000
bot_state['simulation_krw'] = 2000000

save_bot_state(user_id, bot_state)
print(f"✅ {user_id} 봇 상태 DB에 저장")

# 서버 재시작 필요
print("⚠️ 서버 재시작 필요: pm2 reload upbit-bot")
EOF
```

---

## 🎯 **권장 순서**

### **즉시 해결 (1분)**
```
1. wordycow 또는 lee1 계정으로 로그인
2. 시드 입력 → 봇 시작
3. 완료!
```

### **영구 해결 (10분 - 선택사항)**
```
관리자 페이지에 "강제 시작" 버튼 추가
→ 사용자가 로그인하지 않아도 관리자가 직접 시작 가능
```

---

## 📊 **현재 상태**

```bash
# DB 확인
python3 bot_state_manager.py

# 출력:
📊 실행 중인 봇: 1개
  - guest_10.64.13.98: practice 모드, 1,000,000원

# 누락:
- wordycow: DB에 없음 (봇 정지)
- lee1: DB에 없음 (봇 정지)
```

---

## 🔄 **예방책**

앞으로는 이런 일이 없도록:

1. ✅ v10.5부터 모든 봇 자동 저장
2. ✅ 업데이트 시 자동 복구
3. ✅ 사용자 알림 (선택사항)

---

## 💡 **추가 기능 제안**

### **1. 관리자 페이지에 "일괄 시작" 버튼**
```
모든 정지된 봇을 한 번에 시작
```

### **2. 사용자에게 알림**
```
"⚠️ 봇이 정지되었습니다. 다시 시작하려면 클릭하세요"
```

### **3. 자동 재시작 옵션**
```
사용자 설정에서 "자동 재시작" 옵션 제공
```

---

## 🎉 **결론**

**가장 빠른 해결책:**
1. `wordycow`와 `lee1` 계정으로 로그인
2. 봇 시작 버튼 클릭
3. 끝!

이후부터는 자동으로 복구됩니다! 🚀
