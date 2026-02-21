# 🎯 THE UNIQUE - 프로젝트 마스터 문서

**최종 업데이트**: 2026-02-16
**버전**: v7.0
**Repository**: https://github.com/wordycow/so.t-leader-choice
**Latest Commit**: d60ffc0

---

## 📂 **프로젝트 구조**

### 핵심 페이지 (19개)
```
Entry Points:
├── the-unique-gate.html         (메인 게이트)
├── the-unique-main.html         (대시보드)
└── index.html                   (인덱스)

Core Services:
├── saju.html                    (사주팔자 - 50 UT)
├── tarot.html                   (타로 리딩 - 30 UT)
├── slang.html                   (암호화폐 은어)
├── news.html                    (뉴스 피드)
├── survival.html                (생존 전략 - SF 사이버펑크)
├── exchange-select.html         (거래소 선택)
├── upbit-trend.html             (업비트 트렌드)
└── bithumb-trend.html           (빗썸 트렌드)

User/Management:
├── the-unique-signup.html       (회원가입)
├── rank-hall.html               (랭킹 홀)
└── buy.html                     (UT 구매)

Ebook System:
├── the-unique-ebook.html        (전자책 메인)
├── ebook.html                   (전자책 목록)
├── ebook1.html                  (전자책 1)
├── ebook2.html                  (전자책 2)
└── ebook-view.html              (전자책 뷰어)
```

---

## 🎨 **디자인 시스템**

### 핵심 CSS 파일
```css
css/the-unique-core.css          (15.1 KB - 메인 디자인 시스템)
css/hover-visibility-enhanced.css (11.3 KB - 호버 효과 v4.1)
```

