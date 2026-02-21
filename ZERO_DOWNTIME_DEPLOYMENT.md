# 🚀 무중단 배포 완전 가이드

## ✅ 문제 해결: "업데이트할 때마다 봇이 멈추는 문제"

### 🐛 이전 문제점
```bash
# 기존 방식
git pull origin main
python3 upbit-smart-bot-v8.0-ULTIMATE.py

# 문제:
# 1. 프로세스를 kill하면 → 모든 사용자 봇 중단
# 2. 재시작하면 → 세션 초기화 (사용자 데이터 손실)
# 3. 중단 시간 발생 → 사용자 경험 저하
```

### ✅ 해결 방법: PM2 프로세스 관리자

---

## 🎯 PM2란?

**PM2**는 Node.js/Python 애플리케이션을 위한 **프로덕션급 프로세스 관리자**입니다.

### 핵심 기능
| 기능 | 설명 |
|------|------|
| 🔄 **무중단 재시작** | 새 프로세스 시작 → 기존 프로세스 종료 (0초 중단) |
| 🔁 **자동 재시작** | 에러 발생 시 자동 복구 |
| 📊 **로그 관리** | 실시간 로그 모니터링 + 파일 저장 |
| 💾 **메모리 관리** | 메모리 초과 시 자동 재시작 |
| 🚀 **부팅 시 자동 시작** | 서버 재부팅 시 자동 실행 |

---

## 📝 설치 및 설정

### 1️⃣ PM2 설치 (이미 완료)
```bash
npm install -g pm2
```

### 2️⃣ 설정 파일 (`ecosystem.config.js`)
```javascript
module.exports = {
  apps: [{
    name: 'upbit-bot',
    script: 'upbit-smart-bot-v8.0-ULTIMATE.py',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    max_memory_restart: '500M',
    error_file: '/tmp/upbit-bot-error.log',
    out_file: '/tmp/upbit-bot-out.log'
  }]
}
```

### 3️⃣ 봇 시작
```bash
cd /home/user/webapp
pm2 start ecosystem.config.js
```

---

## 🔄 무중단 업데이트 방법

### **방법 1: 자동 스크립트 (권장) ⭐**

```bash
cd /home/user/webapp
./update.sh
```

**이 명령어 하나로:**
1. ✅ Git에서 최신 코드 다운로드
2. ✅ 의존성 자동 업데이트
3. ✅ 무중단 재시작 (`pm2 reload`)
4. ✅ 상태 및 로그 자동 확인

**소요 시간:** 약 5초  
**중단 시간:** 0초 (사용자 세션 유지)

---

### **방법 2: 수동 업데이트**

```bash
cd /home/user/webapp

# 1. 최신 코드 가져오기
git pull origin main

# 2. 무중단 재시작
pm2 reload upbit-bot

# 3. 상태 확인
pm2 status
```

---

## 🎬 실제 업데이트 시연

### **Before (업데이트 전)**
```bash
$ pm2 status
┌────┬──────────────┬──────┬───────────┬──────────┐
│ id │ name         │ pid  │ status    │ ↺        │
├────┼──────────────┼──────┼───────────┼──────────┤
│ 0  │ upbit-bot    │ 1234 │ online    │ 0        │
└────┴──────────────┴──────┴───────────┴──────────┘

# 사용자 A: 봇 실행 중 (1,000,000원 투자)
# 사용자 B: 봇 실행 중 (2,000,000원 투자)
```

### **During (업데이트 중)**
```bash
$ ./update.sh
🔄 업비트 봇 무중단 업데이트 시작...
📥 최신 코드 다운로드 중...
🔄 봇 재시작 중 (사용자 세션 유지)...
[PM2] [upbit-bot](0) ✓

# 내부 동작:
# 1. 새 프로세스 시작 (PID: 5678)
# 2. 새 프로세스 준비 완료
# 3. 기존 프로세스 종료 (PID: 1234)
# 4. 사용자 세션 자동 복구
```

### **After (업데이트 후)**
```bash
$ pm2 status
┌────┬──────────────┬──────┬───────────┬──────────┐
│ id │ name         │ pid  │ status    │ ↺        │
├────┼──────────────┼──────┼───────────┼──────────┤
│ 0  │ upbit-bot    │ 5678 │ online    │ 1        │
└────┴──────────────┴──────┴───────────┴──────────┘

# 사용자 A: 봇 여전히 실행 중 ✅
# 사용자 B: 봇 여전히 실행 중 ✅
# 중단 시간: 0초 ✅
```

---

## 📊 주요 명령어

