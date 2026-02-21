# 📊 REPORT_00: 서버 현황 스냅샷

**생성일시**: 2026-02-18 10:10  
**작성자**: Claude AI Assistant  
**목적**: 코드 수정 전 현황 파악

---

## A. 서버 엔트리포인트

| 항목 | 값 |
|------|-----|
| **메인 파일** | `upbit-smart-bot-v8.0-ULTIMATE.py` (138,797 bytes) |
| **Flask 서버** | Line 1764: `app = Flask(__name__)` |
| **실행 진입점** | Line 3420: `if __name__ == "__main__":` |
| **포트** | 5000 (기본) |
| **서버 URL** | https://5000-imdh8jpm1izc140vdjj3t-3844e1b6.sandbox.novita.ai |

---

## B. IMEI 상담(챗/Q&A) 엔드포인트

| 엔드포인트 | 메서드 | 위치 | 설명 |
|-----------|--------|------|------|
| `/api/emei/chat` | POST | Line 3373 | 메인 채팅 엔드포인트 (Router 사용) |
| `/api/emei/stats` | GET | Line 3405 | 학습 통계 조회 |

**호출 흐름**:
```
Client → /api/emei/chat → emei_router.chat(user_id, message)
                         ↓
                    EmeiRouter 클래스 (emei_response_router.py)
```

---

## C. LLM 호출 위치

| 구분 | 파일 | 위치 | 설명 |
|------|------|------|------|
| **Router 모듈** | `emei_response_router.py` | Line 1~700 | EmeiRouter 클래스 |
| **Ollama 호출** | `emei_response_router.py` | Line 188-217 | `_ollama_chat()` 함수 |
| **프롬프트 생성** | `emei_response_router.py` | Line 220-302 | `_emei_system_prompt()` |
| **모델** | 환경변수 | OLLAMA_MODEL | `qwen2.5:7b` (default) |
| **Ollama URL** | 환경변수 | OLLAMA_URL | `http://ollama.thetheunique.com` |

**프롬프트 구조**:
```python
messages = [
    {"role": "system", "content": system_prompt},  # Emei 정체성 + 규칙
    {"role": "system", "content": context_blocks}, # RAG 검색 결과 (top-k)
    {"role": "user", "content": user_message}
]
```

---

## D. DB 지식 154개 저장 위치/형식

| 항목 | 값 |
|------|-----|
| **DB 파일** | `upbit_bot.db` (SQLite3) |
| **테이블명** | `emei_knowledge` |
| **총 레코드** | **154개** ✅ |
| **스키마** | `(id, question, answer, source, quality_score, use_count, last_used, created_at)` |
| **검색 방식** | **키워드 기반 (Jaccard + SequenceMatcher)** |
| **검색 함수** | `_retrieve_best(user_msg, topk=4)` (Line 172-185) |
| **임베딩 사용** | ❌ (현재 미사용, 향후 개선 가능) |

**검색 알고리즘**:
```python
# 1. 토큰화: 한글/영문/숫자 2글자 이상
utoks = _tokens(user_msg)
qtoks = _tokens(question)

# 2. 유사도 계산
jac = _jaccard(utoks, qtoks)           # Jaccard coefficient
seq = SequenceMatcher(...).ratio()     # Sequence similarity

# 3. 품질 가중치 적용
score = (0.55 * jac + 0.45 * seq) * (0.85 + 0.15 * quality_score)

# 4. Top-K 선택 (기본 4개)
```

---

## E. 트레이딩 엔진 파일 (버전8 핵심)

| 구분 | 값 |
|------|-----|
| **메인 파일** | `upbit-smart-bot-v8.0-ULTIMATE.py` |
| **봇 루프** | Line 2436-2570: `bot_main_loop(user_id, bot_state)` |
| **연습/실전 분기** | Line 2069-2262: `/api/start` 엔드포인트 |
| **모드 저장** | `bot_state['mode']` (practice / live) |
| **실주문 실행** | Line 1379-1476: `execute_trade()` 함수 |
| **청산 실행** | Line 1577-1639: `execute_exit()` 함수 |

