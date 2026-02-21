# 🤖 Lee May Training Center - AI 봇 분류 및 정리

## 📊 AI 학습 방법별 분류

---

## 1️⃣ AI 언어 모델(LLM) 학습 방법 및 비용

### 🔴 **단기/소규모: RAG (검색 증강 생성)**
**항시 돌려야 하는 봇** ✅

| 파일명 | 용도 | 학습 방식 | 비고 |
|--------|------|-----------|------|
| `api_server.py` | 🎭 통합 API 서버 | RAG (실시간) | **메인 서버** - 24시간 가동 필수 |
| `leemay/core/emay_brain.py` | 🧠 LLM 두뇌 시스템 | RAG + LLM | Ollama 연동, MongoDB 메모리 |
| `leemay/core/memory.py` | 💾 메모리 시스템 | RAG (검색) | MongoDB Atlas 연결 |
| `bot_manager.py` | 🔗 봇 중앙 관리 | - | 다른 봇들 제어 |

**가동 시간:** 24시간 (서버 다운되면 전체 시스템 멈춤)  
**구루/기간:** 실시간 (API 요청마다)  
**예상 비용:** MongoDB Atlas Free Tier (512MB), Ollama 자체 호스팅 (무료)

---

### 🟡 **중/장기: LoRA / QLoRA (Fine-tuning)**
**가끔 돌려야 하는 봇** 🕒

| 파일명 | 용도 | 학습 방식 | 비고 |
|--------|------|-----------|------|
| `leemay/learning/youtube_learner.py` | 📺 유튜브 자막 학습 | LoRA (수동) | 사용자가 URL 입력 시 실행 |
| `leemay/learning/youtube_smart_learner.py` | 📺 고급 유튜브 학습 | LoRA + Whisper | 자막 없는 영상도 지원 (Whisper) |

**가동 시간:** 수동 실행 (유튜브 URL 입력 시)  
**구루/기간:** 수 일 → 수 주 (1~3일) | RTX 3090/4090급  
**예상 비용:** 
- 자막 추출: 무료 (YouTube Transcript API)
- Whisper 음성 인식: GPU 필요 시 Runpod/Vast.ai ($0.3~0.5/hour)

**학습 프로세스:**
1. 사용자가 대시보드에서 유튜브 URL 입력
2. 자막 자동 추출 (한국어/영어)
3. `knowledge_base/` 폴더에 JSON 저장
4. EmayBrain이 다음 대화 시 컨텍스트로 활용

---

## 2️⃣ AI 트레이딩 봇 학습 방법 및 비용

### 🔴 **단기/소규모: 지도 학습 (Supervised)**
**항시 돌려야 하는 봇** ✅

| 파일명 | 용도 | 학습 방식 | 비고 |
|--------|------|-----------|------|
| `upbit-smart-bot-v8.0-ULTIMATE.py` | 🏆 **최종 트레이딩 봇** | 지도 학습 (실시간) | **현재 가동 중** - 실전 매매 |

**기능:**
- 📊 5가지 패턴 자동 인식 (박스권, 상승/하락 추세, 급등후, 수급 변화)
- 🏆 5개 전략 동시 경쟁 (Surge Hunter, Dip Hunter, Box Trader, Trend Follower, Volume Hunter)
- 🧠 매 거래마다 학습 → 50개 거래마다 재학습
- 🛡️ 손실 복구 모드 (-15% 손실 시 자동 활성화)
- 📈 Flask 대시보드 (웹 UI)

**가동 시간:** 24시간 (실전 매매)  
**구루/기간:** 수 시간 (실시간 학습)  
**예상 비용:** 무료 (로컬 PC 실행), Upbit API 수수료만 (0.05%)

---

### 🟡 **중/장기: 강화 학습 (DQN, PPO)**
**가끔 돌려야 하는 봇** 🕒

