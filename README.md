# 🤖 Lee May Training Center

**완전 통합 AI 학습 및 모니터링 시스템**

---

## 📖 문서 바로가기

- **🏗️ [현재 운영 구조 (Architecture)](docs/ARCHITECTURE.md)** - 시스템 아키텍처 1페이지 요약
- **📚 [운영 매뉴얼 (Runbook)](docs/RUNBOOK.md)** - 부팅, 제어, 점검, 문제 해결
- **🤖 [봇 분류 (Bots Classification)](BOTS_CLASSIFICATION.md)** - AI 학습 방법별 봇 분류
- **🔧 [AI Trading 복구 계획](docs/AI_TRADING_RECOVERY_PLAN.md)** - 5000 포트 복구 체크리스트

---

## 🏛️ 현재 운영 구조

### CONTROL vs BOTS 철학

Lee May는 **CONTROL**(핵심 인프라)과 **BOTS**(선택적 작업자) 2계층으로 운영됩니다.

#### 🌐 CONTROL 서비스 (24/7 가동)
```
포트: 5001 (API Server) + Cloudflare Tunnel
역할: 웹 UI, AI 대화, 모니터링, 학습 인터페이스
외부 URL: https://leemay.thetheunique.com
시작: ops\01_CONTROL_START.bat
```

#### 🤖 BOTS 서비스 (선택적 가동)
```
포트: 5000 (Trading Bot - 현재 비활성)
역할: AI Trading, YouTube 학습, 전략 최적화
외부 URL: https://ai_trading.thetheunique.com (현재 5001로 라우팅)
시작: ops\02_BOTS_START.bat
정지: ops\03_BOTS_STOP.bat
```

### 📂 Ops Scripts (운영 자동화)
```
ops/
├── 01_CONTROL_START.bat   # CONTROL 서비스 시작
├── 02_BOTS_START.bat      # BOTS 시작 (현재 안내만)
├── 03_BOTS_STOP.bat       # BOTS 정지
└── 99_STATUS.bat          # 전체 시스템 상태 점검
```

**일반 사용**: `01_CONTROL_START.bat` → `99_STATUS.bat` → 웹 접속  
**운영 가이드**: [docs/RUNBOOK.md](docs/RUNBOOK.md) 참조

---

## 📋 개요

Lee May Training Center는 **4대 핵심 모듈**을 하나의 유기적인 시스템으로 통합한 AI 기반 학습 플랫폼입니다.

### 🎯 핵심 기능

1. **🎭 Emotion Engine** - 페르소나/감정/이미지 삼위일체
   - 36개 감정 실시간 분석
   - 대화 내용에 따른 감정 이미지 자동 변경
   - 페르소나 기반 응답 생성

2. **📚 Knowledge RAG** - 유튜브 학습 시스템
   - 유튜브 자막 자동 추출 (`yt-dlp`)
   - 지식 베이스 자동 저장
   - LLM 컨텍스트 강제 주입
   - "방금 본 영상 요약해줘" 실시간 응답

3. **📊 Live Telemetry** - 실시간 데이터 파이프라인
   - CPU/메모리/디스크 실시간 모니터링
   - 트레이딩 봇 자산 수치 (실제 API 연동 가능)
   - 1초 단위 자동 업데이트

4. **🔗 Central Command** - 봇 중앙 관리
   - 모든 봇 상태 실시간 추적
   - 자가 진단 시스템
   - 에러 없는 모듈 간 데이터 통신

---

## 🚀 빠른 시작

### 1️⃣ 저장소 클론
```bash
git clone https://github.com/wordycow/so.t-leader-choice.git
cd so.t-leader-choice
```

### 2️⃣ 의존성 설치
```bash
pip install -r requirements.txt
```

**필수 패키지:**
- `flask`, `flask-cors` - 웹 서버
- `psutil` - 시스템 모니터링
- `ollama` - LLM
- `youtube-transcript-api` - 유튜브 자막
- `pymongo` - MongoDB (메모리 시스템)

### 3️⃣ 서버 시작

**Windows (스텔스 모드):**
```bash
LeeMay_START.vbs
```
→ 콘솔 창 없이 백그라운드 실행, 5초 후 완료 팝업

**직접 실행:**
```bash
python api_server.py
```

### 4️⃣ 접속

- **로컬**: http://localhost:5001
- **외부**: https://leemay.thetheunique.com (Cloudflare Tunnel)

---

## 📁 프로젝트 구조

