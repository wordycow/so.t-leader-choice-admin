# -*- coding: utf-8 -*-
"""
LeeMay Brain (canonical)
- core 폴더의 api_server.py에서 직접 import하여 사용
- Ollama 호출은 여기서만 담당 (서버는 죽지 않고 graceful fallback)
"""

from __future__ import annotations

import os
import json
import urllib.request


def _env(name: str, default: str = "") -> str:
    v = os.environ.get(name, "").strip()
    return v if v else default


OLLAMA_URL = _env("OLLAMA_URL", "http://ollama.thetheunique.com").rstrip("/")
OLLAMA_MODEL = _env("OLLAMA_MODEL", "llama3.1")


class LeemayBrain:
    def __init__(self) -> None:
        self.ollama_url = OLLAMA_URL
        self.model = OLLAMA_MODEL

    def chat(self, user_id: str, message: str) -> str:
        if not message:
            return "메시지를 입력해 주세요."

        payload = {
            "model": self.model,
            "prompt": message,
            "stream": False,
        }

        try:
            req = urllib.request.Request(
                url=f"{self.ollama_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                out = (data.get("response") or "").strip()
                return out if out else "응답이 비어 있습니다."
        except Exception:
            # Ollama 불가 시에도 서버는 정상 동작해야 함
            return "안녕하세요. LeeMay 기본 모드입니다. (Ollama 연결 실패)"