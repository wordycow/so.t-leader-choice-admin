# 🏗️ 현재 운영 구조 (Architecture Overview)

**Lee May Training Center - 시스템 아키텍처 1페이지 요약**

---

## 🎯 시스템 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                  🌐 외부 사용자                                  │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              ☁️  Cloudflare Tunnel                              │
│              (ollama-stable)                                    │
│                                                                 │
│   leemay.thetheunique.com ──────────┐                          │
│   ai_trading.thetheunique.com ──────┤ → localhost:5001         │
│                                      │                          │
└──────────────────────────────────────┴──────────────────────────┘
                 │
                 │ HTTP
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  🖥️  Windows Server (C:\leemay_project)                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🔴 CONTROL (항시 유지)                                   │  │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │  │
│  │                                                           │  │
│  │  📡 API Server (5001)                                     │  │
│  │     ├─ api_server.py                                      │  │
│  │     ├─ Flask + CORS                                       │  │
│  │     └─ Endpoints:                                         │  │
│  │        - /health                                          │  │
│  │        - /chat                                            │  │
│  │        - /image/<emotion>                                 │  │
│  │        - /api/system/status                               │  │
│  │        - /api/bots/status                                 │  │
│  │        - /api/learning/youtube                            │  │
│  │                                                           │  │
│  │  🧠 LLM Engine                                            │  │
│  │     ├─ leemay/core/emay_brain.py                          │  │
│  │     ├─ Ollama Client                                      │  │
│  │     └─ 연결: http://ollama.thetheunique.com              │  │
│  │                                                           │  │
│  │  💾 Memory System                                         │  │
│  │     ├─ leemay/core/memory.py                              │  │
│  │     └─ MongoDB Atlas (512MB Free)                         │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  🟡 BOTS (선택적 가동)                                    │  │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │  │
│  │                                                           │  │
│  │  📉 AI Trading Bot (5000) - 현재 비활성                   │  │
│  │     └─ upbit-smart-bot-v8.0-ULTIMATE.py                   │  │
│  │                                                           │  │
│  │  📺 YouTube Learner (수동)                                │  │
│  │     ├─ leemay/learning/youtube_learner.py                 │  │
│  │     └─ leemay/learning/youtube_smart_learner.py           │  │
│  │                                                           │  │
│  │  🎓 Strategy Learning (수동)                              │  │
│  │     ├─ upbit-smart-bot-v8.0-LEARNING.py                   │  │
│  │     └─ upbit-backtest.py                                  │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 핵심 컴포넌트

### **1. CONTROL (🔴 항시 유지)**

| 컴포넌트 | 포트 | 역할 | 상태 |
|----------|------|------|------|
| **API Server** | 5001 | 웹 UI + REST API | ✅ 가동 중 |
| **Cloudflare Tunnel** | - | 외부 접속 (HTTPS) | ✅ 가동 중 |
| **Ollama** | - | LLM 엔진 (외부 서버) | ✅ 접속 가능 |

**시작 방법:**
```bash
ops\01_CONTROL_START.bat
```

---

### **2. BOTS (🟡 선택적 가동)**

| 봇 | 포트 | 역할 | 상태 |
|----|------|------|------|
| **AI Trading Bot** | 5000 | 실전 매매 (Upbit) | ⚪ 비활성 |
| **YouTube Learner** | - | 유튜브 자막 학습 | ⚪ 수동 |
| **Strategy Learning** | - | 전략 최적화 | ⚪ 수동 |

**시작 방법:**
```bash
ops\02_BOTS_START.bat
```

**중지 방법:**
```bash
ops\03_BOTS_STOP.bat
```

---

## 🌐 외부 접속 경로

### **도메인 매핑**

```
https://leemay.thetheunique.com
  └─> Cloudflare Tunnel (ollama-stable)
      └─> localhost:5001 (API Server)
          └─> /health, /chat, /api/*

https://ai_trading.thetheunique.com
  └─> Cloudflare Tunnel (ollama-stable)
      └─> localhost:5001 (현재 5001로 라우팅)
          └─> 향후 5000으로 변경 예정
```

### **Cloudflare 설정**

**config.yml 위치:**
```
C:\Users\[사용자]\.cloudflared\config.yml
```

**Ingress 라우팅:**
```yaml
tunnel: [TUNNEL_ID]
ingress:
  - hostname: leemay.thetheunique.com
    service: http://localhost:5001
  - hostname: ai_trading.thetheunique.com
    service: http://localhost:5001  # 현재 5001로 라우팅
  - service: http_status:404
```

---

## 📂 디렉토리 구조

