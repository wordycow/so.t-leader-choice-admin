# 🤖 이메이 (Emei) AI 시스템 - ChatGPT 협업 가이드

## 📍 서버 정보

### 접속 정보
- **서버 URL**: https://5000-imdh8jpm1izc140vdjj3t-3844e1b6.sandbox.novita.ai
- **포트**: 5000
- **호스트**: 5000-imdh8jpm1izc140vdjj3t-3844e1b6.sandbox.novita.ai
- **샌드박스 ID**: imdh8jpm1izc140vdjj3t-3844e1b6
- **로그인**: wordycow / 1234

### 서버 환경
- **프레임워크**: Flask (Python)
- **메인 파일**: `/home/user/webapp/upbit-smart-bot-v8.0-ULTIMATE.py`
- **로그 파일**: `/tmp/bot_clean.log`
- **데이터베이스**: `/home/user/webapp/upbit_bot.db` (SQLite)

---

## 🧠 이메이 학습 시스템 구조

### 1. 핵심 파일들

#### Python 모듈
```
/home/user/webapp/
├── emei_learning.py (337줄)
│   └── 기본 학습 엔진
├── emei_persona_data.py (8.7KB)
│   └── 여성 트레이더 페르소나 데이터
├── enhanced_emei_learning.py (3.4KB)
│   └── 향상된 학습 시스템 (사용자별 맞춤)
└── init_emei_knowledge.py
    └── 초기 지식 28개 항목 로드
```

#### 데이터베이스 테이블
```sql
-- 학습된 지식
CREATE TABLE emei_knowledge (
    id INTEGER PRIMARY KEY,
    question TEXT,           -- 질문
    answer TEXT,            -- 답변
    source TEXT DEFAULT 'chat',  -- 출처
    quality_score REAL DEFAULT 0.8,
    use_count INTEGER DEFAULT 0,
    last_used TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 대화 기록
CREATE TABLE emei_conversations (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    user_message TEXT,
    emei_response TEXT,
    learned INTEGER DEFAULT 0,
    youtube_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 대화 패턴
CREATE TABLE user_speech_patterns (
    user_id TEXT PRIMARY KEY,
    avg_message_length INTEGER DEFAULT 0,
    emoji_usage_rate REAL DEFAULT 0.0,
    formality_level TEXT DEFAULT 'formal',  -- formal/casual
    common_words TEXT DEFAULT '[]',  -- JSON 배열
    conversation_count INTEGER DEFAULT 0,
    last_interaction TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 선호도
CREATE TABLE user_preferences (
    user_id TEXT PRIMARY KEY,
    favorite_coins TEXT DEFAULT '[]',
    risk_tolerance TEXT DEFAULT 'medium',
    trading_style TEXT DEFAULT 'swing',
    preferred_response_style TEXT DEFAULT 'friendly',
    notes TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📊 현재 데이터 상태

### 학습된 지식 (111개)
- 코인 분석: 85개
- 기술 지표: 5개 (RSI, MACD 등)
- 트레이딩 전략: 5개
- 감정 지원: 5개
- 시장 분석: 5개
- 일반: 6개

### 응답 속도
- **DB 조회**: 0.002 ~ 0.003초 ⚡
- **로컬 AI** (연결 시): 2 ~ 5초
- **유튜브 학습**: 5 ~ 10초

---

## 🎭 이메이 페르소나 정보

### 기본 설정
```python
{
    "name": "이메이 (Emei)",
    "age": "20대 후반",
    "personality": "밝고 친근한, 진지할 땐 진지한",
    "speech_style": "이모지 자주 사용, 존댓말 기본, 가끔 반말",
    "expertise": ["차트 분석", "리스크 관리", "심리 상담"],
    "catchphrase": [
        "💜 같이 수익 내봐요!",
        "🎯 시장은 항상 기회를 줘요",
        "📊 차트는 거짓말 안 해요",
        "💪 우리 꾸준히 가요!"
    ]
}
```

### 유튜브 학습 기반
1. **슈카월드 - 여성 트레이더 인터뷰**
   - 손절의 중요성 강조
   - 감정 조절이 승률보다 중요
   - 작은 수익이라도 꾸준히

2. **가즈아 - 코인 투자 초보 탈출**
   - RSI, MACD 기초
   - 분할 매수 전략
   - 물타기 절대 금지

3. **여성 트레이더 밤비**
   - 일봉 차트 중심
   - 단타보다 스윙이 안전
   - 손절 -5% 원칙

---

## 🔌 API 엔드포인트

### Flask 라우트
```python
# 이메이 채팅
POST /api/emei/chat
- Input: {"message": "사용자 메시지"}
- Output: {"response": "답변", "learned": bool, "response_time": float}

