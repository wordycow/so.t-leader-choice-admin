(function () {
  "use strict";

  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  // 네임스페이스 안전장치
  U.STATE = U.STATE || {};
  U.ui = U.ui || {};

  function safeIsHQ() {
    try {
      return !!(U.auth && typeof U.auth.isHQ === "function" && U.auth.isHQ());
    } catch (_) {
      return false;
    }
  }

  function safeGetUser() {
    try {
      if (U.STATE && U.STATE.user) return U.STATE.user;
      if (U.auth && typeof U.auth.getUser === "function") return U.auth.getUser();
    } catch (_) {}
    return {};
  }

  function openTab(evtOrEl, tabName){
  const content = document.getElementsByClassName("tb-content");
  for (let i=0;i<content.length;i++) content[i].classList.remove("active");

  const tablinks = document.getElementsByClassName("tb-tab-btn");
  for (let i=0;i<tablinks.length;i++) tablinks[i].classList.remove("active");

  const target = document.getElementById(tabName);
  if (target) target.classList.add("active");

  const el = (evtOrEl && evtOrEl.currentTarget) ? evtOrEl.currentTarget : evtOrEl; // ✅ 핵심
  if (el && el.classList) el.classList.add("active");
}

  function updateHeaderUI() {
    const u = safeGetUser();
    const id = String(u.id || "").trim();
    const name = String(u.name || "").trim();
    const team = String(u.team || "").trim();

    const hello = document.getElementById("member-hello");
    if (hello) hello.textContent = (name || id || "멤버") + "님, 오늘도 성장하러 오셨군요.";

    const memberName = document.getElementById("member-name");
    if (memberName) memberName.textContent = id || "Unknown";

    const teamEl = document.getElementById("member-team");
    if (teamEl) teamEl.textContent = safeIsHQ() ? "소속: HQ" : (team ? "소속: " + team : "소속: -");

    const tbUser = document.getElementById("tb-user-name");
    if (tbUser) tbUser.textContent = name || id || "User";

    const adminLink = document.getElementById("ebook-admin-link");
    if (adminLink && !safeIsHQ()) adminLink.style.display = "none";
  }

  function updateNicknameButton() {
    const btn = document.getElementById("btn-nick-reg");
    if (!btn) return;

    const u = safeGetUser();
    const id = String(u.id || "").toLowerCase().trim();
    const savedNick = (id ? localStorage.getItem("myNickname_" + id) : "") || "";

    if (savedNick) {
      btn.textContent = "닉네임: " + savedNick;
      btn.classList.add("done");
      btn.onclick = null;
    } else {
      btn.textContent = "닉네임 등록";
      btn.classList.remove("done");
      // inline onclick이 있어도, 여기선 안전하게 전역 래퍼 연결
      btn.onclick = window.registerNickname || null;
    }
  }

  function updateWalletUI() {
    const rawUt = Number.parseFloat(localStorage.getItem("myUtPoints") || "0");
    const ut = Number.isFinite(rawUt) ? rawUt : 0;

    const rawPrice = Number(U.STATE && U.STATE.utPrice);
    const price = (Number.isFinite(rawPrice) && rawPrice > 0) ? rawPrice : 0.02;

    // tab-main
    const myUtEl = document.getElementById("my-ut-display");
    if (myUtEl) myUtEl.textContent = ut.toFixed(2);

    const myUsdtEl = document.getElementById("my-usdt-display");
    if (myUsdtEl) myUsdtEl.textContent = `≈ ${(ut * price).toFixed(2)} USDT 환산(정산가)`;

    const rateLine = document.getElementById("ut-rate-line");
    if (rateLine) rateLine.textContent = `1 UT = ${price.toFixed(6)} USDT (정산가 · 매일 00:00 KST 갱신)`;

    // tab-transfer (좌측 자산)
    const myUtTransfer = document.getElementById("my-ut-display-transfer");
    if (myUtTransfer) myUtTransfer.textContent = ut.toFixed(2);

    const myUsdtTransfer = document.getElementById("my-usdt-display-transfer");
    if (myUsdtTransfer) myUsdtTransfer.textContent = `≈ ${(ut * price).toFixed(2)} USDT 환산(정산가)`;

    const rateTransfer = document.getElementById("ut-rate-line-transfer");
    if (rateTransfer) rateTransfer.textContent = `1 UT = ${price.toFixed(6)} USDT (정산가 · 매일 00:00 KST 갱신)`;

    // tab-transfer (우측 뱃지)
    const badge = document.getElementById("my-ut-transfer-badge");
    if (badge) badge.textContent = `보유: ${Math.floor(ut).toLocaleString()} UT`;
  }

  function bindBasicButtons() {
    const workBtn = document.getElementById("work-btn");
    if (workBtn && workBtn.dataset.bound !== "1") {
      workBtn.dataset.bound = "1";
      workBtn.addEventListener("click", () => window.open("the-unique-work-tool.html", "_blank"));
    }

    const sotBtn = document.getElementById("sot-btn");
    if (sotBtn && sotBtn.dataset.bound !== "1") {
      sotBtn.dataset.bound = "1";
      sotBtn.addEventListener("click", () => window.open("https://www.ssoti.com/", "_blank"));
    }

    const travelBtn = document.getElementById("travel-btn");
    if (travelBtn && travelBtn.dataset.bound !== "1") {
      travelBtn.dataset.bound = "1";
      travelBtn.addEventListener("click", () => window.open("index.html", "_blank"));
    }

    const linkonBtn = document.getElementById("ppt-form-btn");
    if (linkonBtn && linkonBtn.dataset.bound !== "1") {
      linkonBtn.dataset.bound = "1";
      linkonBtn.addEventListener("click", () => window.open("https://www.pi-meta.com/main/", "_blank"));
    }

    const marketBtn = document.getElementById("market-btn");
    if (marketBtn && marketBtn.dataset.bound !== "1") {
      marketBtn.dataset.bound = "1";
      marketBtn.addEventListener("click", () => window.open("market.html", "_blank"));
    }

    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn && logoutBtn.dataset.bound !== "1") {
      logoutBtn.dataset.bound = "1";
      logoutBtn.addEventListener("click", () => {
        if (confirm("로그아웃 하시겠습니까?")) {
          localStorage.removeItem("uniqueCurrentUser");
          window.location.href = "the-unique-gate.html";
        }
      });
    }
  }

  // ✅ inline onclick 방지용 전역 래퍼 (로딩 순서 때문에 "not defined" 에러 뜨는 거 막음)
  function bindGlobals() {
    window.openTab = openTab;

    if (typeof window.registerNickname !== "function") {
      window.registerNickname = function () {
        // 나중에 실제 구현이 로딩되면 그걸 쓰게끔 유도
        if (U.nick && typeof U.nick.registerNickname === "function") return U.nick.registerNickname();
        alert("닉네임 기능 로딩중입니다. 잠시 후 다시 시도해주세요.");
      };
    }

    if (typeof window.sendP2P !== "function") {
      window.sendP2P = function () {
        if (U.wallet && typeof U.wallet.sendP2P === "function") return U.wallet.sendP2P();
        alert("송금 기능 로딩중입니다. 잠시 후 다시 시도해주세요.");
      };
    }
  }

  function init() {
    bindGlobals();
    bindBasicButtons();
    try { updateHeaderUI(); } catch (_) {}
    try { updateNicknameButton(); } catch (_) {}
    try { updateWalletUI(); } catch (_) {}
  }

  // 외부에서 호출 가능하게 노출
  U.ui.openTab = openTab;
  U.ui.updateHeaderUI = updateHeaderUI;
  U.ui.updateNicknameButton = updateNicknameButton;
  U.ui.updateWalletUI = updateWalletUI;
  U.ui.bindBasicButtons = bindBasicButtons;
  U.ui.init = init;

  // 중복 init 방지
  if (!window.__UNIQUE_UI_INIT__) {
    window.__UNIQUE_UI_INIT__ = true;
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }
})();