```
C:\leemay_project\
├── api_server.py                    # 메인 API 서버 (5001)
├── bot_manager.py                   # 봇 중앙 관리
├── emotion_mapper.py                # 36개 감정 매핑
│
├── leemay/                          # Lee May 코어
│   ├── core/
│   │   ├── emay_brain.py            # LLM 두뇌
│   │   └── memory.py                # MongoDB 메모리
│   └── learning/
│       ├── youtube_learner.py       # 유튜브 학습
│       └── youtube_smart_learner.py # 고급 유튜브 학습
│
├── ops/                             # 🆕 운영 스크립트
│   ├── 01_CONTROL_START.bat         # CONTROL 시작
│   ├── 02_BOTS_START.bat            # BOTS 시작
│   ├── 03_BOTS_STOP.bat             # BOTS 정지
│   └── 99_STATUS.bat                # 상태 점검
│
├── docs/                            # 🆕 문서
│   ├── RUNBOOK.md                   # 운영 매뉴얼
│   └── AI_TRADING_RECOVERY_PLAN.md  # Trading Bot 복구 계획
│
├── web/
│   └── dashboard.html               # 웹 UI
│
├── knowledge_base/                  # 유튜브 학습 데이터
│   └── knowledge_base.json
│
├── logs/                            # 🆕 로그
│   └── ops_api.log
│
└── upbit-smart-bot-v8.0-ULTIMATE.py # Trading Bot (비활성)
```

---

## 🔄 데이터 흐름

### **1. 채팅 요청**

```
사용자 (웹)
  │ POST /chat {"message": "안녕!"}
  ▼
api_server.py (5001)
  │ analyze_emotion()
  ▼
emotion_mapper.py
  │ detect_emotion() → "happy"
  ▼
emay_brain.py
  │ chat() → LLM 호출
  ▼
Ollama (외부 서버)
  │ llama3.1 모델
  ▼
memory.py
  │ save_conversation() → MongoDB
  ▼
Response
  │ {"response": "...", "emotion": "happy", "image_url": "/image/happy"}
  ▼
웹 UI
  │ 감정 이미지 업데이트
  └─ 채팅 메시지 표시
```

---

### **2. 유튜브 학습**

```
사용자 (웹)
  │ POST /api/learning/youtube {"url": "https://..."}
  ▼
api_server.py (5001)
  │ knowledge_rag.learn_from_youtube()
  ▼
youtube_learner.py
  │ YouTubeTranscriptApi.get_transcript()
  ▼
knowledge_base/
  │ knowledge_base.json 저장
  ▼
emay_brain.py
  │ 다음 채팅 시 컨텍스트로 활용
  └─ "방금 본 영상 요약해줘" → 실제 내용 응답
```

---

## 📊 리소스 사용량

### **CONTROL (24시간 가동)**

| 항목 | 사용량 |
|------|--------|
| CPU | 15~30% |
| RAM | 1~2GB |
| 디스크 | 200MB~1GB |
| 네트워크 | 외부 접속 시 변동 |

### **BOTS (선택적 가동)**

| 항목 | Trading Bot | YouTube Learner |
|------|-------------|-----------------|
| CPU | 15~30% | 5~10% |
| RAM | 300MB | 150MB |
| 실행 시간 | 24시간 (가동 시) | 5~30초 (학습 1회) |

---

## 🚀 빠른 시작

### **시스템 시작 (부팅 후)**

```bash
# 1. CONTROL 시작 (필수)
cd C:\leemay_project\ops
01_CONTROL_START.bat

# 2. 상태 확인
99_STATUS.bat

# 3. 외부 접속 테스트
curl https://leemay.thetheunique.com/health
```

### **일상 운영**

```bash
# 상태 점검 (일 1회)
ops\99_STATUS.bat

# BOTS 시작 (필요 시)
ops\02_BOTS_START.bat

# BOTS 정지 (필요 시)
ops\03_BOTS_STOP.bat
```

---

## 📌 중요 노트

### **✅ 정상 상태**
- API Server (5001): ✅ RUNNING
- Cloudflare Tunnel: ✅ RUNNING
- Ollama: ✅ ACCESSIBLE
- 외부 접속: ✅ https://leemay.thetheunique.com

### **⚠️ 현재 비활성**
- AI Trading Bot (5000): ⚪ STOPPED
  - 복구 계획: `docs/AI_TRADING_RECOVERY_PLAN.md`
  - 수동 실행: `python upbit-smart-bot-v8.0-ULTIMATE.py`

### **🎯 다음 단계**
1. ✅ CONTROL 안정화 (완료)
2. 🔄 웹 UI 개선 (진행 중)
3. ⏳ Trading Bot 복구 (계획 중)
4. ⏳ 모니터링 강화 (계획 중)

---

**GitHub**: https://github.com/wordycow/so.t-leader-choice  
**Last Updated**: 2026-02-20  
**Version**: 1.0
