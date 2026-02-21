# 🚀 배치 파일 사용 가이드 (수정 완료)

## ⚠️ 문제 해결 완료

### **이전 문제:**
1. ❌ 한글 깨짐 (Windows 콘솔 인코딩)
2. ❌ Cloudflare Tunnel URL이 콘솔에 표시 안됨

### **해결 방법:**
1. ✅ 영어 메시지로 변경 (인코딩 문제 회피)
2. ✅ Cloudflare Tunnel을 **별도 창**으로 실행
3. ✅ URL을 새 창에서 직접 확인 가능

---

## 📦 새로 만든 배치 파일

### 🟢 시작 스크립트
```
START_ALL.bat                     ← 모든 서버 한번에 시작 (권장!)
START_Cloudflare_Ollama.bat      ← Ollama + Tunnel만 시작
노트북_시작.bat                   ← Trading Bot만 시작 (기존)
```

### 🔴 종료 스크립트
```
STOP_ALL.bat                      ← 모든 서버 한번에 종료
STOP_Cloudflare_Ollama.bat       ← Ollama + Tunnel만 종료
노트북_종료.bat                   ← Trading Bot만 종료 (기존)
```

---

## 🎯 사용 방법

### **1️⃣ 모든 서버 시작 (권장)**

#### 실행:
```
START_ALL.bat 더블클릭
```

#### 화면 출력:
```
========================================
[START] ALL SERVICES
========================================
  1. Ollama Server (localhost:11434)
  2. Cloudflare Tunnel
  3. Trading Bot (localhost:5000)
========================================

[1/3] Starting Ollama Server...
[OK] Ollama started - http://localhost:11434

[2/3] Starting Cloudflare Tunnel...
========================================
CLOUDFLARE TUNNEL URL:
========================================
[OK] Cloudflare Tunnel started
[INFO] Check the new window for URL!

[3/3] Starting Trading Bot...
[OK] Trading Bot started - http://localhost:5000

========================================
SUCCESS! All services running
========================================

[ACCESS URLS]
  Trading Bot:  http://localhost:5000
  Ollama:       http://localhost:11434
  External:     Check Cloudflare Tunnel window

[STOP ALL]
  Run: STOP_ALL.bat
```

#### ⚡ 중요!
- **새 창이 자동으로 열립니다**: "Cloudflare Tunnel - CHECK THIS WINDOW!"
- **이 창에서 URL 확인**: `https://xxxx-yyyy-zzzz.trycloudflare.com`
- **URL 복사해서 외부 접속에 사용**

#### 종료:
```
STOP_ALL.bat 더블클릭
```

---

### **2️⃣ Ollama + Cloudflare Tunnel만 시작**

#### 실행:
```
START_Cloudflare_Ollama.bat 더블클릭
```

#### 화면 출력:
```
========================================
[START] Cloudflare Tunnel + Ollama
========================================

[1/2] Checking Ollama Server...
[START] Starting Ollama on port 11434...
[OK] Ollama started

[2/2] Checking Cloudflare Tunnel...
[START] Starting Cloudflare Tunnel...
========================================
CLOUDFLARE TUNNEL URL WILL APPEAR HERE:
========================================

[OK] Cloudflare Tunnel started in separate window
[INFO] Look for "https://xxxxx.trycloudflare.com" in the new window!

========================================
SUCCESS! All servers are running
========================================

[LOCAL ACCESS]
  Ollama: http://localhost:11434

[EXTERNAL ACCESS]
  Check the "Cloudflare Tunnel" window
  Look for: https://xxxxx.trycloudflare.com

[STOP SERVICES]
  Run: STOP_Cloudflare_Ollama.bat
```

#### 종료:
```
STOP_Cloudflare_Ollama.bat 더블클릭
```

---

### **3️⃣ Trading Bot만 시작**

#### 실행:
```
노트북_시작.bat 더블클릭
→ http://localhost:5000
```

#### 종료:
```
노트북_종료.bat 더블클릭
```

---

## 🌐 Cloudflare Tunnel URL 확인 방법