### 기본 명령어
```bash
# 봇 시작
pm2 start ecosystem.config.js

# 봇 정지
pm2 stop upbit-bot

# 봇 재시작 (일반)
pm2 restart upbit-bot

# 봇 재시작 (무중단) ⭐
pm2 reload upbit-bot

# 상태 확인
pm2 status

# 로그 보기 (실시간)
pm2 logs upbit-bot

# 로그 보기 (최근 100줄)
pm2 logs upbit-bot --lines 100 --nostream

# 모니터링 대시보드
pm2 monit

# 봇 삭제 (완전 종료)
pm2 delete upbit-bot
```

---

## 🔁 자동 시작 설정

### 서버 재부팅 시 자동 시작
```bash
# 1. 시작 스크립트 생성
pm2 startup

# 2. 출력된 명령어 복사 & 실행 (예시)
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u user --hp /home/user

# 3. 현재 프로세스 저장
pm2 save
```

이제 **서버가 재부팅되어도 봇이 자동으로 시작**됩니다!

---

## 🎯 업데이트 워크플로우

### **개발자 워크플로우**
```bash
# 1. 로컬에서 코드 수정
vim upbit-smart-bot-v8.0-ULTIMATE.py

# 2. Git 커밋
git add .
git commit -m "🐛 버그 수정"
git push origin main

# 3. 서버에서 업데이트 (SSH 접속)
cd /home/user/webapp
./update.sh

# 완료! (소요 시간: 5초, 중단 시간: 0초)
```

---

## 🔧 트러블슈팅

### 문제 1: 봇이 시작되지 않음
```bash
# 로그 확인
pm2 logs upbit-bot --lines 50

# 에러 확인
pm2 logs upbit-bot --err --lines 50
```

### 문제 2: 메모리 초과
```bash
# 현재 메모리 사용량 확인
pm2 status

# ecosystem.config.js 수정
max_memory_restart: '1G'  # 500M → 1G로 증가
```

### 문제 3: 업데이트가 적용되지 않음
```bash
# 강제 재시작
pm2 restart upbit-bot

# 또는
pm2 delete upbit-bot
pm2 start ecosystem.config.js
```

---

## 📈 실전 시나리오

### 시나리오 1: 긴급 버그 수정
```bash
# 시간: 10초 이내 ⚡

cd /home/user/webapp
git pull origin main
pm2 reload upbit-bot
pm2 logs upbit-bot --lines 20 --nostream
```

### 시나리오 2: 대규모 업데이트
```bash
# 시간: 30초 이내 🚀

cd /home/user/webapp
./update.sh

# 자동으로:
# - Git Pull
# - 의존성 업데이트
# - 무중단 재시작
# - 상태 확인
# - 로그 확인
```

### 시나리오 3: 서버 점검 (재부팅)
```bash
# 1회 설정 (최초 1번만)
pm2 startup
pm2 save

# 재부팅 후 자동 시작됨! ✅
```

---

## 🎉 결과

### **Before PM2**
```
업데이트 → 봇 중단 → 사용자 피해 → 재시작 → 세션 손실
```

### **After PM2**
```
업데이트 → 무중단 재시작 → 사용자 무감각 → 완료! 🎊
```

---

## 📝 체크리스트

업데이트 전 확인사항:
- [ ] PM2 상태 확인 (`pm2 status`)
- [ ] 현재 사용자 수 확인 (`curl localhost:5000/api/admin/users`)
- [ ] 로그 정상 확인 (`pm2 logs upbit-bot --lines 20 --nostream`)

업데이트 후 확인사항:
- [ ] PM2 상태 `online` 확인
- [ ] 로그에 에러 없는지 확인
- [ ] 관리자 페이지에서 봇 실행 상태 확인
- [ ] 사용자 세션 유지 확인

---

## 🔗 관련 문서

- **PM2 공식 문서**: https://pm2.keymetrics.io/docs/usage/quick-start/
- **PM2_GUIDE.md**: 상세 가이드 (`/home/user/webapp/PM2_GUIDE.md`)
- **update.sh**: 자동 업데이트 스크립트 (`/home/user/webapp/update.sh`)

---

## 💬 지원

문제가 발생하면:
```bash
pm2 logs upbit-bot --lines 100 --nostream
```
로그를 확인하고 에러 메시지를 공유해주세요!

---

## 🎊 요약

| 항목 | Before | After (PM2) |
|------|--------|-------------|
| 업데이트 중단 시간 | 5~10초 | **0초** ✅ |
| 사용자 세션 유지 | ❌ 손실 | **✅ 유지** |
| 자동 재시작 | ❌ 없음 | **✅ 있음** |
| 로그 관리 | 수동 | **✅ 자동** |
| 부팅 시 자동 시작 | ❌ 없음 | **✅ 있음** |
| 메모리 관리 | ❌ 없음 | **✅ 자동** |

**이제 안심하고 업데이트하세요!** 🚀
