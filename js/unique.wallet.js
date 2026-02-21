(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  // =========================
  // ✅ UT 송금 "최근 내역" (로컬 저장 + 렌더)
  // =========================
  const HISTORY_KEY = "ut_recent_history_v1";

  function loadHistory() {
    try {
      const arr = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      return Array.isArray(arr) ? arr : [];
    } catch (_) {
      return [];
    }
  }

  function saveHistory(arr) {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(arr.slice(0, 30))); // 최대 30개
    } catch (_) {}
  }

  function addHistory(item) {
    const arr = loadHistory();
    arr.unshift(item);
    saveHistory(arr);
  }

  function renderHistory() {
    const el = document.getElementById("history-container");
    if (!el) return;

    const arr = loadHistory();

    // ✅ 비어있으면: empty 스타일 ON
    if (!arr.length) {
      el.classList.add("history-empty");
      el.innerHTML = "거래 내역이 없습니다.";
      return;
    }

    // ✅ 내역 있으면: empty 스타일 OFF
    el.classList.remove("history-empty");

    el.innerHTML = arr.slice(0, 30).map(it => {
      const amtColor = it.kind === "out" ? "#fbbf24" : "#4ade80";
      const sign = it.kind === "out" ? "-" : "+";

      return `
        <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.08);">
          <div style="flex:1; min-width:0;">
            <div style="color:#fff; font-weight:700; font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
              ${escapeHtml(it.title || "")}
            </div>
            <div style="color:#64748b; font-size:10px; margin-top:2px;">
              ${escapeHtml(it.date || "")}
            </div>
          </div>
          <div style="color:${amtColor}; font-weight:900; font-size:12px; white-space:nowrap;">
            ${sign}${Number(it.amount || 0)} UT
          </div>
        </div>
      `;
    }).join("");
  }

  // ✅ XSS/깨짐 방지 (닉네임에 특수문자 들어가도 안전)
  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  // ✅ 탭 전환 후에도 보이게: 송금 탭 열 때마다 렌더
  function hookTabRenderOnce() {
    if (window.__utHistoryHooked) return;
    window.__utHistoryHooked = true;

    document.addEventListener("click", (e) => {
      const btn = e.target && e.target.closest && e.target.closest(".tb-tab-btn");
      if (!btn) return;

      // 탭 전환 DOM 반영 이후 갱신
      setTimeout(() => {
        try { renderHistory(); } catch(_) {}
        try { updateUtViz(); } catch(_) {}
      }, 60);
    }, true);
  }

  // =========================
  // ✅ 3D UT 점유 도표 (총 발행 vs 내 보유) 연결
  // =========================
  function fmtNum(n, digits) {
    const x = Number(n);
    if (!Number.isFinite(x)) return "0";
    return x.toLocaleString("en-US", {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits
    });
  }

