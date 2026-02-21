export function symbolsFromConfig(cfg) {
  const w = (k, def) => {
    const n = Number(cfg?.[k]);
    return Number.isFinite(n) ? n : def;
  };

  return [
    { id: "star1", weight: w("SLOT_W_STAR1", 22), payout: 2 },
    { id: "star2", weight: w("SLOT_W_STAR2", 18), payout: 3 },
    { id: "star3", weight: w("SLOT_W_STAR3", 14), payout: 5 },

    { id: "pro1", weight: w("SLOT_W_PRO1", 12), payout: 8 },
    { id: "pro2", weight: w("SLOT_W_PRO2", 9), payout: 12 },
    { id: "pro3", weight: w("SLOT_W_PRO3", 7), payout: 16 },
    { id: "pro4", weight: w("SLOT_W_PRO4", 5), payout: 24 },
    { id: "pro5", weight: w("SLOT_W_PRO5", 4), payout: 32 },
    { id: "pro6", weight: w("SLOT_W_PRO6", 3), payout: 48 },
    { id: "pro7", weight: w("SLOT_W_PRO7", 2.5), payout: 64 },
    { id: "pro8", weight: w("SLOT_W_PRO8", 2), payout: 96 },
    { id: "pro9", weight: w("SLOT_W_PRO9", 1.5), payout: 128 },
    { id: "pro10", weight: w("SLOT_W_PRO10", 1), payout: 200 },
  ];
}

export function pickSymbol(symbols) {
  const total = symbols.reduce((a, b) => a + Number(b.weight || 0), 0);
  let r = Math.random() * total;

  for (const s of symbols) {
    r -= Number(s.weight || 0);
    if (r <= 0) return s;
  }
  return symbols[0];
}
