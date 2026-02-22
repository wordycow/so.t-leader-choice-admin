# -*- coding: utf-8 -*-
"""
🤖 Lee May Training Center - CONTROL API Server (5001)

[정본 물리 구조 준수]
core/: api_server.py, leemay_brain.py, memory.py, emotion_mapper.py (4개만)

주요 기능
- / -> /web/control_5001.html 리다이렉트
- /web/<file> 정적 서빙
- /health, /api/health, /api/status, /api/ops/status (헬스체크/폴링 200 보장)
- POST /api/chat (+ /chat alias)
- GET  /api/chat/history
- GET  /api/system/status
- GET  /api/bots/status
- POST /api/ops/run  (관리자 토큰 옵션)
- POST /api/conversations/import  (Tampermonkey Logger)
- GET  /image/<emotion> (web/emotions 폴더에서 PNG 제공)
- POST /api/learning/youtube (옵션: youtube-transcript-api 설치 시)
"""

from __future__ import annotations

import os
import re
import sys
import json
import time
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, request, jsonify, send_from_directory, send_file, redirect

# CORS (옵션)
try:
    from flask_cors import CORS  # type: ignore

    _CORS_OK = True
except Exception:
    CORS = None  # type: ignore
    _CORS_OK = False

# psutil (옵션)
try:
    import psutil  # type: ignore

    _PSUTIL_OK = True
except Exception:
    psutil = None  # type: ignore
    _PSUTIL_OK = False

import shutil

# ============================================================
# 🔧 경로 (core 기준 → 상위가 정본 루트)
# ============================================================
CORE_DIR = Path(__file__).resolve().parent
BASE_DIR = CORE_DIR.parent  # C:\leemay_project

WEB_DIR = BASE_DIR / "web"
OPS_DIR = BASE_DIR / "ops"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "server.db"

# import path 보정 (core 4파일만 사용)
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ============================================================
# 📦 core 모듈 로드 (정본 4파일)
# ============================================================
from leemay_brain import LeemayBrain  # noqa: E402
from memory import Memory  # noqa: E402
from emotion_mapper import detect_emotion, get_emotion_image_path  # noqa: E402

brain = LeemayBrain()
memory = Memory()

# ============================================================
# 🌐 Flask & CORS
# ============================================================
app = Flask(__name__)
if _CORS_OK:
    CORS(app, resources={r"/*": {"origins": "*"}})

# ============================================================
# 🗃️ SQLite (chat history + imported messages)
# ============================================================
def _db() -> sqlite3.Connection:
    # data 폴더는 정본 구조에 포함되므로, 없으면 생성(필수)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            emotion TEXT,
            image_url TEXT
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS imported_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            source TEXT,
            conversation_id TEXT,
            url TEXT,
            role TEXT,
            content TEXT
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============================================================
# 🔐 OPS 인증(선택): 환경변수 있으면 강제
# ============================================================
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "").strip()


def require_admin() -> bool:
    """
    ADMIN_TOKEN이 비어있으면 인증 없이 통과(개발용).
    설정되어 있으면 헤더 토큰 검사.
    """
    if not ADMIN_TOKEN:
        return True
    token = (
        request.headers.get("X-ADMIN-TOKEN", "").strip()
        or request.headers.get("X-Admin-Key", "").strip()
        or request.headers.get("Authorization", "").replace("Bearer", "").strip()
    )
    return token == ADMIN_TOKEN


# ============================================================
# 🧩 Web 정적 서빙
# ============================================================
@app.get("/")
def root():
    return redirect("/web/control_5001.html")


@app.get("/web/<path:filename>")
def serve_web(filename: str):
    return send_from_directory(str(WEB_DIR), filename)


# ============================================================
# ✅ Health (반드시 200)
# ============================================================
@app.get("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "timestamp": now_ts(),
            "utc": utc_iso(),
            "modules": {
                "Brain": True,
                "MongoMemory": bool(memory.enabled),
                "psutil": _PSUTIL_OK,
                "cors": _CORS_OK,
            },
        }
    ), 200


