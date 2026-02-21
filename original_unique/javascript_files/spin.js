import { json } from "../lib/http.js";
import { toInt, safeKey, clamp } from "../lib/utils.js";
import {
  getCfgAndStats,
  betFromCfg,
  getUserFromSheetById,
  getUserFromSheetByNick,
  applySheetDeltaById,
} from "../lib/gs.js";
import { symbolsFromConfig, pickSymbol } from "./symbols.js";

const VERSION = "unique-slot-worker-v6";

// KV keys
const K_JACKPOT = "slot:jackpot";
const K_HOUSE = "slot:houseProfit";
const K_FS_PREFIX = "slot:fs:";

function requireKV(env) {
  if (!env.DONATIONS_KV) throw new Error("DONATIONS_KV missing");
}

function getBodyUser(body) {
  return String(body?.u || body?.user || "").trim();
}
function getBodyId(body) {
  return String(body?.id || body?.uid || "").trim().toLowerCase();
}

export async function handleSlotSpin(env, request) {
  requireKV(env);

  const GS_WEBAPP_URL = env.GS_WEBAPP_URL;

  const body = await request.json().catch(() => ({}));
  const id = getBodyId(body);
  const nickname = getBodyUser(body);

  if (!id && !nickname) return json({ ok: false, error: "missing_user", version: VERSION }, 200);

  const { cfg, stats } = await getCfgAndStats(GS_WEBAPP_URL);
  const bet = betFromCfg(cfg);
  const symbols = symbolsFromConfig(cfg);

  // 유저 조회 (id 우선)
  const user = id ? await getUserFromSheetById(GS_WEBAPP_URL, id) : await getUserFromSheetByNick(GS_WEBAPP_URL, nickname);
  if (!user) return json({ ok: false, error: "user_not_found_in_sheet", version: VERSION }, 200);

  const identity = { id: String(user.id || ""), nickname: String(user.nickname || ""), name: String(user.name || "") };

  // free spin
  const fsKey = safeKey(identity.id || identity.nickname || "");
  let fs = fsKey ? toInt(await env.DONATIONS_KV.get(K_FS_PREFIX + fsKey)) : 0;
  const usedFreeSpin = fs > 0;
  if (usedFreeSpin) fs -= 1;

  // 잭팟/하우스
  let jackpot = toInt(await env.DONATIONS_KV.get(K_JACKPOT));
  let house = toInt(await env.DONATIONS_KV.get(K_HOUSE));

  // 잔액 체크
  const bal = Number(user.balance || 0);
  if (!usedFreeSpin && bal < bet) {
    return json({ ok: false, error: "insufficient_balance", version: VERSION, ut: bal, bet }, 200);
  }

  // bet 분배
  const betCharged = usedFreeSpin ? 0 : bet;
  let jackpotNext = jackpot;
  let houseNext = house;

  if (!usedFreeSpin) {
    const toJackpot = Math.floor(bet * 0.5);
    const toHouse = bet - toJackpot;
    jackpotNext += toJackpot;
    houseNext += toHouse;
  }

  // grid 3x5
  const GRID_ROWS = 3,
    GRID_COLS = 5;
  const grid = [];
  for (let r = 0; r < GRID_ROWS; r++) {
    const row = [];
    for (let c = 0; c < GRID_COLS; c++) row.push(pickSymbol(symbols).id);
    grid.push(row);
  }

  // 당첨: 가운데줄 가운데3칸 동일
  const a = grid[1][1],
    b = grid[1][2],
    c = grid[1][3];
  let isWinLine = a === b && b === c;

  // 공급량 기반 승률 억제(옵션)
  const totalSupply = Number(stats?.total_ut_supply || 0);
  const target = Number(cfg?.SLOT_SUPPLY_TARGET || 500000);
  const sens = Number(cfg?.SLOT_SUPPLY_SENS || 0.5);
  const baseAccept = Number(cfg?.SLOT_WIN_ACCEPT ?? 1.0);
  const supplyRatio = target > 0 ? totalSupply / target : 1;

  let accept = baseAccept;
  if (Number.isFinite(supplyRatio) && Number.isFinite(sens)) {
    const adj = 1 / Math.pow(Math.max(0.0001, supplyRatio), Math.max(0, sens));
    accept = clamp(baseAccept * adj, 0, 1);
  }

  if (isWinLine) {
    if (Math.random() > accept) {
      grid[1][3] = pickSymbol(symbols).id;
      isWinLine = false;
    }
  }

  // payout
  let win = 0;
  let winType = "LOSE";

  if (isWinLine) {
    const sym = symbols.find((s) => s.id === a);
    const mul = Number(sym?.payout || 0);
    win = mul * bet;
    winType = a === "pro10" ? "JACKPOT" : "WIN";

    let remain = win;
    if (houseNext >= remain) {
      houseNext -= remain;
      remain = 0;
    } else {
      remain -= houseNext;
      houseNext = 0;
      jackpotNext = Math.max(0, jackpotNext - remain);
      remain = 0;
    }
  }

  // free spin 보너스
  const star3Count = grid.flat().filter((x) => x === "star3").length;
  let awardedFreeSpin = 0;
  if (star3Count >= 3) {
    fs += 1;
    awardedFreeSpin = 1;
  }

  // delta
  const delta = win - betCharged;

  // ✅ 시트 반영 (id 기반)
  await applySheetDeltaById(GS_WEBAPP_URL, { id: identity.id, delta });

  // KV 업데이트
  await env.DONATIONS_KV.put(K_JACKPOT, String(jackpotNext));
  await env.DONATIONS_KV.put(K_HOUSE, String(houseNext));
  if (fsKey) await env.DONATIONS_KV.put(K_FS_PREFIX + fsKey, String(fs));

  // 최신 잔액 재조회
  const userAfter = await getUserFromSheetById(GS_WEBAPP_URL, identity.id);
  const utAfter = Number(userAfter?.balance || 0);

  return json(
    {
      ok: true,
      version: VERSION,
      identity,
      ut: utAfter,
      bet,
      betCharged,
      win,
      net: win - betCharged,
      winType,
      grid,
      jackpot: jackpotNext,
      house: houseNext,
      freeSpins: fs,
      awardedFreeSpin,
    },
    200
  );
}
