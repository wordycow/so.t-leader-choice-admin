우리는 GitHub Pages 프로젝트에서 The Unique main.html을 12개 JS 모듈로 분리해서 운영 중이다.

✅ 핵심 규칙
- 스케줄 gviz는 main.html에서 직접 로드하지 않고, js/unique.schedule.js가 U.CONFIG.SCHEDULE_GVIZ_URL로 1회 로드한다(중복 방지).
- main.html은 인라인 스크립트 없이 스크립트 로더 역할만 한다.
- HTML onclick 때문에 전역 함수가 반드시 있어야 한다:
  window.openTab, window.registerNickname, window.sendP2P,
  window.handleScheduleSheet, window.onYouTubeIframeAPIReady

✅ main.html 스크립트 로드 순서
1) js/unique.config.js
2) js/unique.state.js
3) js/unique.utils.js
4) js/unique.api.js
5) js/unique.supabase.js
6) js/unique.ui.js
7) js/unique.schedule.js
8) js/unique.rank.js
9) js/unique.ebooks.js
10) js/unique.wallet.js
11) js/unique.youtube.js
12) js/unique.app.js

✅ 부팅
- unique.app.js DOMContentLoaded에서 boot() 실행
- boot() 순서: requireLogin → schedule.init → UI → refreshUserFromSheet → rank.loadAndApply + bindCaptureClicks → refreshRewardConfig → refreshPricing → ebooks.load → youtube.init + bindRewardButton + bindLuckyBox → setInterval(REFRESH_MS)

# UNIQUE MAIN HANDOFF (GitHub Pages)

우리는 GitHub Pages 프로젝트에서 The Unique `main.html`을 12개 JS 모듈로 분리해서 운영 중이다.

---

## ✅ 핵심 규칙 (MAIN)

- 스케줄 gviz는 `main.html`에서 직접 로드하지 않고, `js/unique.schedule.js`가 `U.CONFIG.SCHEDULE_GVIZ_URL`로 **1회 로드**한다(중복 방지).
- `main.html`은 **인라인 스크립트 없이** “스크립트 로더 역할”만 한다.
- HTML onclick 때문에 전역 함수가 반드시 있어야 한다:
  - `window.openTab`
  - `window.registerNickname`
  - `window.sendP2P`
  - `window.handleScheduleSheet`
  - `window.onYouTubeIframeAPIReady`

---

## ✅ main.html 스크립트 로드 순서 (12 modules)

1) `js/unique.config.js`  
2) `js/unique.state.js`  
3) `js/unique.utils.js`  
4) `js/unique.api.js`  
5) `js/unique.supabase.js`  
6) `js/unique.ui.js`  
7) `js/unique.schedule.js`  
8) `js/unique.rank.js`  
9) `js/unique.ebooks.js`  
10) `js/unique.wallet.js`  
11) `js/unique.youtube.js`  
12) `js/unique.app.js`

---

## ✅ 부팅 (MAIN)

- `unique.app.js`에서 `DOMContentLoaded` → `boot()` 실행
- `boot()` 순서:
  - `requireLogin` → `schedule.init` → 기본 UI
  - `refreshUserFromSheet`
  - `rank.loadAndApply + bindCaptureClicks`
  - `refreshRewardConfig` → `refreshPricing` → `ebooks.load`
  - `youtube.init + bindRewardButton + bindLuckyBox`
  - `setInterval(REFRESH_MS)`로 주기 동기화

---

# SLOT GAME HANDOFF (games/slot.html)

슬롯 게임은 **MAIN과 분리된 독립 페이지**이며, 유지보수/업그레이드를 위해 **JS/CSS를 모듈로 분리**해서 운영한다.

---

## ✅ SLOT 목표

- `main.html`에서 클릭해서 진입하면 **닉네임(u) + uid + ut(표시용)** 이 자동 연동된다.
- 슬롯은 **prompt(닉네임 입력창)를 띄우지 않는다.**
- 사운드는 **mp3 소문자 파일만 사용**하고, “대문자 fallback/재시도 코드”는 제거한다.
- 슬롯 UI/룰/연출은 게임답게(심볼 크게, 승리 시 하이라이트/플래시/로그 연출).

---

