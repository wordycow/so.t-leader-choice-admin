# 🚀 무중단 배포 가이드 - PM2 활용

## 📋 목차
1. [PM2란?](#pm2란)
2. [주요 명령어](#주요-명령어)
3. [무중단 업데이트 방법](#무중단-업데이트-방법)
4. [로그 확인](#로그-확인)
5. [자동 재시작 설정](#자동-재시작-설정)

---

## 🎯 PM2란?

**PM2 (Process Manager 2)**는 Node.js/Python 애플리케이션을 위한 프로덕션급 프로세스 관리자입니다.

### ✅ 주요 기능
- **무중단 재시작**: 사용자 세션 유지
- **자동 재시작**: 에러 발생 시 자동 복구
- **로그 관리**: 실시간 로그 모니터링
- **메모리 관리**: 메모리 초과 시 자동 재시작
- **부팅 시 자동 시작**: 서버 재부팅 시 자동 실행

---

## 📌 주요 명령어

### 1️⃣ 봇 시작
```bash
cd /home/user/webapp
pm2 start ecosystem.config.js
```

### 2️⃣ 봇 정지
```bash
pm2 stop upbit-bot
```

### 3️⃣ 봇 재시작
```bash
# 일반 재시작 (잠깐 중단됨)
pm2 restart upbit-bot

# 무중단 재시작 (권장) ⭐
pm2 reload upbit-bot
```

### 4️⃣ 상태 확인
```bash
pm2 status
```

### 5️⃣ 로그 확인
```bash
# 실시간 로그 (Ctrl+C로 종료)
pm2 logs upbit-bot

# 최근 100줄만 보기
pm2 logs upbit-bot --lines 100 --nostream

# 에러 로그만 보기
pm2 logs upbit-bot --err
```

### 6️⃣ 봇 삭제 (완전 종료)
```bash
pm2 delete upbit-bot
```

### 7️⃣ 모니터링 대시보드
```bash
pm2 monit
```

---

## 🔄 무중단 업데이트 방법

### **방법 1: 자동 스크립트 사용 (권장) ⭐**

```bash
cd /home/user/webapp
./update.sh
```

**이 스크립트는 자동으로:**
1. ✅ 최신 코드를 Git에서 다운로드
2. ✅ 의존성 업데이트
3. ✅ 무중단 재시작 (`pm2 reload`)
4. ✅ 상태 및 로그 확인

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

## 📊 로그 확인

### 실시간 로그 보기
```bash
pm2 logs upbit-bot
```

### 로그 파일 위치
- **출력 로그**: `/tmp/upbit-bot-out.log`
- **에러 로그**: `/tmp/upbit-bot-error.log`

### 로그 직접 보기
```bash
tail -f /tmp/upbit-bot-out.log
```

---

## 🔁 자동 재시작 설정

### 1️⃣ 부팅 시 자동 시작 설정
```bash
pm2 startup
# 출력된 명령어를 복사해서 실행

pm2 save
```

### 2️⃣ 현재 프로세스 저장
```bash
pm2 save
```

이제 **서버가 재부팅되어도 봇이 자동으로 시작**됩니다!

---

## 🎯 무중단 배포의 핵심

### **`pm2 reload` vs `pm2 restart`**

| 명령어 | 설명 | 중단 시간 | 세션 유지 |
|--------|------|-----------|-----------|
| `pm2 restart` | 기존 프로세스 종료 → 새 프로세스 시작 | ❌ 있음 (1~2초) | ❌ 없음 |
| `pm2 reload` | 새 프로세스 시작 → 기존 프로세스 종료 | ✅ 없음 (0초) | ✅ 있음 |

**결론:** 항상 `pm2 reload`를 사용하세요!

---

## 🔧 트러블슈팅

### 문제 1: 봇이 시작되지 않음
```bash
pm2 logs upbit-bot --lines 50
```
에러 로그를 확인하고 문제 해결

### 문제 2: 메모리 초과
```bash
pm2 status
```
메모리 사용량 확인 → `ecosystem.config.js`에서 `max_memory_restart` 조정

### 문제 3: PM2가 없음
```bash
npm install -g pm2
```

---

## 📝 예제 시나리오

### 시나리오 1: 코드 수정 후 배포
```bash
# 로컬에서 코드 수정
git add .
git commit -m "🐛 버그 수정"
git push origin main

# 서버에서
cd /home/user/webapp
./update.sh
```

**결과:** 사용자들은 중단 없이 새 버전 사용 ✅

---

### 시나리오 2: 긴급 패치
```bash
cd /home/user/webapp
git pull origin main
pm2 reload upbit-bot
pm2 logs upbit-bot --lines 20 --nostream
```

**소요 시간:** 10초 이내 ⚡

---

### 시나리오 3: 서버 재부팅
```bash
# 부팅 시 자동 시작 설정 (최초 1회만)
pm2 startup
pm2 save

# 재부팅 후 자동으로 봇이 실행됨!
```

---

## 🎉 결론

**PM2를 사용하면:**
- ✅ 사용자 세션 유지 (봇이 돌아가는 중에도 업데이트 가능)
- ✅ 자동 재시작 (에러 발생 시 자동 복구)
- ✅ 간편한 로그 관리
- ✅ 부팅 시 자동 시작

**추천 워크플로우:**
1. 코드 수정 → Git Push
2. 서버에서 `./update.sh` 실행
3. 끝! 🎊

---

## 📞 지원

문제가 발생하면:
```bash
pm2 logs upbit-bot --lines 100 --nostream
```
로그를 확인하고 에러 메시지를 공유해주세요!