@app.get("/api/health")
def api_health():
    return jsonify({"ok": True, "timestamp": now_ts(), "utc": utc_iso()}), 200


@app.get("/api/status")
def api_status():
    return jsonify({"ok": True, "service": "control_5001", "timestamp": now_ts()}), 200


@app.get("/api/ops/status")
def api_ops_status():
    # ops 폴더 내 bat 목록을 노출 (정본 6종 정리 전에도 안전)
    items: list[str] = []
    try:
        if OPS_DIR.exists():
            items = sorted([p.name for p in OPS_DIR.glob("*.bat")])
    except Exception:
        items = []
    return jsonify({"ok": True, "timestamp": now_ts(), "ops_scripts": items}), 200


# ============================================================
# 🎭 Emotion image
# ============================================================
@app.get("/image/<emotion>")
def emotion_image(emotion: str):
    try:
        path = get_emotion_image_path(BASE_DIR, emotion)
        if path and os.path.exists(path):
            return send_file(path, mimetype="image/png")
    except Exception:
        pass
    return jsonify({"error": "image not found"}), 404


# ============================================================
# 💬 Chat API (표준)
# ============================================================
def build_chat_response(user_id: str, message: str) -> tuple[str, str, str]:
    emo = detect_emotion(message) if message else "neutral"
    image_url = f"/image/{emo}"

    try:
        resp = brain.chat(user_id, message)
    except Exception:
        resp = "안녕하세요. LeeMay 기본 모드입니다."

    return resp, emo, image_url


@app.post("/api/chat")
@app.post("/chat")  # alias
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or data.get("prompt") or "").strip()
    user_id = (data.get("user_id") or "web_user").strip()

    if not message:
        return jsonify({"error": "message required"}), 400

    response, emotion, image_url = build_chat_response(user_id, message)

    # DB 기록
    conn = _db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history(ts, role, content) VALUES(?,?,?)",
        (now_ts(), "user", message),
    )
    cur.execute(
        "INSERT INTO chat_history(ts, role, content, emotion, image_url) VALUES(?,?,?,?,?)",
        (now_ts(), "assistant", response, emotion, image_url),
    )
    conn.commit()
    conn.close()

    # Mongo(옵션) 기록
    memory.save_chat("user", message, {"user_id": user_id})
    memory.save_chat("assistant", response, {"user_id": user_id, "emotion": emotion})

    return jsonify({"response": response, "emotion": emotion, "image_url": image_url}), 200


@app.get("/api/chat/history")
def api_chat_history():
    limit = int(request.args.get("limit", "50"))
    limit = max(1, min(limit, 500))

    conn = _db()
    cur = conn.cursor()
    cur.execute(
        "SELECT ts, role, content, emotion, image_url FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    items = []
    for r in reversed(rows):
        items.append(
            {
                "ts": r["ts"],
                "role": r["role"],
                "content": r["content"],
                "emotion": r["emotion"],
                "image_url": r["image_url"],
            }
        )
    return jsonify({"ok": True, "items": items}), 200


# ============================================================
# 🧠 Tampermonkey Logger (지식 수신)
# ============================================================
@app.post("/api/conversations/import")
def import_conversation():
    data = request.get_json(silent=True) or {}

    source = (data.get("source") or "Unknown").strip()
    content = (data.get("content") or "").strip()
    conversation_id = (data.get("conversation_id") or "").strip()
    # 호환: conversation_url / url 둘 다
    url = (data.get("conversation_url") or data.get("url") or "").strip()
    role = (data.get("role") or "user").strip()

    if not content:
        return jsonify({"ok": False, "error": "content required"}), 400

    conn = _db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO imported_messages(ts, source, conversation_id, url, role, content) VALUES(?,?,?,?,?,?)",
        (now_ts(), source, conversation_id, url, role, content),
    )
    conn.commit()
    conn.close()

    return jsonify({"ok": True, "status": "captured", "ts": now_ts()}), 200


