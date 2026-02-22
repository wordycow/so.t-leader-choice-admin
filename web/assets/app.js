(() => {
  const CFG = {
    endpoints: {
      health: "/health",
      systemStatus: "/api/system/status",
      botsStatus: "/api/bots/status",
      chat: "/chat",
      imageBase: "/image/",
      // OPS (관리자)
      opsBotsStart: "/api/ops/bots/start",
      opsBotsStop: "/api/ops/bots/stop",
      opsBotsRestart: "/api/ops/bots/restart",
      opsSystemRestart: "/api/ops/system/restart",
      opsStrategyApply: "/api/ops/strategy/apply",
      opsCommander: "/api/ops/command",
      // logs
      logsList: "/api/ops/logs/list",
      logsRead: "/api/ops/logs/read"
    },
    refreshMs: 15000,
    logTail: 300
  };

  const $ = (id) => document.getElementById(id);

  const state = {
    auto: true,
    selectedLog: "ops_api.log",
    logs: [],
    opsKey: localStorage.getItem("LEEMAY_OPS_KEY") || ""
  };

  function setPill(el, text, kind) {
    el.classList.remove("ok", "warn", "danger");
    if (kind) el.classList.add(kind);
    el.textContent = text;
  }

  function setDot(dotEl, ok) {
    dotEl.classList.toggle("on", !!ok);
    dotEl.classList.toggle("off", !ok);
  }

  function showError(title, detail) {
    const wrap = $("api-error");
    const body = $("api-error-body");
    wrap.hidden = false;
    body.textContent = `${title}\n\n${detail || ""}`.trim();
  }

  function clearError() {
    const wrap = $("api-error");
    wrap.hidden = true;
    $("api-error-body").textContent = "";
  }

  async function apiFetch(url, opts = {}, expectJson = true) {
    const headers = Object.assign(
      { "Content-Type": "application/json" },
      opts.headers || {}
    );

    // OPS KEY는 /api/ops/* 에만 자동 첨부
    if (url.startsWith("/api/ops/") && state.opsKey) {
      headers["X-OPS-KEY"] = state.opsKey;
    }

    const res = await fetch(url, Object.assign({}, opts, { headers }));
    const ct = (res.headers.get("content-type") || "").toLowerCase();

    const readText = async () => {
      try { return await res.text(); } catch { return ""; }
    };

    if (!res.ok) {
      const t = await readText();
      throw new Error(`[HTTP ${res.status}] ${url}\n${t.slice(0, 1200)}`);
    }

    if (!expectJson) return await res.text();

    if (ct.includes("application/json")) {
      return await res.json();
    }

    // JSON 기대했는데 HTML/텍스트가 내려오는 경우(= 네가 지금 본 "JSON 아님" 케이스)
    const t = await readText();
    throw new Error(`[JSON 아님] ${url}\ncontent-type=${ct || "unknown"}\n\n${t.slice(0, 1200)}`);
  }

  function addMsg(role, text) {
    const box = $("chatbox");
    const msg = document.createElement("div");
    msg.className = `msg ${role}`;
    msg.innerHTML = `
      <div class="msg-meta">${role === "user" ? "YOU" : "E-MAY"}</div>
      <div class="msg-body"></div>
    `;
    msg.querySelector(".msg-body").textContent = text;
    box.appendChild(msg);
    box.scrollTop = box.scrollHeight;
  }

  function setEmotion(emotion) {
    const e = emotion || "neutral";
    setPill($("pill-emotion"), `emotion: ${e}`, null);
    $("emotion-img").src = `${CFG.endpoints.imageBase}${encodeURIComponent(e)}?t=${Date.now()}`;
  }

  function renderLogChips() {
    const wrap = $("log-chips");
    wrap.innerHTML = "";

    const list = state.logs.length ? state.logs : [
      { name: "ops_api.log", path: "C:\\leemay_project\\logs\\ops_api.log" },
      { name: "bots_start_last.log", path: "C:\\leemay_project\\logs\\bots_start_last.log" },
      { name: "ai_trading_latest.log", path: "C:\\leemay_project\\logs\\ai_trading_latest.log" }
    ];

    list.forEach((it) => {
      const b = document.createElement("button");
      b.className = "chip" + (it.name === state.selectedLog ? " active" : "");
      b.textContent = it.name;
      b.addEventListener("click", () => {
        state.selectedLog = it.name;
        $("log-path").textContent = `log: ${it.path || "-"}`;
        renderLogChips();
        loadLog().catch(() => {});
      });
      wrap.appendChild(b);
    });

    const selected = list.find(x => x.name === state.selectedLog) || list[0];
    if (selected) {
      state.selectedLog = selected.name;
      $("log-path").textContent = `log: ${selected.path || "-"}`;
    }
  }

  function applyLogFilter(text) {
    const raw = $("logbox").dataset.raw || "";
    if (!text) {
      $("logbox").textContent = raw;
      return;
    }
    const lines = raw.split("\n").filter(l => l.toLowerCase().includes(text.toLowerCase()));
    $("logbox").textContent = lines.join("\n");
  }

  async function loadLog() {
    clearError();
    const data = await apiFetch(`${CFG.endpoints.logsRead}?name=${encodeURIComponent(state.selectedLog)}&tail=${CFG.logTail}`, {}, true);

    // 기대 포맷: { name, path, text }
    const text = data.text || "";
    $("logbox").dataset.raw = text;
    applyLogFilter($("log-filter").value.trim());
  }

  async function refreshStatus() {
    clearError();

    // health (텍스트/JSON 모두 허용)
    try {
      const r = await fetch(CFG.endpoints.health);
      const t = await r.text();
      const ok = r.ok;
      setPill($("pill-health"), `health: ${ok ? "OK" : "FAIL"}`, ok ? "ok" : "danger");
    } catch {
      setPill($("pill-health"), "health: FAIL", "danger");
    }

    // system status
    const s = await apiFetch(CFG.endpoints.systemStatus, {}, true);

    // 기대 포맷(권장):
    // { now, uptime_s, ports:{5001:{ok},5000:{ok},11434:{ok}}, logs:{ai_log,ops_log}, emotion }
    const ports = s.ports || {};
    const p5001 = ports["5001"] || ports[5001] || {};
    const p5000 = ports["5000"] || ports[5000] || {};
    const p11434 = ports["11434"] || ports[11434] || {};

    setDot($("dot-5001"), !!p5001.ok);
    setDot($("dot-5000"), !!p5000.ok);
    setDot($("dot-11434"), !!p11434.ok);

    $("txt-5001").textContent = p5001.ok ? "ON" : "OFF";
    $("txt-5000").textContent = p5000.ok ? "ON" : "OFF";
    $("txt-11434").textContent = p11434.ok ? "ON" : "OFF";

    $("txt-uptime").textContent = (s.uptime_s != null) ? `${s.uptime_s}s` : "-";
    $("txt-ai-log").textContent = (s.logs && s.logs.ai_log) ? s.logs.ai_log : "-";
    $("txt-ops-log").textContent = (s.logs && s.logs.ops_log) ? s.logs.ops_log : "-";

    const nowText = s.now || new Date().toLocaleString();
    setPill($("pill-last"), `Last: ${nowText}`, null);

    // logs list (있으면 반영)
    if (Array.isArray(s.log_files)) {
      state.logs = s.log_files; // [{name,path}]
      renderLogChips();
    }

    // emotion
    if (s.emotion) setEmotion(s.emotion);

    // bots status는 별도(있으면)
    try {
      await apiFetch(CFG.endpoints.botsStatus, {}, true);
    } catch {
      // botsStatus가 없어도 시스템 상태만으로 충분히 표시 가능
    }
  }

  async function opsPost(url, payload = {}) {
    clearError();
    return await apiFetch(url, { method: "POST", body: JSON.stringify(payload) }, true);
  }

  async function doStart() { await opsPost(CFG.endpoints.opsBotsStart); }
  async function doStop() { await opsPost(CFG.endpoints.opsBotsStop); }
  async function doRestartBots() { await opsPost(CFG.endpoints.opsBotsRestart); }
  async function doReboot() { await opsPost(CFG.endpoints.opsSystemRestart); }
  async function doTrain() { await opsPost("/api/ops/learning/trading/start"); } // 서버에서 구현 시 활성
  async function doApply() {
    const ratio = Number($("ir").value) / 100;
    await opsPost(CFG.endpoints.opsStrategyApply, { intelligence_ratio: ratio });
  }

  async function doCommander(cmd) {
    if (!cmd.trim()) return;
    await opsPost(CFG.endpoints.opsCommander, { command: cmd.trim() });
  }

  async function doChat(text) {
    clearError();
    addMsg("user", text);

    const data = await apiFetch(CFG.endpoints.chat, {
      method: "POST",
      body: JSON.stringify({ message: text })
    }, true);

    const reply = data.reply || data.text || "(no reply)";
    addMsg("ai", reply);

    if (data.emotion) setEmotion(data.emotion);
  }

  function bind() {
    $("btn-refresh").addEventListener("click", () => refreshStatus().catch(e => showError("Status Error", e.message)));
    $("btn-engine").addEventListener("click", async () => {
      try { await doStart(); await refreshStatus(); await loadLog().catch(()=>{}); }
      catch(e){ showError("OPS Start Error", e.message); }
    });
    $("btn-stop").addEventListener("click", async () => {
      if (!confirm("매매를 중단(봇 STOP) 하시겠습니까?")) return;
      try { await doStop(); await refreshStatus(); await loadLog().catch(()=>{}); }
      catch(e){ showError("OPS Stop Error", e.message); }
    });
    $("btn-rearm").addEventListener("click", async () => {
      if (!confirm("봇 재정비(봇 RESTART) 하시겠습니까?")) return;
      try { await doRestartBots(); await refreshStatus(); await loadLog().catch(()=>{}); }
      catch(e){ showError("OPS Restart Error", e.message); }
    });
    $("btn-reboot").addEventListener("click", async () => {
      if (!confirm("CONTROL(5001)을 재시작합니다. 잠시 끊길 수 있습니다.\n진행?")) return;
      try { await doReboot(); }
      catch(e){ showError("System Restart Error", e.message); }
    });
    $("btn-train").addEventListener("click", async () => {
      try { await doTrain(); await loadLog().catch(()=>{}); }
      catch(e){ showError("Training Trigger Error", e.message); }
    });

    $("ir").addEventListener("input", () => {
      $("txt-ir").textContent = `${$("ir").value}%`;
    });
    $("btn-apply").addEventListener("click", async () => {
      try { await doApply(); await refreshStatus(); }
      catch(e){ showError("Apply Strategy Error", e.message); }
    });

    $("btn-auto").addEventListener("click", () => {
      state.auto = !state.auto;
      $("btn-auto").textContent = `AUTO: ${state.auto ? "ON" : "OFF"}`;
      $("btn-auto").classList.toggle("ghost", !state.auto);
    });

    $("btn-log-load").addEventListener("click", () => loadLog().catch(e => showError("Log Load Error", e.message)));
    $("btn-log-clear").addEventListener("click", () => {
      $("logbox").textContent = "";
      $("logbox").dataset.raw = "";
    });
    $("log-filter").addEventListener("input", () => applyLogFilter($("log-filter").value.trim()));

    // chat
    const send = async () => {
      const v = $("chat-input").value.trim();
      if (!v) return;
      $("chat-input").value = "";
      try { await doChat(v); }
      catch(e){ showError("Chat Error", e.message); }
    };
    $("btn-send").addEventListener("click", () => send());
    $("chat-input").addEventListener("keydown", (e) => {
      if (e.key === "Enter") send();
    });

    // commander
    $("cmd-input").addEventListener("keydown", async (e) => {
      if (e.key !== "Enter") return;
      const v = $("cmd-input").value;
      $("cmd-input").value = "";
      try { await doCommander(v); await loadLog().catch(()=>{}); }
      catch(err){ showError("Commander Error", err.message); }
    });
  }

  async function init() {
    setEmotion("neutral");
    renderLogChips();

    // logs list를 먼저 가져오면 더 정확
    try {
      const data = await apiFetch(CFG.endpoints.logsList, {}, true);
      if (Array.isArray(data.files)) {
        state.logs = data.files; // [{name,path}]
        renderLogChips();
      }
    } catch {
      // 없어도 진행
    }

    try { await refreshStatus(); } catch(e){ showError("Init Status Error", e.message); }
    try { await loadLog(); } catch(e){ showError("Init Log Error", e.message); }

    setInterval(() => {
      if (!state.auto) return;
      refreshStatus().catch(e => showError("Auto Status Error", e.message));
      loadLog().catch(() => {});
    }, CFG.refreshMs);
  }

  bind();
  init();
})();