### **1. START_ALL.bat 실행 시:**
1. 배치 파일 실행
2. **새 콘솔 창 자동 열림**: "Cloudflare Tunnel - CHECK THIS WINDOW!"
3. 이 창에서 다음과 같은 출력 확인:

```
2024-02-19 12:34:56 INF +--------------------------------------------------------------------------------------------+
2024-02-19 12:34:56 INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
2024-02-19 12:34:56 INF |  https://abc-def-ghi.trycloudflare.com                                                    |
2024-02-19 12:34:56 INF +--------------------------------------------------------------------------------------------+
```

4. **URL 복사**: `https://abc-def-ghi.trycloudflare.com`
5. **외부 접속**: 이 URL을 사용해 Ollama 서버에 접속

### **2. URL 사용 예시:**

#### 로컬 접속:
```
http://localhost:11434/api/generate
```

#### 외부 접속:
```
https://abc-def-ghi.trycloudflare.com/api/generate
```

---

## ⚠️ 주의사항

### **1. Cloudflare Tunnel 창 닫지 마세요**
- Tunnel 창을 닫으면 외부 접속이 끊깁니다
- 최소화해서 사용하세요

### **2. URL은 매번 바뀝니다**
- Cloudflare Tunnel 재시작 시마다 새 URL 생성
- 항상 새 창에서 URL 확인 필요

### **3. 포트 충돌 시:**
```
STOP_ALL.bat 실행
→ 모든 서비스 종료
→ 다시 START_ALL.bat 실행
```

---

## 🔧 트러블슈팅

### **Q1. Cloudflare URL이 안 보여요**
**A:** Cloudflare Tunnel 창이 열렸는지 확인하세요
- 창 제목: "Cloudflare Tunnel - CHECK THIS WINDOW!"
- 작업 표시줄에서 찾아보세요

### **Q2. "cloudflared를 찾을 수 없음" 오류**
**A:** Cloudflare Tunnel 설치 필요
```
https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
→ Windows용 cloudflared 다운로드
→ PATH 환경 변수에 추가
```

### **Q3. Ollama "11434 포트 사용 중" 오류**
**A:** 
```cmd
STOP_ALL.bat 실행
또는
taskkill /F /IM ollama.exe
```

### **Q4. 한글이 깨져요**
**A:** 새 버전 배치 파일은 영어로 작성되어 문제 없습니다
- `START_ALL.bat` 사용하세요

---

## 📁 파일 구조

```
C:\Users\wordy\OneDrive\바탕화면\webapp\
├── START_ALL.bat                     ← 🟢 전체 시작 (권장)
├── STOP_ALL.bat                      ← 🔴 전체 종료
├── START_Cloudflare_Ollama.bat      ← 🟢 Ollama+Tunnel 시작
├── STOP_Cloudflare_Ollama.bat       ← 🔴 Ollama+Tunnel 종료
├── 노트북_시작.bat                   ← 🟢 Bot 시작
├── 노트북_종료.bat                   ← 🔴 Bot 종료
├── upbit-smart-bot-v8.0-ULTIMATE.py
└── BATCH_GUIDE_FIXED.md             ← 📖 이 파일
```

---

## 🎉 빠른 시작

### **1단계: 모든 서버 시작**
```
START_ALL.bat 더블클릭
```

### **2단계: Cloudflare URL 확인**
```
"Cloudflare Tunnel" 창에서 URL 복사
예: https://abc-xyz-123.trycloudflare.com
```

### **3단계: Trading Bot 접속**
```
브라우저 열기
→ http://localhost:5000
→ API 키 입력
→ 봇 시작!
```

### **4단계: 외부에서 Ollama 사용**
```
Cloudflare URL 공유
→ 다른 사람이 Ollama 서버 접속 가능
```

---

## 📅 업데이트 내역

- **2024-02-19**: 
  - ✅ 한글 깨짐 문제 해결 (영어 버전 배치 파일)
  - ✅ Cloudflare URL 표시 문제 해결 (별도 창 실행)
  - ✅ 통합 시작/종료 스크립트 추가 (START_ALL.bat, STOP_ALL.bat)

---

**🚀 이제 START_ALL.bat을 실행하고 새 창에서 Cloudflare URL을 확인하세요!**