function updateUtViz() {
  const root = document.querySelector("[data-ut-viz]");
  if (!root) return;

  const ring = root.querySelector("[data-ut-ring]");
  const pctEl = root.querySelector("[data-ut-pct]");
  const totalEl = root.querySelector("[data-ut-total]");
  const myEl = root.querySelector("[data-ut-my]");

  let my = Number((U.STATE?.user?.balance) ?? localStorage.getItem("myUtPoints") ?? 0);
  let total = Number(U.STATE?.totalUT ?? 0);

  if (!Number.isFinite(my) || my < 0) my = 0;
  if (!Number.isFinite(total) || total < 0) total = 0;

  const pct = total > 0 ? Math.max(0, Math.min(100, (my / total) * 100)) : 0;

  const deg = pct * 3.6;
  const dialDeg = total > 0 ? (pct * 1.8) - 90 : -90;

  const p = pct.toFixed(2);

  if (ring) {
    ring.style.setProperty("--p", p);
    ring.style.setProperty("--deg", deg.toFixed(2) + "deg");
    ring.style.setProperty("--dial", dialDeg.toFixed(2) + "deg");
  }

  const donut = root.querySelector(".ut-donut");
  if (donut) {
    donut.style.setProperty("--p", p);
    donut.style.setProperty("--deg", deg.toFixed(2) + "deg");
    donut.style.setProperty("--dial", dialDeg.toFixed(2) + "deg");
  }

  if (pctEl) pctEl.textContent = p;
  if (totalEl) totalEl.textContent = `${fmtNum(total, 0)} UT`;
  if (myEl) myEl.textContent = `${fmtNum(my, 2)} UT`;
}


  // =========================
  // Auth
  // =========================
  U.auth = {
    getUser() {
      return U.utils.safeJsonParse(localStorage.getItem("uniqueCurrentUser"), null);
    },
    setUser(u) {
      localStorage.setItem("uniqueCurrentUser", JSON.stringify(u));
    },
    requireLogin() {
      const u = this.getUser();
      if (!u || !u.id) {
        window.location.href = "the-unique-gate.html";
        return false;
      }
      U.STATE.user = u;
      return true;
    },
    isHQ() {
      const u = U.STATE.user || this.getUser() || {};
      const team = String(u.team || "").trim();
      const name = String(u.name || "").trim();
      return team === "HQ" || (name && team && name === team);
    }
  };

  function applyUserFromSheet(user) {
    const idLower = String(user.id || "").toLowerCase().trim();
    const payload = {
      id: idLower,
      name: user.name || "",
      nickname: user.nickname || "",
      team: user.team || "",
      joinedAt: user.joinedAt || "",
      balance: Number(user.balance || 0)
    };

    U.STATE.user = payload;
    U.auth.setUser(payload);
    localStorage.setItem("myUtPoints", String(payload.balance));

    const nickKey = "myNickname_" + idLower;
    if ((payload.nickname || "").trim()) localStorage.setItem(nickKey, payload.nickname.trim());
    else localStorage.removeItem(nickKey);

    // ✅ 유저 갱신될 때 도표도 즉시 갱신
    try { updateUtViz(); } catch(_) {}
  }

  // ✅ 정산가 저장 키
  const SETTLE_DATE_KEY  = "ut_settlement_date_kst";
  const SETTLE_PRICE_KEY = "ut_settlement_price";
  const SETTLE_META_KEY  = "ut_settlement_meta";

  function getSettlementPrice() {
    const p = Number(localStorage.getItem(SETTLE_PRICE_KEY));
    return Number.isFinite(p) && p > 0 ? p : null;
  }

  function setSettlementPrice(todayKST, price, meta) {
    localStorage.setItem(SETTLE_DATE_KEY, todayKST);
    localStorage.setItem(SETTLE_PRICE_KEY, String(price));
    if (meta) localStorage.setItem(SETTLE_META_KEY, JSON.stringify(meta));
  }

  U.wallet = {
    async refreshUserFromSheet() {
      const u = U.STATE.user || U.auth.getUser();
      if (!u || !u.id) return;

      const r = await U.api.jsonp("getUser", { id: String(u.id).toLowerCase().trim() });
      if (r && r.ok && r.user) applyUserFromSheet(r.user);
    },

    async refreshDonationUSDT() {
      const db = U.supabase.init();
      try {
        const { data, error } = await db.from("profiles").select("donation_total");
        if (error) throw error;
        U.STATE.donationUSDT = (data || []).reduce((acc, r) => acc + (Number(r.donation_total) || 0), 0);
      } catch (e) {
        console.warn("donation_total sum fail:", e);
        U.STATE.donationUSDT = 0;
      }
    },

    async refreshStatsFromSheet() {
      try {
        const r = await U.api.jsonp("getStats", {});
        if (r && r.ok && r.stats) {
          const total = Number(
  r.stats.total_earned_ut ??
  r.stats.total_ut_minted ??
  r.stats.total_ut_supply ??
  r.stats.total_ut ??
  0
);
U.STATE.totalUT = Number.isFinite(total) ? total : 0;


          // ✅ 총 발행 갱신될 때 도표 갱신
          try { updateUtViz(); } catch(_) {}
        }
      } catch (e) {
        console.warn("getStats fail:", e);
        U.STATE.totalUT = 0;
        try { updateUtViz(); } catch(_) {}
      }
    },

    async refreshRewardConfig() {
      try {
        const r = await U.api.jsonp("getConfig", {});
        if (r && r.ok && r.config) {
          const cfg = r.config;
          const vr = Number(cfg.VIDEO_REWARD);
          const er = Number(cfg.EBOOK_REWARD);
          const lm = Number(cfg.LUCKY_MIN);
          const lx = Number(cfg.LUCKY_MAX);

          if (Number.isFinite(vr)) U.STATE.videoReward = Math.floor(vr);
          if (Number.isFinite(er)) U.STATE.ebookReward = Math.floor(er);
          if (Number.isFinite(lm)) U.STATE.luckyMin = Math.floor(lm);
          if (Number.isFinite(lx)) U.STATE.luckyMax = Math.floor(lx);
          if (U.STATE.luckyMax < U.STATE.luckyMin) U.STATE.luckyMax = U.STATE.luckyMin;
        }
      } catch (_) {}
    },

    async refreshPricing() {
      await this.refreshDonationUSDT();
      await this.refreshStatsFromSheet();

      const today = U.utils.getTodayKST();
      const lastSettleDate = localStorage.getItem(SETTLE_DATE_KEY);

      let calc = null;
      if (U.STATE.totalUT > 0) {
        calc = (Number(U.STATE.donationUSDT) * Number(U.CONFIG.UT_PRICE_FACTOR)) / Number(U.STATE.totalUT);
      }
      if (!Number.isFinite(calc) || calc <= 0) calc = 0.02;

      const settlePrice = Number(calc.toFixed(6));

      if (lastSettleDate !== today) {
        setSettlementPrice(today, settlePrice, {
          donationUSDT: Number(U.STATE.donationUSDT) || 0,
          totalUT: Number(U.STATE.totalUT) || 0,
          factor: Number(U.CONFIG.UT_PRICE_FACTOR),
        });
        U.STATE.utPrice = settlePrice;
      } else {
        const p = getSettlementPrice();
        U.STATE.utPrice = p || settlePrice;
      }

      // ✅ 가격/총발행 갱신 끝나면 도표도 갱신
      try { updateUtViz(); } catch(_) {}
    },

    async addUt(delta) {
      const u = U.STATE.user || U.auth.getUser();
      if (!u || !u.id) throw new Error("로그인 정보가 없습니다.");

      const r = await U.api.jsonp("addBalance", { id: String(u.id).toLowerCase().trim(), delta });
      if (!r || !r.ok || !r.user) throw new Error(r?.error || "UT update failed");

      applyUserFromSheet(r.user);
      await this.refreshPricing();

      if (U.ui) {
        U.ui.updateHeaderUI();
        U.ui.updateNicknameButton();
        U.ui.updateWalletUI();
      }

      try { updateUtViz(); } catch(_) {}
    },

    async sendP2P(receiver, amount) {
      const u = U.STATE.user || U.auth.getUser();
      if (!u || !u.id) throw new Error("로그인 정보가 없습니다.");

      const r = await U.api.jsonp("transfer", {
        fromId: String(u.id).toLowerCase().trim(),
        toNickname: receiver,
        amount
      });

      if (!r || !r.ok) throw new Error(r?.error || "송금 실패");

      if (r.fromUser) applyUserFromSheet(r.fromUser);

      await this.refreshUserFromSheet();
      await this.refreshPricing();

      if (U.ui) {
        U.ui.updateHeaderUI();
        U.ui.updateNicknameButton();
        U.ui.updateWalletUI();
      }

      try { updateUtViz(); } catch(_) {}
    }
  };

  // ✅ 전역: 닉네임 등록
  window.registerNickname = async function () {
    const u = U.STATE.user || U.auth.getUser();
    if (!u || !u.id) return alert("로그인 정보가 없습니다.");

    const idLower = String(u.id).toLowerCase().trim();
    const already = localStorage.getItem("myNickname_" + idLower);
    if (already) return alert("이미 등록된 닉네임입니다.");

    const rawNick = prompt("송금에 사용할 닉네임을 입력하세요.\n(변경 불가, 신중히 입력)");
    if (!rawNick) return;

    const nickname = U.utils.normNick(rawNick);
    if (!nickname) return;

    if (!confirm(`'${nickname}' (으)로 설정하시겠습니까?`)) return;

    const btn = document.getElementById("btn-nick-reg");
    const prev = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "처리 중..."; }

    try {
      const r = await U.api.jsonp("setNickname", { id: idLower, nickname });
      if (!r || !r.ok || !r.user) throw new Error(r?.error || "닉네임 저장 실패");

      applyUserFromSheet(r.user);

      if (U.ui) {
        U.ui.updateHeaderUI();
        U.ui.updateNicknameButton();
        U.ui.updateWalletUI();
      }

      try { updateUtViz(); } catch(_) {}

      alert("닉네임이 저장되었습니다.");
    } catch (e) {
      console.error(e);
      alert("저장 실패: " + (e.message || e));
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = prev; }
      if (U.ui) U.ui.updateNicknameButton();
    }
  };

  // ✅ 전역: 송금
  window.sendP2P = async function () {
    const receiver = U.utils.normNick(document.getElementById("p2p-receiver")?.value || "");
    const amount = Number(document.getElementById("p2p-amount")?.value);

    if (!receiver) return alert("받는 분 닉네임을 입력하세요.");
    if (!Number.isFinite(amount) || amount <= 0) return alert("보낼 수량(UT)을 올바르게 입력하세요.");

    const myBal = Number(localStorage.getItem("myUtPoints") || 0);
    if (amount > myBal) return alert("잔액 부족");
    if (!confirm(`${receiver}님에게 ${amount} UT를 송금하시겠습니까?`)) return;

    const btn = document.querySelector(".transfer-btn");
    const prev = btn ? btn.textContent : "";
    if (btn) { btn.disabled = true; btn.textContent = "처리 중..."; }

    try {
      await U.wallet.sendP2P(receiver, amount);

      // ✅ 성공 즉시 "최근 내역" 추가 + 렌더
      addHistory({
        kind: "out",
        title: `→ ${receiver} 송금`,
        amount: amount,
        date: new Date().toLocaleString("ko-KR")
      });
      renderHistory();

      // ✅ 송금 후 도표 반영
      try { updateUtViz(); } catch(_) {}

      alert("송금 완료");
      const amtEl = document.getElementById("p2p-amount");
      if (amtEl) amtEl.value = "";

    } catch (e) {
      console.error(e);
      alert("송금 오류: " + (e.message || e));
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = prev || "송금하기"; }
    }
  };

  // ✅ 페이지 로드 시: 탭 클릭 훅 + 초기 렌더
  hookTabRenderOnce();
  document.addEventListener("DOMContentLoaded", () => {
    try { renderHistory(); } catch(_) {}
    try { updateUtViz(); } catch(_) {}
  });

})();