| 파일명 | 용도 | 학습 방식 | 비고 |
|--------|------|-----------|------|
| `upbit-smart-bot-v8.0-LEARNING.py` | 🧠 패턴 학습 봇 | 강화 학습 (백테스트) | 전략 최적화 테스트용 |
| `upbit-backtest.py` | 📊 백테스트 시스템 | - | 과거 데이터로 전략 검증 |

**가동 시간:** 수동 실행 (전략 업데이트 시)  
**구루/기간:** 수 일 → 수 주 (GPU 가속 필요 없음, CPU만으로 가능)  
**예상 비용:** 무료 (로컬 실행)

**사용 시나리오:**
1. 새로운 전략 아이디어 발생
2. `upbit-backtest.py`로 과거 데이터 검증
3. `upbit-smart-bot-v8.0-LEARNING.py`로 학습
4. 결과 좋으면 `upbit-smart-bot-v8.0-ULTIMATE.py`에 반영

---

## 🗑️ 삭제 대상 (중복/구버전)

### ❌ **구버전 봇 (v3~v7)**
```
upbit-smart-bot-v3.py            # 770줄 - v8.0으로 대체
upbit-smart-bot-v4.py            # 797줄 - v8.0으로 대체
upbit-smart-bot-v4-final.py      # 721줄 - v8.0으로 대체
upbit-smart-bot-v5.py            # 773줄 - v8.0으로 대체
upbit-smart-bot-v7.2-SURGE-HUNTER.py  # 835줄 - v8.0에 통합됨
upbit-smart-bot-v7.3-DIP-HUNTER.py    # 1000줄 - v8.0에 통합됨
upbit-smart-bot.py               # 642줄 - 최초 버전
```

### ❌ **중복 런처**
```
upbit-bot-launcher.py            # 350줄 - LeeMay_START.vbs로 대체
upbit-scalping-bot.py            # 316줄 - v8.0에 통합됨
upbit-smart-bot-v8.5-RECOVERY.py # 579줄 - v8.0에 손실 복구 모드 통합됨
```

### ❌ **테스트 파일 (보관용)**
```
test_bot_signals.py              # 83줄 - 개발 완료
leemay/tests/test_emay_chat.py   # 테스트 완료
leemay/tests/test_memory.py      # 테스트 완료
leemay/tests/test_mongodb_atlas.py  # 테스트 완료
```

### ❌ **Archive 폴더 (이미 백업됨)**
```
archive/unused-bot-versions/upbit-bot-v5/*
archive/unused-bot-versions/upbit-bot-v6/*
upbit-bot-v6/*                    # 중복 (archive에 있음)
upbit-bot-v8-ultimate-release/*   # 중복 (루트에 있음)
```

---

## ✅ 최종 유지 파일 목록

### 🔴 **항시 가동 (24시간)**
```
✅ api_server.py                  # 메인 API 서버
✅ bot_manager.py                 # 봇 중앙 관리
✅ bot_state_manager.py           # 봇 상태 DB
✅ leemay/core/emay_brain.py      # LLM 두뇌
✅ leemay/core/memory.py          # MongoDB 메모리
✅ upbit-smart-bot-v8.0-ULTIMATE.py  # 실전 트레이딩
```

### 🟡 **수동 실행 (필요 시)**
```
✅ leemay/learning/youtube_learner.py        # 유튜브 학습 (기본)
✅ leemay/learning/youtube_smart_learner.py  # 유튜브 학습 (고급)
✅ upbit-smart-bot-v8.0-LEARNING.py         # 전략 학습/최적화
✅ upbit-backtest.py                        # 백테스트 검증
```

### 🔵 **지원 파일**
```
✅ emotion_mapper.py              # 36개 감정 매핑
✅ user_manager.py                # 사용자 관리
✅ portfolio_manager.py           # 포트폴리오 관리
✅ trade_reasons.py               # 거래 이유 생성
✅ recovery_system.py             # 손실 복구 시스템
✅ enhanced_emei_learning.py      # 고급 학습
✅ emei_response_router.py        # 응답 라우터
```

---