## ✅ SLOT 폴더 구조
so.t-leader-choice/
games/
slot.html
img/slot/.png
sounds/.mp3
slot/
  slot.css
  slot.config.js
  slot.audio.js
  slot.ui.js
  slot.api.js
  slot.game.js
  slot.app.js

---

## ✅ SLOT 로드 규칙

- `games/slot.html`은 **인라인 JS 최소화**하고, 아래 파일을 `defer`로 로드한다.
- `slot/slot.css`를 별도 로드한다.

### slot.html 스크립트 로드 순서

1) `slot/slot.config.js`  
2) `slot/slot.audio.js`  
3) `slot/slot.ui.js`  
4) `slot/slot.api.js`  
5) `slot/slot.game.js`  
6) `slot/slot.app.js`

---

## ✅ MAIN → SLOT 연동 규칙 (쿼리 파라미터)

MAIN에서 SLOT 링크는 가능하면 아래 파라미터를 함께 넘긴다.

- `u` : 닉네임(필수, 없으면 Guest)
- `uid` : 사용자 고유 ID(가능하면 전달)
- `ut` : 표시용 UT(가능하면 전달, 서버가 최신값 주면 서버값으로 갱신)

예시:
---

## ✅ SLOT 로드 규칙

- `games/slot.html`은 **인라인 JS 최소화**하고, 아래 파일을 `defer`로 로드한다.
- `slot/slot.css`를 별도 로드한다.

### slot.html 스크립트 로드 순서

1) `slot/slot.config.js`  
2) `slot/slot.audio.js`  
3) `slot/slot.ui.js`  
4) `slot/slot.api.js`  
5) `slot/slot.game.js`  
6) `slot/slot.app.js`

---

## ✅ MAIN → SLOT 연동 규칙 (쿼리 파라미터)

MAIN에서 SLOT 링크는 가능하면 아래 파라미터를 함께 넘긴다.

- `u` : 닉네임(필수, 없으면 Guest)
- `uid` : 사용자 고유 ID(가능하면 전달)
- `ut` : 표시용 UT(가능하면 전달, 서버가 최신값 주면 서버값으로 갱신)

예시:games/slot.html?u=이유송&uid=abc123&ut=101

---

## ✅ SLOT 내부 저장 키 (localStorage)

- `slot_player` : 닉네임(u)
- `unique_userid` : uid
- `unique_ut` : ut(표시용 캐시)

⚠️ 슬롯은 localStorage 값을 “마지막 백업”으로만 사용하며, 가능하면 서버 응답으로 최신 표시값을 갱신한다.

---

## ✅ MAIN 쪽 슬롯 링크 브릿지 수정 포인트

`js/unique.app.js`의 슬롯 브릿지(`applySlotLinks()`)에서
`u`만 넘기지 말고 `uid/ut`도 함께 넘길 수 있다.

- URLSearchParams로 `u/uid/ut` 구성
- `#slotBtnPc`, `#slotBtnM` href에 반영
- localStorage에도 `unique_userid`, `unique_ut` 저장

---

## ✅ SLOT API 규칙(방어)

- `/slot/state` 응답은 구현/버전에 따라 키가 다를 수 있으므로 방어적으로 읽는다:
  - `bet`, `jackpot`, `ut` (또는 `state.*`, `user.*`, `balanceUT` 등)
- `/slot/spin` 응답도 `result.win`이 없을 수 있으므로
  - `result.win` → 없으면 `win` → 없으면 0
  - `grid`도 `data.grid` 또는 `data.result.grid` 등 방어 처리
- `result.win` undefined로 인한 크래시가 나지 않게 한다.

---

## ✅ SLOT 룰/연출 기본

- 중앙 하이라이트 라인(가운데 줄)이 “승리 라인”이라는 UI 힌트를 제공한다.
- 승리/잭팟/패배에 따라:
  - 로그 메시지 변화
  - 배경 플래시(짧게)
  - SFX(win/lose/jackpot) 재생

---

## ✅ 작업 원칙

- MAIN(12모듈) 규칙은 깨지지 않는다.
- SLOT은 별도의 분리 모듈로만 업그레이드하며 MAIN을 오염시키지 않는다.
- 변경 시 “어디를 바꿨는지”가 이 문서에 남게 한다(핸드오프 가능 상태 유지).



