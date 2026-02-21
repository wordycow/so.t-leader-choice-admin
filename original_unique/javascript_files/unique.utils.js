(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  U.utils = {
    safeJsonParse(s, fallback=null) {
      try { return JSON.parse(s || ""); } catch (_) { return fallback; }
    },
    getTodayKST() {
      const now = new Date();
      const kst = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Seoul" }));
      const y = kst.getFullYear();
      const m = String(kst.getMonth() + 1).padStart(2, "0");
      const d = String(kst.getDate()).padStart(2, "0");
      return `${y}-${m}-${d}`;
    },
    normNick(v){
      return String(v||"")
        .replace(/[\u200B-\u200D\uFEFF]/g,"")
        .replace(/\s+/g," ")
        .trim();
    },
    normalizeRank(raw){
      let t = String(raw||"").trim();
      if (!t) return "Member";
      const u = t.toUpperCase().replace(/\s+/g,"");
      if (u === "MEMBER" || u === "정회원" || u === "회원" || u === "일반") return "Member";
      if (u.startsWith("STAR")) return "Star" + u.replace("STAR","").replace(/[^\d]/g,"");
      if (u.startsWith("PRO"))  return "Pro"  + u.replace("PRO","").replace(/[^\d]/g,"");
      if (t.startsWith("스타")) return "Star" + t.replace("스타","").trim().replace(/[^\d]/g,"");
      if (t.startsWith("프로")) return "Pro"  + t.replace("프로","").trim().replace(/[^\d]/g,"");
      return t.replace(/\s+/g,"");
    },
    isPro1OrHigher(rankCode){
      const r = String(rankCode||"").trim();
      if (!/^Pro\d+$/i.test(r)) return false;
      const n = parseInt(r.replace(/pro/i,""), 10);
      return Number.isFinite(n) && n >= 1;
    }
  };
})();
