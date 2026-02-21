// js/unique.config.js
(function () {
  window.UNIQUE = window.UNIQUE || {};
  window.UNIQUE.CONFIG = window.UNIQUE.CONFIG || {};

  const stripSlash = (s) => String(s || "").replace(/\/+$/, "");
  const C = window.UNIQUE.CONFIG;

  // ✅ 공통 백엔드(구글 시트/Apps Script)
  C.GOOGLE_SCRIPT_URL =
    "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec";

  // ✅ Supabase(그대로)
  C.SUPABASE_URL = "https://lrpscubricemcgfssjgg.supabase.co";
  C.SUPABASE_KEY = "sb_publishable_8mMA4oEsuB9j0rc6KsLmtQ_UkJo0Zaq";

  // ✅ 워커 주소
  // - "회원/로그인/닉네임/UT/P2P/슬롯" API는 slot-api에 있음 (네 스샷 routes 기준)
  C.SLOT_API_BASE = stripSlash("https://the-unique-slot-api.wordycow0001.workers.dev");

  // - vault-api는 따로 쓰고 싶을 때만 사용 (기부/금고 등)
  C.VAULT_API_BASE = stripSlash("https://the-unique-vault-api.wordycow0001.workers.dev");

  // ✅ 지금 당장 “로그인/회원/슬롯”이 죽은 걸 살리려면
  // 공통 API BASE를 slot-api로 통일해야 한다.
  C.WORKER_BASE_URL = C.SLOT_API_BASE;

  // ✅ 신/구 호환 키들 (기존 코드가 VAULT_WORKER_BASE를 써도 공통 API로 가게)
  C.SLOT_WORKER_BASE  = C.WORKER_BASE_URL;
  C.VAULT_WORKER_BASE = C.WORKER_BASE_URL;

  // ✅ 레거시 전역 브릿지 (여기서 절대 vault로 덮어쓰면 안 됨)
  window.SLOT_API_BASE  = C.WORKER_BASE_URL;
  window.VAULT_API_BASE = C.VAULT_API_BASE;
  window.WORKER_BASE_URL = C.WORKER_BASE_URL;

  // ✅ 경제/설정
  C.UT_PRICE_FACTOR = 0.30;

  C.RANK_JSON = "rank-hall.json";
  C.RANK_PAGE = "rank-hall.html";
  C.PROMO_PAGE = "the-unique-promo.html";

  C.EBOOK_JSON = "ebook-config.json";
  C.EBOOK_FALLBACK = [
    {
      id: "unique-basic",
      title: "협력을 배우고 협력을 만들어낸다.",
      description: "THE UNIQUE 기본 매뉴얼",
      cover: "img/ebook-the-unique-system-book.jpg",
      link: "ebook.html",
      visible: true,
      order: 1,
      posY: 50,
    },
    {
      id: "unique-sot",
      title: "현대 사회에 맞는 여행도구 so.t",
      description: "so.t 안에서 서로를 챙겨주며 함께 여행을 그린다.",
      cover: "img/ebook-network-marketing-cover.jpg",
      link: "ebook1.html",
      visible: true,
      order: 2,
      posY: 50,
    },
  ];

  C.SCHEDULE_GVIZ_URL =
    "https://docs.google.com/spreadsheets/d/1C4fyJtyBHSaBIWyN_lM75Zp7myvtz3cKfHYUbAmoVQY/gviz/tq?gid=0&tqx=responseHandler:handleScheduleSheet";

  C.YT_VIDEO_ID = "DBcSLPRz0HI";
  C.REFRESH_MS = 30000;

  console.log("[UNIQUE.CONFIG]", {
    WORKER_BASE_URL: C.WORKER_BASE_URL,
    SLOT_API_BASE: C.SLOT_API_BASE,
    VAULT_API_BASE: C.VAULT_API_BASE,
    GOOGLE_SCRIPT_URL: C.GOOGLE_SCRIPT_URL,
  });
})();
