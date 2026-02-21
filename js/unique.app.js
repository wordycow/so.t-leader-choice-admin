/* =========================================================
 * js/unique.app.js  (FULL REPLACE / COPY-PASTE)
 * - 앱 부트스트랩(로그인체크 → 스케줄 → UI → 시트동기화 → 직급/설정/가격/ebook → 유튜브)
 * - onclick 전역함수(openTab/registerNickname/sendP2P/handleScheduleSheet/onYouTubeIframeAPIReady) 보장
 * - Casino/Slot 링크에 닉/UID/UT/ID 쿼리 동기화
 * - slot/casino에서 돌아올 때 ?u=&uid=&ut=&id= 로컬스토리지 즉시 반영
 * ========================================================= */

(function () {
  "use strict";

  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  const SLOT_PATH  = "games/slot.html";
  const LOBBY_PATH = "casino.html"; // 현재 main.html 링크(id="btnCasinoLobby") 기본 목적지

  /* -------------------------
   * Utils
   * ------------------------- */
  const isFn = (v) => typeof v === "function";

  function cleanText(v) {
    v = (v ?? "").toString().trim();
    if (!v) return "";
    if (v === "User" || v === "회원 이름") return "";
    return v;
  }

  function cleanNumText(v) {
    v = cleanText(v);
    if (!v) return "";
    // "12,345.67 UT" 같은 표시도 들어올 수 있으니 숫자/점/마이너스만 남김
    const only = v.replace(/[^0-9.\-]/g, "");
    return only || v;
  }

  function textById(id) {
    const el = document.getElementById(id);
    if (!el) return "";
    return cleanText(el.textContent || el.value || "");
  }

  function fromLS(keys) {
    for (const k of keys) {
      const v = cleanText(localStorage.getItem(k));
      if (v) return v;
    }
    return "";
  }

  function fromLSNum(keys) {
    for (const k of keys) {
      const v = cleanNumText(localStorage.getItem(k));
      if (v) return v;
    }
    return "";
  }

  function buildUrl(basePath, paramsObj) {
    const params = new URLSearchParams();
    Object.entries(paramsObj || {}).forEach(([k, v]) => {
      const cv = cleanText(v);
      if (cv) params.set(k, cv);
    });
    const qs = params.toString();
    return qs ? `${basePath}?${qs}` : basePath;
  }

  /* -------------------------
   * Query Sync (slot/casino → main)
   * - ?u= &uid= &ut= &id= 들어오면 즉시 저장
   * ------------------------- */
  function syncFromQuery() {
    try {
      const qs = new URLSearchParams(location.search);

      const u   = cleanText(qs.get("u"));
      const uid = cleanText(qs.get("uid"));
      const ut  = cleanNumText(qs.get("ut"));
      const id  = cleanText(qs.get("id"));

      if (u) {
        localStorage.setItem("slot_player", u);
        localStorage.setItem("unique_nickname", u);
      }
      if (uid) {
        localStorage.setItem("unique_userid", uid);
        localStorage.setItem("uid", uid);
      }
      if (ut) {
        localStorage.setItem("unique_ut", ut);
      }
      if (id) {
        // 예전 호환: id로도 uid 채워주기
        localStorage.setItem("unique_userid", id);
        localStorage.setItem("uid", id);
      }
    } catch (e) {
      console.warn("[query sync] error:", e);
    }
  }

  /* -------------------------
   * Identity getters
   * ------------------------- */
  function getNickname() {
    // 1) localStorage
    const v1 = fromLS(["slot_player", "unique_nickname", "nickname", "userNickname", "the_unique_nickname"]);
    if (v1) return v1;

    // 2) DOM
    const v2 = textById("tb-user-name") || textById("member-name") || textById("nickname");
    if (v2) return v2;

    // 3) window.UNIQUE 상태값
    const v3 =
      cleanText(U.STATE?.nickname) ||
      cleanText(U.STATE?.user?.nickname) ||
      cleanText(U.user?.nickname);
    if (v3) return v3;

    return "";
  }

  function getUid() {
    // 1) localStorage
    const v1 = fromLS(["unique_userid", "uid", "userId", "memberId", "unique_user_id"]);
    if (v1) return v1;

    // 2) DOM
    const v2 =
      textById("member-id") ||
      textById("tb-user-id") ||
      textById("user-id") ||
      textById("uid") ||
      textById("my-uid");
    if (v2) return v2;

    // 3) window.UNIQUE 상태값
    const v3 =
      cleanText(U.STATE?.uid) ||
      cleanText(U.STATE?.userId) ||
      cleanText(U.STATE?.user?.uid) ||
      cleanText(U.STATE?.user?.id) ||
      cleanText(U.user?.uid);
    if (v3) return v3;

    return "";
  }

  function getUt() {
    // 1) localStorage
    const v1 = fromLSNum(["unique_ut", "ut", "balanceUT"]);
    if (v1) return v1;

    // 2) DOM
    const v2 =
      cleanNumText(textById("my-ut-display")) ||
      cleanNumText(textById("my-ut-display-transfer")) ||
      cleanNumText(textById("tb-user-ut")) ||
      cleanNumText(textById("user-ut")) ||
      cleanNumText(textById("ut"));
    if (v2) return v2;

    // 3) window.UNIQUE 상태값
    const v3 =
      cleanNumText(U.STATE?.ut) ||
      cleanNumText(U.STATE?.balanceUT) ||
      cleanNumText(U.STATE?.user?.ut) ||
      cleanNumText(U.user?.ut);
    if (v3) return v3;

    return "";
  }

  function getLoginId() {
    // 1) gate가 저장한 uniqueCurrentUser 우선
    try {
      const raw = localStorage.getItem("uniqueCurrentUser");
      if (raw) {
        const obj = JSON.parse(raw);
        if (obj && obj.id) return cleanText(obj.id);
      }
    } catch (e) {}

    // 2) 호환 키들
    const v2 = fromLS(["unique_userid", "unique_user_id", "user_id", "uid", "id"]);
    if (v2) return v2;

    return "";
  }

  /* -------------------------
   * Casino/Slot link apply
   * - 다양한 id를 모두 지원
   * ------------------------- */
  function applyCasinoLinks() {
    const nick = getNickname();
    const uid  = getUid();
    const ut   = getUt();
    const id   = getLoginId() || uid; // id 호환

    // 저장(다음 페이지에서도 유지)
    if (nick) {
      localStorage.setItem("slot_player", nick);
      localStorage.setItem("unique_nickname", nick);
    }
    if (uid) {
      localStorage.setItem("unique_userid", uid);
      localStorage.setItem("uid", uid);
    }
    if (ut) {
      localStorage.setItem("unique_ut", ut);
    }

    // (A) 로비 링크들
    const lobbyIds = ["btnCasinoLobby"];
    const lobbyUrl = buildUrl(LOBBY_PATH, { u: nick, uid, ut, id });

    // (B) 슬롯 직접 링크들
    const slotIds = ["slotBtnPc", "slotBtnM", "slotCta", "slotBtn"];
    const slotUrl = buildUrl(SLOT_PATH, { u: nick, uid, ut, id });

    function setLink(el, url, needUid) {
      if (!el) return;

      // a 태그면 href / 버튼이면 dataset으로 처리(버튼인 케이스도 방어)
      if (el.tagName === "A") el.href = url;

      const ok = needUid ? !!uid : !!id;
      if (!ok) {
        el.setAttribute("data-slot-disabled", "1");
        el.title = "로그인 후 이용 가능합니다. (회원 UID 필요)";
      } else {
        el.removeAttribute("data-slot-disabled");
        el.title = "";
      }
    }

    lobbyIds.forEach((idName) => setLink(document.getElementById(idName), lobbyUrl, true));
    slotIds.forEach((idName)  => setLink(document.getElementById(idName),  slotUrl,  true));

    return { nick, uid, ut, id, lobbyUrl, slotUrl };
  }

  function bindCasinoLinkGuards() {
    // 클릭 순간에도 한 번 더 보정 + uid 없으면 이동 막기
    document.addEventListener("click", (e) => {
      const a = e.target.closest("#btnCasinoLobby, #slotBtnPc, #slotBtnM, #slotCta, #slotBtn");
      if (!a) return;

      const info = applyCasinoLinks();
      const needUid = true;

      if (needUid && !info.uid) {
        e.preventDefault();
        alert("슬롯/카지노는 메인에서 로그인 후 이용 가능합니다. (회원 UID가 필요해요)");
      }
    });
  }

  /* -------------------------
   * Global bindings for onclick
   * - openTab/registerNickname/sendP2P/handleScheduleSheet/onYouTubeIframeAPIReady
   * ------------------------- */
  function ensureGlobalBindings() {
    function pickFn(paths) {
      for (const path of paths) {
        let cur = window;
        for (const key of path) {
          if (!cur || !(key in cur)) { cur = null; break; }
          cur = cur[key];
        }
        if (isFn(cur)) return cur;
      }
      return null;
    }

    // openTab
    if (!isFn(window.openTab)) {
      const modOpenTab = pickFn([
        ["UNIQUE","ui","openTab"],
        ["UNIQUE","UI","openTab"],
        ["UNIQUE","ui","tabs","openTab"],
      ]);

      window.openTab = function (btn, tabId) {
        try {
          if (modOpenTab) return modOpenTab(btn, tabId);

          // fallback: 탭 active 토글
          const tabButtons = document.querySelectorAll(".tb-tab-btn");
          const contents = document.querySelectorAll(".tb-content");
          tabButtons.forEach(b => b.classList.remove("active"));
          contents.forEach(c => c.classList.remove("active"));

          if (btn && btn.classList) btn.classList.add("active");
          const el = document.getElementById(tabId);
          if (el) el.classList.add("active");
        } catch (e) {
          console.error("[openTab] failed:", e);
        }
      };
    }

    // registerNickname
    if (!isFn(window.registerNickname)) {
      const fn = pickFn([
        ["UNIQUE","ui","registerNickname"],
        ["UNIQUE","wallet","registerNickname"],
        ["UNIQUE","supabase","registerNickname"],
      ]);

      window.registerNickname = function () {
        if (fn) return fn();
        alert("registerNickname 함수가 아직 준비되지 않았습니다. (unique.ui.js / unique.wallet.js / unique.supabase.js 확인)");
        console.warn("[registerNickname] not found");
      };
    }

    // sendP2P
    if (!isFn(window.sendP2P)) {
      const fn = pickFn([
        ["UNIQUE","wallet","sendP2P"],
      ]);

      window.sendP2P = function () {
        if (fn) return fn();
        alert("sendP2P 함수가 아직 준비되지 않았습니다. (unique.wallet.js 확인)");
        console.warn("[sendP2P] not found");
      };
    }

    // handleScheduleSheet (gviz callback)
    if (!isFn(window.handleScheduleSheet)) {
      const fn = pickFn([
        ["UNIQUE","schedule","handleScheduleSheet"],
      ]);
      if (fn) window.handleScheduleSheet = fn;
    }

    // YouTube Iframe API callback
    if (!isFn(window.onYouTubeIframeAPIReady)) {
      const fn = pickFn([
        ["UNIQUE","youtube","onYouTubeIframeAPIReady"],
      ]);
      if (fn) window.onYouTubeIframeAPIReady = fn;
    }

    // 예전 호환: main → slot 직접 이동 함수(혹시 다른 페이지에서 onclick 쓰면 살아있게)
    if (!isFn(window.goCasinoFromMain)) {
      window.goCasinoFromMain = function (e) {
        if (e) e.preventDefault();
        const id = getLoginId();
        if (!id) {
          alert("로그인 정보가 없습니다. 게이트에서 로그인 후 다시 시도하세요.");
          location.href = "the-unique-gate.html";
          return false;
        }
        location.href = buildUrl(SLOT_PATH, { id });
        return false;
      };
    }
  }

  /* -------------------------
   * Main boot
   * ------------------------- */
  async function boot() {
    // 0) onclick 전역함수 먼저 보장
    ensureGlobalBindings();

    // 0-1) 쿼리 동기화 + 링크 보정
    syncFromQuery();
    applyCasinoLinks();
    bindCasinoLinkGuards();

    // 1) 로그인 체크
    if (U.auth && isFn(U.auth.requireLogin)) {
      const ok = U.auth.requireLogin();
      if (!ok) return;
    }

    // 2) 스케줄 로드
    if (U.schedule && isFn(U.schedule.init)) {
      U.schedule.init();
    }

    // 3) 기본 UI
    if (U.ui) {
      isFn(U.ui.updateHeaderUI) && U.ui.updateHeaderUI();
      isFn(U.ui.updateNicknameButton) && U.ui.updateNicknameButton();
      isFn(U.ui.updateWalletUI) && U.ui.updateWalletUI();
      isFn(U.ui.bindBasicButtons) && U.ui.bindBasicButtons();
    }

    // 4) 시트 최신화 + 직급 + 설정 + 가격 + ebook
    if (U.wallet && isFn(U.wallet.refreshUserFromSheet)) {
      await U.wallet.refreshUserFromSheet();

      // 시트에서 닉/uid/ut가 찍힌 뒤 링크 한 번 더 보정
      applyCasinoLinks();

      if (U.ui) {
        isFn(U.ui.updateHeaderUI) && U.ui.updateHeaderUI();
        isFn(U.ui.updateNicknameButton) && U.ui.updateNicknameButton();
        isFn(U.ui.updateWalletUI) && U.ui.updateWalletUI();
      }
    }

    if (U.rank && isFn(U.rank.loadAndApply)) {
      await U.rank.loadAndApply();
      isFn(U.rank.bindCaptureClicks) && U.rank.bindCaptureClicks();
    }

    if (U.wallet) {
      isFn(U.wallet.refreshRewardConfig) && (await U.wallet.refreshRewardConfig());
      isFn(U.wallet.refreshPricing) && (await U.wallet.refreshPricing());

      if (U.ui) {
        isFn(U.ui.updateWalletUI) && U.ui.updateWalletUI();
      }
    }

    if (U.ebooks && isFn(U.ebooks.load)) {
      await U.ebooks.load();
    }

    // 5) 유튜브/보상 버튼 바인딩
    if (U.youtube) {
      isFn(U.youtube.init) && U.youtube.init();
      isFn(U.youtube.bindRewardButton) && U.youtube.bindRewardButton();
      isFn(U.youtube.bindLuckyBox) && U.youtube.bindLuckyBox();
    }

    // 6) 주기 동기화
    const refreshMs = (U.CONFIG && U.CONFIG.REFRESH_MS) ? U.CONFIG.REFRESH_MS : 15000;

    setInterval(async () => {
      try {
        if (U.wallet && isFn(U.wallet.refreshUserFromSheet)) await U.wallet.refreshUserFromSheet();
        if (U.rank && isFn(U.rank.loadAndApply)) await U.rank.loadAndApply();
        if (U.wallet && isFn(U.wallet.refreshRewardConfig)) await U.wallet.refreshRewardConfig();
        if (U.wallet && isFn(U.wallet.refreshPricing)) await U.wallet.refreshPricing();

        if (U.ui) {
          isFn(U.ui.updateHeaderUI) && U.ui.updateHeaderUI();
          isFn(U.ui.updateNicknameButton) && U.ui.updateNicknameButton();
          isFn(U.ui.updateWalletUI) && U.ui.updateWalletUI();
        }

        // 주기적으로도 링크 보정(닉/uid/ut 변동 대응)
        applyCasinoLinks();
      } catch (e) {
        console.warn("[periodic refresh] error:", e);
      }
    }, refreshMs);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

})();
