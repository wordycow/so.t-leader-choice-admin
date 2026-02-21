# 🔍 디버깅 필요 파일 목록

## 메인 봇 파일
- `upbit-smart-bot-v8.0-ULTIMATE.py` (3,500+ 줄)
  - Line 2436-2570: `bot_main_loop()` 함수 (스캔 로직 포함)
  - Line 1490-1575: `check_exit()` 함수 (청산 조건)
  - Line 2474-2556: while 루프 (스캔 실행 부분)

## 봇 상태 관리
- `bot_state_manager.py`
  - Line 75-91: `get_bot_state()` - DB에서 봇 상태 로드
  - Line 83: entry_time datetime 변환 로직

## 데이터베이스
- `upbit_bot.db`
  - 테이블: bot_states, trades, emei_knowledge

## 현재 증상
1. 봇 시작 ✅ 정상
2. 루프 실행 ✅ "루프 #1, #2..." 로그 출력
3. 스캔 실행 ❌ "티커 스캔 중..." 메시지 없음
4. 추가 매수 ❌ 1종목만 보유, 3종목까지 가능한데 신규 진입 없음

## 체크포인트
- [ ] Line 2500: `if len(bot_state['simulation_holdings']) < max_positions:` 조건 평가
- [ ] Line 2492-2495: `check_exit()` 에서 예외 발생 여부
- [ ] Line 2520: 스캔 시작 로그 출력 여부
- [ ] bot_state['simulation_holdings'] 실제 값 확인