# ============================================================
# 📊 System / Bots status
# ============================================================
@app.get("/api/system/status")
def system_status():
    # psutil 없으면 최소 정보만
    if not _PSUTIL_OK:
        total, used, free = shutil.disk_usage(str(BASE_DIR))
        return jsonify(
            {
                "cpu": None,
                "memory": None,
                "disk_percent": round((used / total) * 100, 1) if total else None,
                "timestamp": now_ts(),
            }
        ), 200

    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    total, used, free = shutil.disk_usage(str(BASE_DIR))
    disk_pct = round((used / total) * 100, 1) if total else 0.0

    return jsonify(
        {
            "cpu": round(cpu, 1),
            "memory": round(mem.percent, 1),
            "disk": disk_pct,
            "timestamp": now_ts(),
        }
    ), 200


@app.get("/api/bots/status")
def bots_status():
    cf_running = False
    cf_pids: list[int] = []
    py_pids: list[int] = []

    if _PSUTIL_OK:
        for p in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                name = (p.info.get("name") or "").lower()
                if "cloudflared" in name:
                    cf_running = True
                    cf_pids.append(int(p.info["pid"]))
                if "python" in name:
                    py_pids.append(int(p.info["pid"]))
            except Exception:
                pass

    return jsonify(
        {
            "control_5001": {"running": True, "pid": os.getpid()},
            "cloudflared": {"running": cf_running, "pids": cf_pids},
            "python": {"pids": py_pids},
            "timestamp": now_ts(),
        }
    ), 200


# ============================================================
# 🎓 YouTube Learning (옵션)
# ============================================================
_YT_OK = False
try:
    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore

    _YT_OK = True
except Exception:
    _YT_OK = False


def _extract_youtube_id(url: str) -> str:
    if not url:
        return ""
    # youtu.be/<id>
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)
    # v=<id>
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)
    # shorts/<id>
    m = re.search(r"shorts/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)
    return ""


@app.post("/api/learning/youtube")
def learning_youtube():
    if not _YT_OK:
        return jsonify({"ok": False, "error": "youtube-transcript-api not installed"}), 501

    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    langs = data.get("langs") or ["ko", "en"]

    vid = _extract_youtube_id(url)
    if not vid:
        return jsonify({"ok": False, "error": "invalid youtube url"}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid, languages=langs)
        # knowledge_base 저장은 “파일 생성”이 될 수 있어 여기서는 반환만 (정본 원칙 준수)
        return jsonify({"ok": True, "video_id": vid, "items": transcript}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "video_id": vid}), 500


# ============================================================
# 🎛️ OPS API
# ============================================================
@app.post("/api/ops/run")
def ops_run():
    if not require_admin():
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"ok": False, "error": "name required"}), 400

    # 보안: 경로 탈출 금지
    if any(x in name for x in ("..", "\\", "/", ":")):
        return jsonify({"ok": False, "error": "invalid script name"}), 400

    # .bat만 허용
    if not name.lower().endswith(".bat"):
        return jsonify({"ok": False, "error": "only .bat allowed"}), 400

    script = OPS_DIR / name
    if not script.exists():
        return jsonify({"ok": False, "error": "script not found", "script": str(script)}), 404

    try:
        proc = subprocess.run(
            ["cmd.exe", "/c", str(script)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return jsonify(
            {
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": (proc.stdout or "").strip(),
                "stderr": (proc.stderr or "").strip(),
                "script": str(script),
            }
        ), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "script": str(script)}), 500


# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🤖 LEE MAY CONTROL SERVER (5001)")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"WEB_DIR : {WEB_DIR}")
    print("=" * 70)
    app.run(host="0.0.0.0", port=5001, debug=True)