### 디자인 철학
| 페이지 | 컨셉 | 색상 |
|--------|------|------|
| **News** | 전문 뉴스 플랫폼 | 그레이 그라데이션 (#f8f9fa → #e9ecef) |
| **Survival** | 첨단 SF 사이버펑크 | 다크 시안 (#0f2027 → #2c5364) + 네온 블루 |
| **Main** | 다크 골드 럭셔리 | 다크 그라데이션 + 골드 액센트 |

---

## 💰 **UT 포인트 시스템**

### 서비스별 UT 비용
- **사주팔자**: 50 UT
- **타로 리딩**: 30 UT
- **슬롯 게임**: 베팅 시 차감
- **룰렛 게임**: 베팅 시 차감

### 기술 스택
```javascript
Google Apps Script:
  - GOOGLE_SCRIPT_URL (js/unique.config.js line 10)
  - doGet/doPost 핸들러
  - Google Sheets 연동

Cloudflare Workers:
  - Slot API: https://the-unique-slot-api.wordycow0001.workers.dev
  - Vault API: https://the-unique-vault-api.wordycow0001.workers.dev
```

### UT 시스템 구현 위치
```
사주 페이지 (saju.html):
  - Line 1200-1250: UT 잔액 표시
  - Line 800-850: AI 분석 버튼 클릭 시 UT 차감

타로 페이지 (tarot.html):
  - Line 1550-1600: UT 잔액 표시
  - Line 1163: selectSpread() - 스프레드 선택 시 UT 차감
```

---

## 🎮 **게임 시스템**

### 슬롯 게임
```
파일: games/slot/slot.game.js
핵심 함수:
  - onSpinClick() (line 202): 스핀 실행
  - API 호출: /api/spin (POST)
  - UT 차감 로직 포함
```

### 룰렛 게임
```
위치: 확인 필요
TODO: 룰렛 파일 위치 및 UT 차감 로직 검증
```

---

## 🔧 **주요 이슈 & 해결 기록**

### v7.0 (2026-02-16) ⭐ NEW
✅ **완료**: 거래소 트렌드 대시보드 v7.0 - 트렌드 주도 국가 & 고래 움직임
  - **트렌드 주도 국가 분석**:
    - 실제 API 데이터 통합 (Binance + Upbit)
    - 각 급등 코인의 주도 거래소/국가 식별
    - 국가별 거래량 점유율 계산
    - 실시간 거래량 USD 표시
  - **고래 움직임 한줄 알림**:
    - 깔끔한 한줄 이미지 스타일 UI
    - ⚠️ 지갑→거래소 = 매도 가능성
    - ✅ 거래소→지갑 = 장기 보유
    - 🔄 거래소↔거래소 = 차익거래
    - 호버 애니메이션 효과
  - 파일: upbit-trend-enhanced-v7.js (850+ lines, 34 KB)

### v5.3 (2026-02-16)
✅ **해결**: Survival 페이지 배경 이미지 제거
  - 문제: 모든 카드에 복잡한 AI 이미지 배경으로 텍스트 안 보임
  - 해결: rgba() 반투명 배경 + 네온 글로우 적용
  - 파일: survival.html (5곳 수정)

### v5.2 (2026-02-16)
✅ **해결**: News & Survival 디자인 전면 개편
  - News: 속보 느낌 → 전문 뉴스 플랫폼
  - Survival: 암울한 폐허 → 첨단 SF 사이버펑크

### v5.0 (2026-02-16)
✅ **해결**: 사주 & 타로 UT 시스템 통합
  - 상단 UT 잔액 표시 추가
  - 서비스 이용 시 UT 차감 로직 구현
  - 애니메이션 알림 추가

### v4.4 (2026-02-16)
✅ **해결**: 저장소 정리
  - 40+ 파일 archive/ 폴더로 이동
  - old-backup 파일 정리
  - upbit-bot-v5, v6 아카이브

---

## 📋 **미완료 작업 (우선순위)**

### 🔴 HIGH Priority
1. **Whale Alert API 키 발급**
   - 실제 고래 움직임 데이터 연동
   - API: https://whale-alert.io/
   - 대규모 트랜잭션 실시간 모니터링

2. **Coinglass API 연동**
   - 롱/숏 포지션 실제 데이터
   - 청산 데이터 실시간 업데이트
   - Exchange dominance 정확한 수치

3. **UT 시스템 실제 테스트**
   - 실사용 계정으로 슬롯 게임 테스트
   - Google Sheets 동기화 확인
   - 잔액 증감 로직 검증

### 🟡 MEDIUM Priority
4. **국가별 USDT 프리미엄 API**
   - 인도, 베트남, 태국, 일본 실제 데이터
   - 실시간 환율 API 통합

5. **룰렛 게임 검증**
   - 파일 위치 확인
   - UT 차감 로직 확인
   - API 연동 테스트

6. **전체 네비게이션 테스트**
   - 모든 버튼 클릭 테스트
   - 페이지 전환 확인
   - 깨진 링크 검사

### 🟢 LOW Priority
6. **성능 최적화**
   - PNG → WebP 변환
   - CSS/JS 압축
   - Lazy loading 적용

7. **접근성 개선**
   - ARIA 레이블 추가
   - 키보드 네비게이션
   - WCAG 2.1 AA 준수

---

## 🚀 **Git Workflow**

### 필수 규칙
```bash
# 1. 코드 수정 후 즉시 커밋
git add -A
git commit -m "type: description"

# 2. 원격 동기화
git fetch origin main
git rebase origin/main

# 3. 충돌 해결 (원격 코드 우선)
# ... conflict resolution ...

# 4. 커밋 스쿼시 (모든 로컬 커밋 합치기)
git reset --soft HEAD~N
git commit -m "comprehensive message"

# 5. 푸시
git push -f origin main

# 6. PR 생성 (genspark_ai_developer → main)
# 7. PR 링크 사용자에게 공유
```

---

## 📱 **SNS & 외부 링크**

```
Discord:   https://discord.gg/3cUN7QXMSY
YouTube:   https://www.youtube.com/@%EC%8F%98%ED%8B%B0So.T
GitHub:    https://github.com/wordycow/so.t-leader-choice

이미지 경로:
  - img/discord-round.png (52 KB)
  - img/youtube-round.png (37 KB)
```

---

## 🎯 **다음 세션 시작 시 체크리스트**

1. ✅ 이 문서 (PROJECT_MASTER.md) 읽기
2. ✅ 최신 커밋 확인: `git log -5 --oneline`
3. ✅ 미완료 작업 우선순위 확인
4. ✅ 진행 중인 이슈 확인
5. ✅ 사용자 요청사항 파악

---

**작성일**: 2026-02-16
**다음 업데이트**: 주요 변경사항 발생 시