# 이메이 통계
GET /api/emei/stats
- Output: {"total_knowledge": int, "total_conversations": int, ...}

# 봇 상태 조회
GET /api/status
- Output: {
    "running": bool,
    "current_krw": float,
    "holdings": [...],
    "recent_trades": [...]
  }
```

---

## 🎨 UI 구조 (dashboard-ultimate-v3-with-emei.html)

### 레이아웃
```
┌─────────────────────────────────────┬──────────┐
│                                     │  이메이  │
│     트레이딩 대시보드 (80%)           │  채팅    │
│                                     │  (20%)   │
│  - 잔고, 수익률, 승률                 │          │
│  - 봇 제어 (시작/정지)                │          │
│  - 보유 코인                         │          │
│  - 최근 신호                         │          │
│  - 거래 내역 (1331-1342줄)           │          │
│  - 전략 성과 카드                    │          │
└─────────────────────────────────────┴──────────┘
```

### 주요 섹션 위치
- **헤더**: 1050-1086줄
- **통계 카드**: 1088-1125줄
- **봇 제어**: 1250-1262줄
- **거래 내역**: 1331-1342줄 (HTML)
- **거래 내역 업데이트**: 1899-1949줄 (JavaScript)
- **이메이 채팅**: 1345-1377줄

---

## 🛠️ 언어 업데이트 방법

### 1. 새로운 지식 추가
```python
from emei_learning import get_emei

emei = get_emei()
emei.save_knowledge(
    question="새로운 질문",
    answer="답변 내용",
    source="manual",
    quality_score=1.0
)
```

### 2. 유튜브 영상 학습
```python
result = emei.learn_from_youtube(
    user_id="admin",
    youtube_url="https://youtube.com/watch?v=..."
)
```

### 3. 로컬 AI 학습
```python
result = emei.learn_from_local_ai(
    question="배우고 싶은 내용",
    context="추가 컨텍스트"
)
```

### 4. 대화 스타일 분석
```python
from emei_persona_data import get_persona

persona = get_persona()
persona.analyze_user_message(user_id, message)
pattern = persona.get_user_pattern(user_id)
```

---

## 📝 업데이트 시 주의사항

### ✅ 반드시 지킬 것
1. **서버 재시작 최소화**
   - 파일 수정 후 `pkill -f python3.*upbit && python3 upbit-smart-bot... &`
   - 또는 debug=True로 자동 재시작

2. **데이터 백업**
   ```bash
   cp upbit_bot.db upbit_bot.db.backup
   ```

3. **Git 커밋**
   ```bash
   git add -A
   git commit -m "설명"
   git push origin main
   ```

4. **로그 확인**
   ```bash
   tail -f /tmp/bot_clean.log
   ```

### ❌ 절대 하지 말 것
1. "지아와 대화" 버튼 다시 추가 (1072줄 이미 삭제됨)
2. 기존 DB 테이블 삭제
3. 학습 데이터 초기화
4. 서버 포트 변경 (5000 고정)

---

## 🔍 디버깅 정보

### 로그 명령어
```bash
# Flask 서버 로그
tail -f /tmp/bot_clean.log

# 거래 로그만
tail -f /tmp/bot_clean.log | grep -E "매수|매도"

# 이메이 로그
tail -f /tmp/bot_clean.log | grep -i emei

# 에러만
tail -f /tmp/bot_clean.log | grep ERROR
```

### DB 조회
```bash
sqlite3 /home/user/webapp/upbit_bot.db

# 지식 확인
SELECT COUNT(*) FROM emei_knowledge;

