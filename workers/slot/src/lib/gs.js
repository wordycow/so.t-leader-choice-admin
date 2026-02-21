// Google Apps Script WebApp 연동 (캐시 포함)
// 기존 worker.js 로직 그대로 옮김

const DEFAULT_BET_UT = 10;

let _cache = { at: 0, cfg: null, stats: null };
const CACHE_TTL_MS = 5000;

export async function getCfgAndStats(GS_WEBAPP_URL) {
  const now = Date.now();
  if (_cache.cfg && now - _cache.at < CACHE_TTL_MS) return _cache;

  const [cfgRes, statsRes] = await Promise.all([
    fetch(`${GS_WEBAPP_URL}?action=getConfig`, { cache: "no-store" })
      .then((r) => r.json())
      .catch(() => null),
    fetch(`${GS_WEBAPP_URL}?action=getStats`, { cache: "no-store" })
      .then((r) => r.json())
      .catch(() => null),
  ]);

  const cfg = cfgRes?.ok ? cfgRes.config : {};
  const stats = statsRes?.ok ? statsRes.stats : {};
  _cache = { at: now, cfg, stats };
  return _cache;
}

export function betFromCfg(cfg) {
  return Math.floor(Number(cfg?.SLOT_BET_UT || DEFAULT_BET_UT)) || DEFAULT_BET_UT;
}

export async function getUserFromSheetByNick(GS_WEBAPP_URL, nickname) {
  const nick = String(nickname || "").trim();
  if (!nick) return null;

  const js = await fetch(
    `${GS_WEBAPP_URL}?action=getUserByNick&nickname=${encodeURIComponent(nick)}`,
    { cache: "no-store" }
  )
    .then((r) => r.json())
    .catch(() => null);

  if (!js?.ok) return null;
  return js.user;
}

export async function getUserFromSheetById(GS_WEBAPP_URL, id) {
  const uid = String(id || "").trim().toLowerCase();
  if (!uid) return null;

  const js = await fetch(
    `${GS_WEBAPP_URL}?action=getUser&id=${encodeURIComponent(uid)}`,
    { cache: "no-store" }
  )
    .then((r) => r.json())
    .catch(() => null);

  if (!js?.ok) return null;
  return js.user;
}

// ✅ 기존 worker.js와 동일: addBalance로 잔액 반영
export async function applySheetDeltaById(GS_WEBAPP_URL, { id, delta }) {
  const qs = new URLSearchParams();
  qs.set("action", "addBalance");
  qs.set("id", String(id));
  qs.set("delta", String(delta));
  qs.set("_t", String(Date.now()));

  const js = await fetch(`${GS_WEBAPP_URL}?${qs.toString()}`, { cache: "no-store" })
    .then((r) => r.json())
    .catch(() => null);

  if (!js?.ok) throw new Error(js?.error || "sheet_apply_failed");
  return js;
}