```
so.t-leader-choice/
├── api_server.py              # 🚀 통합 API 서버 (4대 모듈)
├── emotion_mapper.py          # 🎭 감정 분석 엔진
├── leemay/
│   ├── core/
│   │   ├── emay_brain.py      # 🧠 LLM 두뇌 시스템
│   │   └── memory.py          # 💾 MongoDB 메모리
│   ├── learning/
│   │   └── youtube_learner.py # 📺 유튜브 학습
│   ├── personas/              # 👤 페르소나 JSON
│   └── images/                # 🖼️  감정 이미지 (36개)
├── web/
│   └── dashboard.html         # 🌐 프론트엔드
├── knowledge_base/            # 📚 학습한 지식 저장소
├── LeeMay_START.vbs           # ▶️  시작 스크립트
├── LeeMay_STOP.bat            # ⏹️  종료 스크립트
└── README.md
```

---

## 🌐 API 엔드포인트

### 🎭 Emotion Engine
```http
POST /chat
Content-Type: application/json

{
  "message": "너무 행복해!",
  "user_id": "web_user"
}

→ {
    "response": "와! 행복한 일이 생겼구나! 🎉",
    "emotion": "happy",
    "image_url": "/image/happy",
    "confidence": 85.0
  }
```

```http
GET /image/<emotion>
→ 감정 이미지 PNG 파일 (36개 감정)
```

### 📚 Knowledge RAG
```http
POST /api/learning/youtube
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=abc123"
}

→ {
    "success": true,
    "video_id": "abc123",
    "language": "한국어",
    "length": 15234,
    "summary": "..."
  }
```

```http
GET /api/knowledge/list
→ 학습한 영상 목록
```

### 📊 Live Telemetry
```http
GET /api/system/status
→ {
    "cpu": 25.3,
    "memory": 68.7,
    "disk": 42.1,
    "timestamp": "2026-02-20T07:30:00"
  }
```

```http
GET /api/trading/status
→ 트레이딩 봇 상태 (실시간)
```

### 🔗 Central Command
```http
GET /api/bots/status
→ {
    "leemay_api": {"running": true, "pid": 12345},
    "ollama_tunnel": {"running": true, "pid": 67890}
  }
```

```http
GET /api/system/diagnose
→ 전체 시스템 자가 진단
```

---

## 🧪 테스트

### 1. 헬스체크
```bash
curl http://localhost:5001/health
```

### 2. 채팅 테스트
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕!", "user_id": "test"}'
```

### 3. 유튜브 학습 테스트
```bash
curl -X POST http://localhost:5001/api/learning/youtube \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

---

## 🛠️ 개발 환경

- **Python**: 3.9+
- **Flask**: 2.3.0+
- **Ollama**: 로컬/원격 서버 (http://ollama.thetheunique.com)
- **MongoDB Atlas**: 메모리 저장소
- **Cloudflare Tunnel**: 외부 접속

---

## 📊 시스템 요구사항

- **최소**:
  - CPU: 2코어
  - RAM: 4GB
  - 디스크: 10GB

- **권장**:
  - CPU: 4코어+
  - RAM: 8GB+
  - 디스크: 20GB+

---

## 🔐 환경 변수 (.env)

```env
# MongoDB
MONGODB_URI=mongodb+srv://...

# Ollama
OLLAMA_HOST=http://ollama.thetheunique.com

# 이미지 경로
IMAGE_BASE_PATH=C:\leemay_project\leemay\images\emotions_36
```

---

## 🚨 문제 해결

### 1. 이미지가 안 뜨는 경우
```bash
# 이미지 경로 확인
emotion_mapper.py 파일에서 IMAGE_BASE_PATH 수정
```

### 2. 유튜브 학습 실패
```bash
# youtube-transcript-api 재설치
pip install --upgrade youtube-transcript-api
```

### 3. 시스템 상태가 안 뜨는 경우
```bash
# psutil 재설치
pip install --upgrade psutil
```

---

## 📜 라이선스

MIT License

---

## 👤 작성자

**Lee May Training Center Team**
- GitHub: https://github.com/wordycow/so.t-leader-choice
- Domain: https://leemay.thetheunique.com

---

## 🎉 특별 감사

- **Ollama** - LLM 엔진
- **YouTube Transcript API** - 자막 추출
- **MongoDB Atlas** - 메모리 저장소
- **Cloudflare** - 터널링

---

**Made with ❤️  by Lee May Team**
