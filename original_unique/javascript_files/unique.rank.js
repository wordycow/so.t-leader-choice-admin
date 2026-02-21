(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  const RANK_REQUIRED = {
    Star1:{left:2,right:1},
    Star2:{left:7,right:7},
    Star3:{left:15,right:15},
    Pro1:{left:40,right:40},
    Pro2:{left:80,right:80},
    Pro3:{left:150,right:150},
    Pro4:{left:250,right:250},
    Pro5:{left:400,right:400},
    Pro6:{left:650,right:650},
    Pro7:{left:1000,right:1000},
    Pro8:{left:2000,right:2000},
    Pro9:{left:3000,right:3000},
    Pro10:{left:4000,right:4000},
  };

  const RANK_ORDER = ["Star1","Star2","Star3","Pro1","Pro2","Pro3","Pro4","Pro5","Pro6","Pro7","Pro8","Pro9","Pro10"];
  const RANK_BADGES = {
    Member:"img/member.png",
    Star1:"img/star1.png", Star2:"img/star2.png", Star3:"img/star3.png",
    Pro1:"img/pro1.png", Pro2:"img/pro2.png", Pro3:"img/pro3.png",
    Pro4:"img/pro4.png", Pro5:"img/pro5.png", Pro6:"img/pro6.png",
    Pro7:"img/pro7.png", Pro8:"img/pro8.png", Pro9:"img/pro9.png", Pro10:"img/pro10.png"
  };

  function pickMeByNameThenId(list, myName, myId){
    const name = String(myName||"").trim();
    const id = String(myId||"").trim();
    if (!name) return null;

    const sameName = list.filter(x => String(x?.name||"").trim() === name);
    if (sameName.length === 0) return null;
    if (sameName.length === 1) return sameName[0];

    if (id) {
      const byId = sameName.find(x => String(x?.id||"").trim() === id);
      if (byId) return byId;
    }
    return sameName[0];
  }

  function applyRankToUI(rank){
    const curImg = document.getElementById("member-rank-img");
    const curMini = document.getElementById("member-rank-mini");
    const nextImg = document.getElementById("next-rank-img");
    const nextMini = document.getElementById("next-rank-mini");
    const goalTitle = document.getElementById("goal-next-rank-title");
    const leftEl = document.getElementById("goal-left-count");
    const rightEl = document.getElementById("goal-right-count");

    const curCode = rank && rank !== "-" ? rank : "Member";
    if (curImg) curImg.src = RANK_BADGES[curCode] || RANK_BADGES.Member;
    if (curMini) curMini.textContent = "현재 직급: " + (curCode === "Member" ? "정회원" : curCode);

    let nextCode = "Star1";
    const idx = RANK_ORDER.indexOf(curCode);
    if (curCode === "Member" || idx < 0) nextCode = "Star1";
    else if (idx < RANK_ORDER.length - 1) nextCode = RANK_ORDER[idx+1];
    else nextCode = "-";

    if (nextImg) nextImg.src = (nextCode !== "-" ? (RANK_BADGES[nextCode] || RANK_BADGES.Member) : RANK_BADGES.Member);
    if (nextMini) nextMini.textContent = "다음 직급: " + (nextCode === "-" ? "-" : nextCode);
    if (goalTitle) goalTitle.innerHTML = '다음 목표: <span>' + (nextCode === "-" ? "-" : nextCode) + '</span>';

    const req = RANK_REQUIRED[nextCode];
    if (req && leftEl && rightEl) {
      leftEl.textContent = String(req.left);
      rightEl.textContent = String(req.right);
    } else if (leftEl && rightEl && nextCode === "Star1") {
      leftEl.textContent = "2";
      rightEl.textContent = "1";
    }
  }

  U.rank = {
    async loadAndApply(){
      const u = U.STATE.user || U.auth.getUser() || {};
      const myName = String(u.name||"").trim();
      const myId = String(u.id||"").trim();

      if (!myName) {
        U.STATE.currentRankCode = "Member";
        applyRankToUI("Member");
        return;
      }

      try{
        const res = await fetch(U.CONFIG.RANK_JSON, { cache: "no-store" });
        if (!res.ok) throw new Error("rank-hall.json load fail");
        const data = await res.json();
        const list = Array.isArray(data) ? data : (data.members || []);
        const me = pickMeByNameThenId(list, myName, myId);
        const rank = U.utils.normalizeRank(me?.rank || "Member");

        U.STATE.currentRankCode = rank;
        window.currentRankCode = rank; // 디버깅용
        applyRankToUI(rank);
      } catch(e){
        console.warn("rank load error:", e);
        U.STATE.currentRankCode = "Member";
        window.currentRankCode = "Member";
        applyRankToUI("Member");
      }
    },

    bindCaptureClicks(){
      // ✅ 중복 바인딩 방지
      if (document.body && document.body.dataset.rankBound === "1") return;
      if (document.body) document.body.dataset.rankBound = "1";

      // rank image/text -> rank page
      document.addEventListener("click", (e) => {
        const hit = e.target && e.target.closest && e.target.closest("#next-rank-img,#next-rank-mini,#member-rank-img,#member-rank-mini");
        if (!hit) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        e.stopPropagation();
        window.open(U.CONFIG.RANK_PAGE, "_blank");
      }, true);

      // promo -> gate
      document.addEventListener("click", async (e) => {
        const btn = e.target && e.target.closest && e.target.closest("#promo-btn");
        if (!btn) return;

        e.preventDefault();
        e.stopImmediatePropagation();
        e.stopPropagation();

        if (U.auth.isHQ()) {
          const w = window.open(U.CONFIG.PROMO_PAGE, "_blank");
          if (!w) window.location.href = U.CONFIG.PROMO_PAGE;
          return;
        }

        if (!U.STATE.currentRankCode) await U.rank.loadAndApply();

        if (!U.utils.isPro1OrHigher(U.STATE.currentRankCode)) {
          alert("Pro1 직급 이상 사용 하실 수 있습니다.");
          return;
        }

        const w = window.open(U.CONFIG.PROMO_PAGE, "_blank");
        if (!w) window.location.href = U.CONFIG.PROMO_PAGE;
      }, true);
    }
  };
})();