# 최근 대화 확인
SELECT * FROM emei_conversations ORDER BY created_at DESC LIMIT 5;

# 사용자 패턴 확인
SELECT * FROM user_speech_patterns WHERE user_id = 'wordycow';
```

### 서버 상태
```bash
# 프로세스 확인
ps aux | grep python3.*upbit

# 포트 확인
netstat -tulpn | grep :5000

# 메모리 확인
free -h
```

---

## 🚀 향상된 학습 시스템 (enhanced_emei_learning.py)

### 주요 기능
1. **이상한 입력 감지**
   - 너무 짧음 (< 2글자)
   - 특수문자만
   - 숫자만
   → 의미를 묻는 질문으로 학습 유도

2. **사용자별 맞춤 응답**
   - 반말/존댓말 자동 전환
   - 이모지 사용량 조절
   - 자주 쓰는 단어 학습

3. **상황별 트레이딩 조언**
   - "손실" → 손절 조언
   - "수익" → 분할 익절 조언
   - "살까" → RSI/MACD 확인 조언

---

## 📊 업데이트 체크리스트

### 언어 업데이트 시
- [ ] 새 지식이 DB에 저장되었는가?
- [ ] 중복 질문은 제거되었는가?
- [ ] quality_score가 적절한가?
- [ ] 테스트 대화로 응답 확인했는가?
- [ ] 응답 시간이 0.01초 이하인가? (DB 조회)

### 코드 수정 시
- [ ] 기존 기능이 깨지지 않았는가?
- [ ] Git 커밋 메시지가 명확한가?
- [ ] 로그에 에러가 없는가?
- [ ] 서버가 정상 재시작되었는가?
- [ ] 브라우저 새로고침 후 확인했는가?

---

## 🎯 ChatGPT와 협업 시 전달 사항

### 1. 현재 상태
```
✅ 서버: 정상 작동 중
✅ 이메이: 111개 지식 보유
✅ DB: upbit_bot.db (131KB)
✅ 응답 속도: 0.002초
✅ 사용자 패턴 추적: 작동 중
```

### 2. 필요한 작업
- 언어 업데이트 (새로운 지식 추가)
- 응답 품질 개선
- 학습 데이터 확장
- 기타 요청사항

### 3. 제약사항
- 서버 재시작 최소화
- 크래딧 절약 (로컬 처리 우선)
- 기존 데이터 보존
- Git 히스토리 유지

### 4. 접근 방법
```bash
# 1. 파일 위치 확인
ls -la /home/user/webapp/*.py

# 2. DB 백업
cp upbit_bot.db upbit_bot.db.backup

# 3. 수정 작업
# ... ChatGPT와 협업 ...

# 4. 테스트
python3 test_emei.py

# 5. 커밋 & 재시작
git add -A && git commit -m "..." && git push
pkill -f python3.*upbit && python3 upbit-smart-bot...
```

---

## 📞 문제 발생 시

### 자주 발생하는 문제
1. **서버가 안 떠요**
   - 로그 확인: `tail -f /tmp/bot_clean.log`
   - 포트 충돌: `lsof -i :5000` → `kill -9 PID`

2. **이메이 응답이 안 와요**
   - DB 확인: `sqlite3 upbit_bot.db "SELECT COUNT(*) FROM emei_knowledge"`
   - API 테스트: `curl http://localhost:5000/api/emei/stats`

3. **Git 푸시가 안 돼요**
   - 인증 확인: `git remote -v`
   - 재인증: 자동으로 처리됨

---

**마지막 업데이트**: 2026-02-18 03:10 UTC  
**최신 커밋**: 0e43ff6  
**서버 상태**: ✅ 정상 작동

---

## 🤝 협업 시작하기

ChatGPT에게 이렇게 말하세요:

> "위 문서를 읽고, 이메이 학습 시스템을 업데이트하고 싶어요.  
> 현재 111개 지식이 있고, 응답 속도는 0.002초입니다.  
> [구체적인 요청사항을 여기에 작성]"

**이 파일을 ChatGPT에게 전달하면 모든 컨텍스트를 이해하고 작업할 수 있습니다!** 🚀