**모드 분기 로직**:
```python
# Line 2069-2120: /api/start 엔드포인트
mode = data.get('mode', 'practice')  # 기본값: practice ✅
seed = data.get('seed', 1000000)

if mode == 'live':
    # 라이센스 검증 필요
    txid = data.get('txid', '')
    if len(txid) < 40:
        return jsonify({'warning': 'TXID를 입력하고 라이센스 버튼 클릭 필요'})
    
    # Upbit API 키 로드
    upbit = pyupbit.Upbit(access_key, secret_key)
    bot_state['upbit'] = upbit
else:
    # 연습 모드: API 키 불필요
    bot_state['upbit'] = None
```

**실주문 위치**:
- Line 1379-1476: `execute_trade()` - 매수 주문
- Line 1577-1639: `execute_exit()` - 매도 주문
- 연습 모드에서는 `bot_state['simulation_holdings']`에만 기록
- 실전 모드에서만 `bot_state['upbit'].buy_market_order()` 호출

---

## F. 로그/상태 저장 방식

| 항목 | 위치 | 형식 |
|------|------|------|
| **봇 상태** | DB: `bot_states` 테이블 | SQLite (user_id, running, mode, seed_amount, simulation_krw, simulation_holdings, ...) |
| **거래 기록** | DB: `trades` 테이블 | SQLite (user_id, timestamp, ticker, strategy, ...) |
| **콘솔 로그** | stdout | `log()` 함수 (Line 293-301) |
| **디버그 로그** | `/tmp/bot_{user_id}_debug.log` | 파일 (사용자별) |
| **대화 로그** | DB: `emei_conversations` 테이블 | SQLite (user_id, user_msg, assistant_msg, timestamp) |
| **학습 데이터** | DB: `emei_knowledge` 테이블 | SQLite (question, answer, source, quality_score, ...) |

**디버그 로그 예시**:
```
/tmp/bot_wordycow_debug.log
/tmp/bot_guest_10.64.13.98_debug.log
/tmp/bot_lee1_debug.log
/tmp/bot_1_debug.log
```

**로그 함수 (Line 293-301)**:
```python
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "SUCCESS": "\033[92m", "ERROR": "\033[91m", "WARNING": "\033[93m",
        "INFO": "\033[96m", ...
    }
    color = colors.get(level, "\033[0m")
    print(f"{color}[{timestamp}] {level}: {message}\033[0m")
```

---

## 📈 현재 운영 상태

| 지표 | 값 |
|------|-----|
| **서버 상태** | ✅ 정상 작동 중 |
| **활성 사용자** | 4명 (wordycow, lee1, guest_10.64.13.98, 1) |
| **모드** | 전원 practice (연습) |
| **IMEI 지식** | 154개 |
| **최근 거래** | wordycow: KRW-NEAR, KRW-BTC, KRW-TRX (3종목 보유) |
| **로그인** | wordycow / 1234 |

---

## 🔍 핵심 발견 사항

### ✅ 장점
1. **연습 모드 기본값**: 실수로 실주문 실행 방지 ✅
2. **RAG 시스템 존재**: 154개 지식 DB + 검색 알고리즘 구현 ✅
3. **디버그 로깅**: 사용자별 상세 로그 파일 ✅
4. **모드 분리**: practice/live 명확히 구분 ✅

### ⚠️ 개선 필요
1. **RAG 실제 작동 검증 필요**: 검색 결과가 LLM 프롬프트에 포함되는지 확인 필요
2. **임베딩 미사용**: 현재 키워드 기반, 의미 검색 개선 가능
3. **트레이딩 로그 표준화**: CSV 등 외부 저장 없음
4. **YouTube 소스**: 현재 DB에 통합 여부 불명확

---

**다음 단계**: STEP 1 (RAG 실제 작동 검증) 진행
