import { json, corsHeaders } from "./lib/http.js";
import { normPath } from "./lib/utils.js";
import { handleSlotState } from "./slot/state.js";
import { handleSlotSpin } from "./slot/spin.js";

const VERSION = "unique-slot-worker-v6";

export default {
  async fetch(request, env) {
    const path = normPath(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders() });
    }

    try {
      if (path === "/" || path === "/health") {
        return json(
          {
            ok: true,
            version: VERSION,
            routes: ["GET /slot/state?u=닉네임 OR ?id=아이디", "POST /slot/spin {u:'닉네임'} OR {id:'아이디'}"],
          },
          200
        );
      }

      if (path === "/slot/state") {
        if (request.method !== "GET") return json({ ok: false, error: "method_not_allowed", version: VERSION }, 200);
        return await handleSlotState(env, request);
      }

      if (path === "/slot/spin") {
        if (request.method !== "POST") return json({ ok: false, error: "method_not_allowed", version: VERSION }, 200);
        return await handleSlotSpin(env, request);
      }

      return json({ ok: false, error: "not_found", version: VERSION }, 200);
    } catch (e) {
      return json({ ok: false, error: String(e?.stack || e), version: VERSION }, 200);
    }
  },
};
