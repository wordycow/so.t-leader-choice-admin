export function normPath(urlStr) {
  const url = new URL(urlStr);
  return (
    decodeURIComponent(url.pathname || "/")
      .replace(/\/{2,}/g, "/")
      .replace(/\/+$/, "")
      .toLowerCase() || "/"
  );
}

export function toInt(v) {
  const n = parseInt(String(v || "0"), 10);
  return Number.isFinite(n) ? n : 0;
}

export function safeKey(s) {
  return String(s)
    .trim()
    .slice(0, 80)
    .replace(/[^a-z0-9가-힣._-]/gi, "_");
}

export function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}
