import { json } from "../lib/http.js";
import { toInt, safeKey } from "../lib/utils.js";
import { getCfgAndStats, betFromCfg, getUserFromSheetById, getUserFromSheetByNick } from "../lib/gs.js";
import { symbolsFromConfig } from "./symbols.js";

const VERSION = "unique-slot-worker-v6";

// KV keys
const K_JACKPOT = "slot:jackpot";
const K_HOUSE = "slot:houseProfit";
const K_FS_PREFIX = "slot:fs:";

function requireKV(env) {
  if (!env.DONATIONS_KV) throw new Error("DONATIONS_KV missing");
}

function getUserParam(url) {
  const p = url.searchParams;
  return String(p.get("u") || p.get("user") || "").trim();
}
function getIdParam(url) {
  const p = url.searchParams;
  return String(p.get("id") || p.get("uid") || "").trim().toLowerCase();
}

export async function handleSlotState(env, request) {
  requireKV(env);

  const url = new URL(request.url);
  const id = getIdParam(url);
  const nickname = getUserParam(url);

  const GS_WEBAPP_URL = env.GS_WEBAPP_URL;

  let user = null;
  let identity = { id: "", nickname: "", name: "" };

  if (id) {
    user = await getUserFromSheetById(GS_WEBAPP_URL, id);
    identity = { id, nickname: String(user?.nickname || ""), name: String(user?.name || "") };
  } else if (nickname) {
    user = await getUserFromSheetByNick(GS_WEBAPP_URL, nickname);
    identity = { id: String(user?.id || ""), nickname, name: String(user?.name || "") };
  }

  const jackpot = toInt(await env.DONATIONS_KV.get(K_JACKPOT));
  const house = toInt(await env.DONATIONS_KV.get(K_HOUSE));

  const fsKey = safeKey(id || nickname || "");
  const fs = fsKey ? toInt(await env.DONATIONS_KV.get(K_FS_PREFIX + fsKey)) : 0;

  const { cfg, stats } = await getCfgAndStats(GS_WEBAPP_URL);
  const bet = betFromCfg(cfg);
  const symbols = symbolsFromConfig(cfg);

  return json(
    {
      ok: true,
      version: VERSION,
      identity,
      ut: Number(user?.balance || 0),
      bet,
      jackpot,
      house,
      freeSpins: fs,
      symbols,
      stats,
    },
    200
  );
}