## 🚀 실행 가이드

### **1. 항시 가동 (노트북 부팅 시 자동)**

```bash
# Windows
LeeMay_START.vbs

# 또는 수동
python api_server.py                       # 포트 5001
python upbit-smart-bot-v8.0-ULTIMATE.py    # 포트 5000
```

**결과:**
- http://localhost:5001 → Lee May Training Center
- http://localhost:5000 → Trading Bot Dashboard

---

### **2. 유튜브 학습 (필요 시)**

```bash
# 방법 1: 대시보드에서
http://localhost:5001 접속 → 유튜브 URL 입력 → "학습" 버튼

# 방법 2: 직접 실행
python leemay/learning/youtube_learner.py
# URL 입력: https://www.youtube.com/watch?v=...
```

---

### **3. 전략 최적화 (주 1회)**

```bash
# 백테스트로 검증
python upbit-backtest.py

# 학습 봇으로 최적화
python upbit-smart-bot-v8.0-LEARNING.py
```

---

## 📊 리소스 사용량

| 봇 | CPU | 메모리 | 디스크 | GPU |
|----|-----|--------|--------|-----|
| api_server.py | 5~10% | 200MB | 50MB | ❌ |
| emay_brain.py | 10~20% | 500MB | - | ❌ (Ollama 서버 사용) |
| upbit-smart-bot-v8.0 | 15~30% | 300MB | 100MB | ❌ |
| youtube_learner.py | 5% | 150MB | 10MB | ❌ |
| youtube_smart_learner.py (Whisper) | 50%+ | 2GB+ | 500MB | ✅ (선택) |

**총 예상:**
- CPU: 30~60% (4코어 기준)
- RAM: 1~2GB
- 디스크: 200MB~1GB (로그 제외)

---

## 💰 예상 비용 (월)

| 항목 | 비용 | 비고 |
|------|------|------|
| MongoDB Atlas (메모리) | $0 | Free Tier (512MB) |
| Ollama 호스팅 | $0 | 자체 서버 (ollama.thetheunique.com) |
| Cloudflare Tunnel | $0 | 무료 플랜 |
| YouTube API | $0 | youtube-transcript-api (무료) |
| Whisper (선택) | $0~$30 | 로컬 실행 무료, Runpod 사용 시 유료 |
| Upbit 수수료 | 거래량 × 0.05% | 실제 거래만 발생 |
| **총계** | **$0~$30** | Whisper 클라우드 사용 시에만 |

---

## 🎯 권장 운영 시나리오

### **평일 (자동화)**
```
08:00 - 노트북 부팅
08:01 - LeeMay_START.vbs 자동 실행
08:02 - api_server.py 가동 (5001 포트)
08:03 - upbit-smart-bot-v8.0-ULTIMATE.py 가동 (5000 포트)
09:00~23:00 - 자동 매매 (24시간 감시 모드)
23:00 - 일일 리포트 생성
```

### **주말 (유지보수)**
```
토요일 오전:
  1. 주간 트레이딩 성과 분석
  2. upbit-backtest.py로 새 전략 검증
  3. 필요 시 upbit-smart-bot-v8.0-LEARNING.py 실행
  
일요일:
  1. 유튜브 학습 (관심 있는 트레이딩/AI 영상)
  2. knowledge_base 업데이트 확인
  3. Lee May와 대화로 학습 내용 확인
```

---

## 📌 핵심 요약

### ✅ **유지 (12개 파일)**
- API 서버 (1개)
- LLM 봇 (4개)
- 트레이딩 봇 (2개)
- 지원 파일 (5개)

### ❌ **삭제 (25개 파일)**
- 구버전 봇 (7개)
- 중복 파일 (3개)
- 테스트 파일 (4개)
- Archive (11개)

### 💾 **절약 공간**
- 삭제 전: ~50MB (코드 + 로그)
- 삭제 후: ~5MB
- **절약: 45MB (90%)**

---

**Made with ❤️  by Lee May Team**
