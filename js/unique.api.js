(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

  function jsonpOnce(action, params = {}, timeoutMs = 25000) {
    const { GOOGLE_SCRIPT_URL } = U.CONFIG;

    return new Promise((resolve, reject) => {
      const cb = "cb_" + Date.now() + "_" + Math.random().toString(16).slice(2);
      let finished = false;

      // ✅ 1) 먼저 콜백을 전역에 등록
      window[cb] = (data) => {
        if (finished) return;
        finished = true;
        cleanup();
        resolve(data);
      };

      params.action = action;
      params.callback = cb;
      params._t = Date.now();

      const qs = new URLSearchParams(params).toString();
      const s = document.createElement("script");
      const joiner = GOOGLE_SCRIPT_URL.includes("?") ? "&" : "?";
      s.src = GOOGLE_SCRIPT_URL + joiner + qs;

      const t = setTimeout(() => {
        if (finished) return;
        finished = true;
        cleanup();
        reject(new Error("API timeout"));
      }, timeoutMs);

      s.onerror = () => {
        if (finished) return;
        finished = true;
        cleanup();
        reject(new Error("API load failed"));
      };

      function cleanup(){
        clearTimeout(t);
        try { delete window[cb]; } catch(_){}
        try { s.remove(); } catch(_){}
      }

      // ✅ 2) 그 다음 script 삽입
      document.body.appendChild(s);
    });
  }

  U.api = {
    // ✅ 재시도 포함
    async jsonp(action, params = {}) {
      let lastErr = null;
      for (let i = 1; i <= 3; i++) {
        try {
          const timeoutMs = (i === 1) ? 20000 : 30000;
          return await jsonpOnce(action, params, timeoutMs);
        } catch (e) {
          lastErr = e;
          await sleep(350 * i);
        }
      }
      throw lastErr || new Error("API failed");
    }
  };
})();
