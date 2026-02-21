# 🎮 Lee May Control Center - Operations Runbook

> **운영 철학**: CONTROL(항상 가동) vs BOTS(선택적 가동)  
> **목적**: 시스템 관리자가 빠르게 상태를 파악하고, 문제를 해결하며, 서비스를 제어할 수 있도록 돕는 가이드

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [CONTROL vs BOTS Philosophy](#control-vs-bots-philosophy)
3. [Quick Start Guide](#quick-start-guide)
4. [Ops Scripts Reference](#ops-scripts-reference)
5. [API Endpoints](#api-endpoints)
6. [Troubleshooting](#troubleshooting)
7. [Logs & Monitoring](#logs--monitoring)

---

## 🏗️ System Overview

Lee May Control Center는 **통합 AI 학습/모니터링 플랫폼**으로 다음 구성 요소로 이루어져 있습니다:

### Core Components (CONTROL)
- **API Server** (포트 5001): 웹 UI, REST API, 시스템 모니터링
- **Cloudflare Tunnel**: 외부 접속 (https://leemay.thetheunique.com)
- **MongoDB Atlas**: 원격 메모리/지식 저장소 (자동 연결)
- **Ollama LLM**: AI 응답 엔진 (외부 서버: http://ollama.thetheunique.com)

### Optional Components (BOTS)
- **AI Trading Bot** (포트 5000): Upbit 자동 매매 - 현재 비활성
- **YouTube Learner**: 유튜브 자막 학습 - 웹 UI 또는 수동 실행
- **Strategy Learning Bot**: 트레이딩 전략 최적화 - 주말 수동 실행

---

## 🧠 CONTROL vs BOTS Philosophy

### CONTROL (핵심 인프라)
**특징**: 24/7 가동, 시스템 생명선, 재시작 없이 유지
**구성**: API Server, Cloudflare Tunnel, 원격 DB/LLM
**시작**: `ops\01_CONTROL_START.bat`
**중단**: 거의 하지 않음 (유지보수 시에만)

**Why?**
- 외부 사용자가 언제든 접속 가능해야 함
- 시스템 모니터링/관리 기능 제공
- BOTS 없이도 기본 AI 대화 기능 동작
- 학습 인터페이스(웹 UI) 제공

### BOTS (선택적 작업자)
**특징**: 필요할 때만 가동, 독립적 시작/정지 가능
**구성**: Trading Bot, Learning Bots
**시작**: `ops\02_BOTS_START.bat` (현재 자동 시작 없음)
**중단**: `ops\03_BOTS_STOP.bat`

**Why?**
- Trading Bot은 개발/테스트 중 (현재 비활성)
- 학습 작업은 주기적 또는 즉시 실행
- CONTROL 서비스 영향 없이 독립 관리
- 리소스 절약 (필요할 때만)

**철학 요약**:
```
┌─────────────────────────────────────────┐
│         CONTROL (항상 ON)                │
│  ┌─────────────────────────────────┐   │
│  │   API Server (5001)              │   │
│  │   Cloudflare Tunnel              │   │
│  │   Remote DB/LLM                  │   │
│  └─────────────────────────────────┘   │
│                                          │
│         BOTS (선택적 ON/OFF)            │
│  ┌─────────────────────────────────┐   │
│  │ □ Trading Bot (5000) - 비활성    │   │
│  │ □ YouTube Learner - 수동         │   │
│  │ □ Strategy Learning - 수동       │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. 부팅 시 자동 시작 (권장)

**Windows 시작 프로그램에 등록**:
```
1. 시작 폴더 열기: Win+R → shell:startup
2. 바로가기 생성: C:\leemay_project\ops\01_CONTROL_START.bat
3. 재부팅 후 자동 시작 확인
```

**작업 스케줄러 등록 (고급)**:
```
1. "작업 스케줄러" 실행
2. "작업 만들기"
3. 트리거: "시스템 시작 시"
4. 동작: C:\leemay_project\ops\01_CONTROL_START.bat
5. 조건: "컴퓨터의 전원이 AC 전원일 때만" 해제
```

### 2. 수동 시작 (개발/테스트)

**전체 시작**:
```batch
cd C:\leemay_project
ops\01_CONTROL_START.bat    # CONTROL 서비스 시작
ops\99_STATUS.bat            # 상태 확인
```

**BOTS 추가 시작** (필요시):
```batch
ops\02_BOTS_START.bat       # 현재는 안내만 제공 (Trading Bot 비활성)
```

### 3. 상태 확인

**로컬 확인**:
```batch
ops\99_STATUS.bat           # 전체 상태 점검
```

**웹 확인**:
```
로컬: http://localhost:5001
외부: https://leemay.thetheunique.com
```

### 4. 서비스 정지

**BOTS만 정지** (CONTROL 유지):
```batch
ops\03_BOTS_STOP.bat
```

**전체 정지** (비추천, 유지보수 시만):
```batch
taskkill /FI "WINDOWTITLE eq api_server*" /F
taskkill /FI "IMAGENAME eq cloudflared.exe" /F
```

---

## 📜 Ops Scripts Reference

### 01_CONTROL_START.bat
**목적**: 핵심 제어 서비스 시작  
**실행**: `ops\01_CONTROL_START.bat`  
**소요 시간**: 5-10초  
**작업 내용**:
1. Python 및 필수 파일 확인
2. 로그/데이터 디렉토리 생성
3. Ollama 외부 서버 연결 확인
4. API Server 백그라운드 시작 (포트 5001)
5. Cloudflare Tunnel 백그라운드 시작

**출력 예시**:
```
========================================
CONTROL START 완료
========================================

API Server (5001):
  ✓ 실행 중
  → http://localhost:5001

Cloudflare Tunnel:
  ✓ 실행 중
  → https://leemay.thetheunique.com
```

**실패 시**:
- Python 미설치 → Python 3.8+ 설치
- api_server.py 없음 → git pull origin main
- 포트 충돌 → 기존 프로세스 종료 후 재시도
- Cloudflare 설정 없음 → config.yml 확인

---

### 02_BOTS_START.bat
**목적**: 선택적 봇 시작 (현재 자동 시작 없음)  
**실행**: `ops\02_BOTS_START.bat`  
**소요 시간**: 즉시  
**작업 내용**:
1. AI Trading Bot 파일 확인 (현재 비활성)
2. YouTube Learner 상태 안내
3. 수동 실행 명령어 안내

**출력 예시**:
```
========================================
BOTS START 완료
========================================

현재 자동 시작되는 봇: 없음
수동 실행 가능한 봇: YouTube Learner, 전략 학습

AI Trading Bot 복구:
  docs/AI_TRADING_RECOVERY_PLAN.md 참조
```

**수동 실행**:
```batch
# YouTube 학습 (웹 UI 권장)
http://localhost:5001 → YouTube 학습 입력

# 또는 명령줄
python leemay/learning/youtube_learner.py

# 전략 학습 (주말)
python upbit-smart-bot-v8.0-LEARNING.py
python upbit-backtest.py
```

---

### 03_BOTS_STOP.bat
**목적**: 봇만 종료 (CONTROL 유지)  
**실행**: `ops\03_BOTS_STOP.bat`  
**소요 시간**: 2-5초  
**작업 내용**:
1. AI Trading Bot 프로세스 종료
2. YouTube Learner 프로세스 종료
3. CONTROL 서비스 상태 확인

**출력 예시**:
```
========================================
BOTS STOP 완료
========================================

종료된 봇: Trading Bot, Learning Bots
유지된 서비스: API Server (5001), Cloudflare Tunnel
```

**주의사항**:
- Trading Bot 실행 중이면 즉시 매매 중단
- 진행 중인 학습 작업은 중단됨 (복구 불가)
- CONTROL 서비스는 영향 없음

---

### 99_STATUS.bat
**목적**: 전체 시스템 상태 점검  
**실행**: `ops\99_STATUS.bat`  
**소요 시간**: 5-10초  
**작업 내용**:
1. CONTROL 서비스 상태 (API, Cloudflare, Ollama)
2. BOTS 상태 (Trading, Learning)
3. 포트 열림 확인 (5001, 5000, 11434)
4. 외부 접속 확인 (https://leemay.thetheunique.com)
5. 종합 판정 (OK/WARN/FAIL)

**출력 예시**:
```
[OVERALL STATUS]
================================================================

종합 등급: OK
사유: 핵심 서비스(API, Cloudflare) 모두 정상

권장 조치: 없음
```

**종합 등급**:
- **OK**: 핵심 서비스 정상, 외부 접속 가능
- **WARN**: 일부 서비스 경고 (Ollama 접속 실패 등)
- **FAIL**: 핵심 서비스 미실행 → 01_CONTROL_START.bat 실행

---

## 🌐 API Endpoints

### 인증 요구사항
모든 OPS API는 **관리자 인증 필수**:
- 헤더: `X-ADMIN-TOKEN: <your_admin_token>`
- 또는 세션 로그인: `POST /api/auth/login`

환경변수 설정:
```bash
set ADMIN_TOKEN=your_secret_token_here
```

### POST /api/ops/control/start
**목적**: CONTROL 서비스 시작  
**인증**: 필수  
**응답**:
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "...",
  "stderr": ""
}
```

**cURL 예시**:
```bash
curl -X POST http://localhost:5001/api/ops/control/start \
  -H "X-ADMIN-TOKEN: your_token"
```

---

### POST /api/ops/bots/start
**목적**: BOTS 시작 (현재 안내만)  
**인증**: 필수  
**응답**: 동일 형식

**cURL 예시**:
```bash
curl -X POST http://localhost:5001/api/ops/bots/start \
  -H "X-ADMIN-TOKEN: your_token"
```

---

### POST /api/ops/bots/stop
**목적**: BOTS 정지  
**인증**: 필수  
**응답**: 동일 형식

**cURL 예시**:
```bash
curl -X POST http://localhost:5001/api/ops/bots/stop \
  -H "X-ADMIN-TOKEN: your_token"
```

---

### GET /api/ops/status
**목적**: 시스템 종합 상태 조회  
**인증**: 불필요 (읽기 전용)  
**응답**:
```json
{
  "success": true,
  "status": {
    "timestamp": "2026-02-20T12:00:00",
    "control": {
      "api_server": true,
      "cloudflared": true,
      "ollama": true
    },
    "bots": {
      "trading_bot": false,
      "youtube_learner": false
    },
    "ports": {
      "5001": true,
      "5000": false,
      "11434": false
    },
    "overall": "OK"
  },
  "raw_output": "..."
}
```

**cURL 예시**:
```bash
curl http://localhost:5001/api/ops/status
```

---

## 🔧 Troubleshooting

### API Server가 시작되지 않음

**증상**: `ops\99_STATUS.bat`에서 "API Server: STOPPED"

**원인 및 해결**:

1. **포트 충돌 (5001)**
   ```batch
   netstat -ano | findstr :5001
   taskkill /PID <PID> /F
   ops\01_CONTROL_START.bat
   ```

2. **Python 미설치 또는 경로 문제**
   ```batch
   python --version    # 3.8+ 필요
   where python
   ```

3. **필수 패키지 누락**
   ```batch
   cd C:\leemay_project
   pip install -r requirements.txt
   ```

4. **로그 확인**
   ```batch
   type logs\ops_api.log
   # 또는 웹에서: http://localhost:5001/api/admin/logs
   ```

---

### Cloudflare Tunnel 연결 실패

**증상**: 로컬 접속은 되지만 https://leemay.thetheunique.com 접속 안 됨

**원인 및 해결**:

1. **cloudflared 미설치**
   - 다운로드: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   - 설치 후 재시작

2. **config.yml 설정 오류**
   ```yaml
   # config.yml 확인
   tunnel: <your-tunnel-id>
   credentials-file: C:\leemay_project\.cloudflared\<tunnel-id>.json
   ingress:
     - hostname: leemay.thetheunique.com
       service: http://localhost:5001
     - hostname: ai_trading.thetheunique.com
       service: http://localhost:5001  # 현재 5001로 라우팅
     - service: http_status:404
   ```

3. **Cloudflare 대시보드 확인**
   - https://dash.cloudflare.com
   - "Zero Trust" → "Access" → "Tunnels"
   - 터널 상태: "HEALTHY"

---

### Ollama 외부 서버 접속 실패

**증상**: `ops\99_STATUS.bat`에서 "Ollama: NOT ACCESSIBLE"

**영향**: AI 대화 기능 사용 불가

**원인 및 해결**:

1. **네트워크 문제**
   ```batch
   ping ollama.thetheunique.com
   curl http://ollama.thetheunique.com/api/tags
   ```

2. **외부 서버 다운**
   - 서버 관리자에게 연락
   - 또는 로컬 Ollama 설치:
     ```batch
     # Ollama 설치: https://ollama.com/download
     ollama serve     # 포트 11434
     # leemay/core/emay_brain.py 수정:
     # ollama.thetheunique.com → localhost
     ```

3. **방화벽 차단**
   ```batch
   # Windows 방화벽 확인
   netsh advfirewall firewall show rule name=all | findstr Ollama
   ```

---

### Trading Bot 복구

**증상**: Trading Bot (포트 5000) 실행 안 됨

**해결**: `docs/AI_TRADING_RECOVERY_PLAN.md` 참조 (별도 문서)

---

## 📊 Logs & Monitoring

### 로그 파일 위치

```
C:\leemay_project\
├─ logs\
│  ├─ ops_api.log           # OPS API 실행 로그
│  ├─ api_server.log         # API Server 일반 로그
│  └─ cloudflared.log        # Cloudflare Tunnel 로그
├─ data\
│  ├─ server.db              # 감사 로그, 채팅 기록
│  ├─ sim_trading.db         # 시뮬 트레이딩 DB
│  └─ learning_logs\         # 학습 작업 로그
│     └─ job_<id>.log
└─ leemay\
   └─ images\                # Emotion 이미지
```

### 로그 확인 방법

**명령줄**:
```batch
# OPS 로그
type C:\leemay_project\logs\ops_api.log

# 실시간 모니터링 (PowerShell)
Get-Content C:\leemay_project\logs\ops_api.log -Wait
```

**웹 UI** (권장):
```
http://localhost:5001/api/admin/logs
```

### 모니터링 지표

**핵심 지표**:
- API Server 응답 시간: < 200ms
- CPU 사용률: < 60%
- 메모리 사용률: < 70%
- 디스크 여유: > 10GB

**확인 방법**:
```batch
ops\99_STATUS.bat           # 상태 점검
```

**웹 대시보드**:
```
http://localhost:5001       # Live Telemetry 패널
```

---

## 🔐 Security Considerations

### 환경변수 설정 (필수)

**개발 환경** (로컬만):
```batch
set ADMIN_TOKEN=dev_token_123
set SECRET_KEY=dev_secret_456
```

**운영 환경** (외부 접속):
```batch
set ADMIN_TOKEN=strong_random_token_here_min_32_chars
set SECRET_KEY=another_strong_random_token_min_32_chars
set CORS_ORIGINS=https://leemay.thetheunique.com
```

### 보안 제약

1. **Allowlist Only**: 4개 배치 파일만 실행 가능
2. **No Arbitrary Commands**: 사용자 입력 명령 실행 불가
3. **Admin Only**: OPS API는 관리자 인증 필수
4. **Audit Logging**: 모든 OPS 실행 기록

### 추천 사항

- ADMIN_TOKEN은 최소 32자 이상 무작위 문자열
- 외부 접속 시 CORS_ORIGINS 제한 필수
- 정기적으로 logs\ops_api.log 감사
- MongoDB/Cloudflare 토큰 별도 관리

---

## 📚 Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 시스템 아키텍처
- [AI_TRADING_RECOVERY_PLAN.md](./AI_TRADING_RECOVERY_PLAN.md) - Trading Bot 복구 가이드
- [README.md](../README.md) - 프로젝트 개요

---

## 🆘 Emergency Contacts

**시스템 관리자**: wordycow  
**GitHub**: https://github.com/wordycow/so.t-leader-choice  
**외부 접속**: https://leemay.thetheunique.com

---

**Last Updated**: 2026-02-20  
**Version**: 1.0
