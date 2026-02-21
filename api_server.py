# -*- coding: utf-8 -*-
"""
🤖 Lee May Training Center - API Server (v3.3.1 ULTIMATE - CLEAN FULL)

- OPS(배치 실행/상태/로그 tail/재시작)
- 채팅 저장 + 감정 이미지 연동(response/emotion/image_url 고정)
- 러닝잡(유튜브) 뼈대
- 시뮬 트레이딩
- 감사로그(audit)
- ChatGPT/Gemini Import (/api/conversations/import) + imported_messages 테이블
"""

from flask import Flask, request, jsonify, send_from_directory, session, has_request_context
from flask_cors import CORS
import os
import json
import uuid
import time
import sqlite3
import threading
import subprocess
import glob
import traceback
from datetime import datetime
from pathlib import Path

import psutil


# ============================================================
# 0) 기본 경로/환경
# ============================================================
BASE_DIR = r"C:\leemay_project"

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LEARNING_LOG_DIR = os.path.join(DATA_DIR, "learning_logs")
OPS_DIR = os.path.join(BASE_DIR, "ops")
WEB_DIR = os.path.join(BASE_DIR, "web")

IMAGES_DIR = os.path.join(BASE_DIR, "leemay", "images")

SERVER_DB_PATH = os.path.join(DATA_DIR, "server.db")
SIM_DB_PATH = os.path.join(DATA_DIR, "sim_trading.db")
OPS_LOG_FILE = os.path.join(LOG_DIR, "ops_api.log")

ADMIN_ID = "wordycow"
ADMIN_TOKEN = "1106"
SECRET_KEY = os.environ.get("SECRET_KEY", "LEEMAY_ULTIMATE_SECRET").strip()

YT_LEARNER_CMD = os.environ.get("YT_LEARNER_CMD", "").strip()

# ✅ 5000 기동: SAFE 배치 우선(없으면 기존으로 fallback)
ALLOWED_OPS_SCRIPTS = {
    "control_start": os.path.join(OPS_DIR, "01_CONTROL_START.bat"),
    "bots_start_safe": os.path.join(OPS_DIR, "02_BOTS_START_SAFE_5000.bat"),
    "bots_start": os.path.join(OPS_DIR, "02_BOTS_START.bat"),
    "bots_stop": os.path.join(OPS_DIR, "03_BOTS_STOP.bat"),
    "status": os.path.join(OPS_DIR, "99_STATUS.bat"),
}

# 폴더 자동 생성
for d in [DATA_DIR, LOG_DIR, LEARNING_LOG_DIR, OPS_DIR, WEB_DIR, IMAGES_DIR]:
    Path(d).mkdir(parents=True, exist_ok=True)


# ============================================================
# 1) 유틸/인증
# ============================================================
def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_json(obj) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return "{}"


def get_client_ip() -> str:
    xf = request.headers.get("X-Forwarded-For", "")
    return xf.split(",")[0].strip() if xf else (request.remote_addr or "")


def get_user_id() -> str:
    uid = (request.headers.get("X-USER-ID") or "").strip()
    if not uid and request.is_json:
        body = request.get_json(silent=True) or {}
        uid = (body.get("user_id") or body.get("user") or "").strip()
    if not uid:
        uid = (request.args.get("user_id") or "").strip()
    if not uid:
        uid = (session.get("user_id") or "").strip()
    return uid or "guest"


def is_admin_request() -> bool:
    k1 = (request.headers.get("X-Admin-Key") or "").strip()
    k2 = (request.headers.get("X-ADMIN-TOKEN") or "").strip()
    return (k1 == ADMIN_TOKEN) or (k2 == ADMIN_TOKEN)


def is_admin() -> bool:
    uid = get_user_id()
    if uid == ADMIN_ID and is_admin_request():
        return True
    if uid == ADMIN_ID and session.get("is_admin") is True:
        return True
    return False


def log_ops(message: str):
    try:
        Path(OPS_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(OPS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] {message}\n")
    except Exception:
        pass


def check_port_socket(port: int) -> bool:
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()
        return result == 0
    except Exception:
        return False


def latest_ai_trading_log() -> str:
    """
    5000 쪽 로그 파일 후보를 최대한 넓게 잡아서 최신을 반환
    """
    try:
        candidates = []
        candidates += glob.glob(os.path.join(LOG_DIR, "ai_trading_5000_*.log"))
        candidates += glob.glob(os.path.join(LOG_DIR, "ai_trading_5000_*stdout*.log"))
        candidates += glob.glob(os.path.join(LOG_DIR, "ai_trading_5000_*stderr*.log"))
        # SAFE 배치에서 쓰는 고정 파일도 고려
        fixed1 = os.path.join(LOG_DIR, "ai_trading_5000_stdout.log")
        fixed2 = os.path.join(LOG_DIR, "ai_trading_5000_stderr.log")
        for fx in [fixed1, fixed2]:
            if os.path.exists(fx):
                candidates.append(fx)

        candidates = list(set(candidates))
        if not candidates:
            return ""
        candidates.sort(key=lambda p: os.path.getmtime(p))
        return candidates[-1]
    except Exception:
        return ""


def _tail_lines(path: str, n: int = 200):
    try:
        if not path or not os.path.exists(path):
            return []
        n = max(20, min(2000, int(n)))
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        return lines[-n:]
    except Exception:
        return []


# ============================================================
# 2) 서버 DB(감사/채팅/러닝/임포트)
# ============================================================
def db_server_conn():
    conn = sqlite3.connect(SERVER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_server_db():
    conn = db_server_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        user_id TEXT,
        is_admin INTEGER,
        ip TEXT,
        user_agent TEXT,
        event_type TEXT,
        event_name TEXT,
        path TEXT,
        method TEXT,
        status_code INTEGER,
        payload_json TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        user_id TEXT,
        message TEXT,
        response TEXT,
        emotion TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_jobs (
        id TEXT PRIMARY KEY,
        ts_created TEXT,
        ts_started TEXT,
        ts_finished TEXT,
        created_by TEXT,
        job_type TEXT,
        payload_json TEXT,
        status TEXT,
        log_path TEXT,
        result_json TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS imported_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        source TEXT,
        conversation_id TEXT,
        conversation_url TEXT,
        role TEXT,
        content TEXT,
        content_hash TEXT,
        raw_json TEXT
    )
    """)

    conn.commit()
    conn.close()


def audit(event_type: str, event_name: str, status_code: int = 200, payload=None):
    if not has_request_context():
        return
    path = request.path or ""
    if path.startswith("/image/") or path == "/health":
        return

    try:
        conn = db_server_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_log
            (ts, user_id, is_admin, ip, user_agent, event_type, event_name, path, method, status_code, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_iso(),
            get_user_id(),
            1 if is_admin() else 0,
            get_client_ip(),
            (request.headers.get("User-Agent") or "")[:300],
            event_type,
            event_name,
            path,
            request.method,
            int(status_code),
            safe_json(payload or {})
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass


# ============================================================
# 3) RealSimTrading (최소 운영)
# ============================================================
class RealSimTrading:
    def __init__(self, initial_krw=1_000_000, fee_rate=0.0005):
        self.initial_krw = float(initial_krw)
        self.fee_rate = float(fee_rate)
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(SIM_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._conn()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS sim_account (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            krw_balance REAL,
            updated_at TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sim_positions (
            coin TEXT PRIMARY KEY,
            amount REAL,
            avg_price REAL,
            updated_at TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sim_trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            coin TEXT,
            side TEXT,
            price REAL,
            amount REAL,
            trade_value REAL,
            fee REAL,
            strategy TEXT,
            reason TEXT,
            krw_balance_after REAL,
            realized_pnl REAL
        )
        """)

        row = cur.execute("SELECT krw_balance FROM sim_account WHERE id=1").fetchone()
        if row is None:
            cur.execute(
                "INSERT INTO sim_account (id, krw_balance, updated_at) VALUES (1, ?, ?)",
                (self.initial_krw, now_iso())
            )

        conn.commit()
        conn.close()

    def _get_balance(self) -> float:
        conn = self._conn()
        cur = conn.cursor()
        bal = float(cur.execute("SELECT krw_balance FROM sim_account WHERE id=1").fetchone()[0])
        conn.close()
        return bal

    def _set_balance(self, new_balance: float):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("UPDATE sim_account SET krw_balance=?, updated_at=? WHERE id=1",
                    (float(new_balance), now_iso()))
        conn.commit()
        conn.close()

    def _get_position(self, coin: str):
        conn = self._conn()
        cur = conn.cursor()
        row = cur.execute("SELECT coin, amount, avg_price FROM sim_positions WHERE coin=?", (coin,)).fetchone()
        conn.close()
        if not row:
            return {"coin": coin, "amount": 0.0, "avg_price": 0.0}
        return {"coin": row[0], "amount": float(row[1]), "avg_price": float(row[2])}

    def _upsert_position(self, coin: str, amount: float, avg_price: float):
        conn = self._conn()
        cur = conn.cursor()
        if amount <= 0:
            cur.execute("DELETE FROM sim_positions WHERE coin=?", (coin,))
        else:
            cur.execute("""
                INSERT INTO sim_positions (coin, amount, avg_price, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(coin) DO UPDATE SET
                    amount=excluded.amount,
                    avg_price=excluded.avg_price,
                    updated_at=excluded.updated_at
            """, (coin, float(amount), float(avg_price), now_iso()))
        conn.commit()
        conn.close()

    def get_snapshot(self):
        conn = self._conn()
        cur = conn.cursor()
        bal = float(cur.execute("SELECT krw_balance FROM sim_account WHERE id=1").fetchone()[0])
        positions = [dict(r) for r in cur.execute("SELECT * FROM sim_positions ORDER BY coin ASC").fetchall()]
        conn.close()
        return {"krw_balance": round(bal, 2), "positions": positions}

    def execute_trade(self, coin: str, price, amount, side: str, strategy: str = "", reason: str = ""):
        coin = (coin or "").strip().upper()
        side = (side or "").strip().upper()
        if side not in ("BUY", "SELL"):
            return {"success": False, "error": "side는 BUY/SELL만 허용"}

        try:
            price = float(price)
            amount = float(amount)
        except Exception:
            return {"success": False, "error": "price/amount는 숫자여야 함"}

        if price <= 0 or amount <= 0:
            return {"success": False, "error": "price/amount는 0보다 커야 함"}

        trade_value = price * amount
        fee = trade_value * self.fee_rate

        bal = self._get_balance()
        pos = self._get_position(coin)
        realized_pnl = 0.0

        if side == "BUY":
            total = trade_value + fee
            if bal < total:
                return {"success": False, "error": "잔고 부족"}
            old_amt, old_avg = pos["amount"], pos["avg_price"]
            new_amt = old_amt + amount
            new_avg = ((old_amt * old_avg) + trade_value) / new_amt if new_amt > 0 else 0.0
            bal = bal - total
            self._set_balance(bal)
            self._upsert_position(coin, new_amt, new_avg)
        else:
            if pos["amount"] < amount:
                return {"success": False, "error": "보유 수량 부족"}
            realized_pnl = (price - pos["avg_price"]) * amount - fee
            proceeds = trade_value - fee
            new_amt = pos["amount"] - amount
            bal = bal + proceeds
            self._set_balance(bal)
            self._upsert_position(coin, new_amt, pos["avg_price"])

        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sim_trade_history
            (ts, coin, side, price, amount, trade_value, fee, strategy, reason, krw_balance_after, realized_pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_iso(), coin, side, price, amount, trade_value, fee,
            (strategy or "")[:80], (reason or "")[:400],
            float(bal), float(realized_pnl)
        ))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "coin": coin,
            "side": side,
            "price": price,
            "amount": amount,
            "fee": round(fee, 2),
            "krw_balance": round(bal, 2),
            "realized_pnl": round(realized_pnl, 2),
            "position": self._get_position(coin)
        }

    def history(self, limit=20):
        conn = self._conn()
        cur = conn.cursor()
        rows = [dict(r) for r in cur.execute(
            "SELECT * FROM sim_trade_history ORDER BY id DESC LIMIT ?",
            (int(limit),)
        ).fetchall()]
        conn.close()
        return rows


# ============================================================
# 4) Emotion (간단)
# ============================================================
def get_real_emotion(message: str) -> str:
    msg = (message or "").strip()

    if any(k in msg for k in ["미안", "죄송", "사과"]): return "apologizing"
    if any(k in msg for k in ["피곤", "졸려", "지친", "30시간"]): return "tired"
    if any(k in msg for k in ["무서", "겁", "두려"]): return "scared"
    if any(k in msg for k in ["걱정", "불안", "초조"]): return "worried"
    if any(k in msg for k in ["스트레스", "압박", "과부하"]): return "stressed"
    if any(k in msg for k in ["실망", "기대 이하"]): return "disappointed"
    if any(k in msg for k in ["외로", "혼자"]): return "lonely"

    if any(k in msg for k in ["열받", "빡", "짜증", "병신", "똑바로", "개같", "씨발", "좆"]): return "angry"
    if any(k in msg for k in ["답답", "미치겠", "왜이래", "안돼", "에러"]): return "frustrated"
    if any(k in msg for k in ["거슬", "귀찮", "성가시"]): return "annoyed"

    if any(k in msg for k in ["고마", "감사"]): return "grateful"
    if any(k in msg for k in ["해냈", "성공", "됐다"]): return "proud"
    if any(k in msg for k in ["희망", "될거", "가능"]): return "hopeful"
    if any(k in msg for k in ["화이팅", "할수있", "가자"]): return "encouraging"
    if any(k in msg for k in ["신나", "대박", "나이스", "좋아", "ㅋㅋ", "ㅎㅎ"]): return "cheerful"

    if any(k in msg for k in ["설명", "정리", "요약"]): return "explaining"
    if any(k in msg for k in ["궁금", "왜", "뭐지", "어떻게"]): return "curious"
    if any(k in msg for k in ["집중", "진행", "지금부터"]): return "focused"
    if any(k in msg for k in ["진지", "중요"]): return "serious"
    if any(k in msg for k in ["의심", "진짜?", "맞아?"]): return "skeptical"
    if any(k in msg for k in ["차분", "괜찮", "천천히"]): return "calm"

    return "neutral"


# ============================================================
# 5) Learning Jobs (뼈대)
# ============================================================
def learning_create_job(job_type: str, payload: dict, created_by: str) -> dict:
    job_id = uuid.uuid4().hex
    log_path = os.path.join(LEARNING_LOG_DIR, f"{job_id}.log")

    conn = db_server_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO learning_jobs
        (id, ts_created, ts_started, ts_finished, created_by, job_type, payload_json, status, log_path, result_json)
        VALUES (?, ?, NULL, NULL, ?, ?, ?, ?, ?, NULL)
    """, (job_id, now_iso(), created_by, job_type, safe_json(payload), "created", log_path))
    conn.commit()
    conn.close()

    t = threading.Thread(target=learning_run_job, args=(job_id,), daemon=True)
    t.start()

    return {"job_id": job_id, "status": "created", "log_path": log_path}


def learning_update(job_id: str, **fields):
    conn = db_server_conn()
    cur = conn.cursor()
    keys, vals = [], []
    for k, v in fields.items():
        keys.append(f"{k}=?")
        vals.append(v)
    vals.append(job_id)
    cur.execute(f"UPDATE learning_jobs SET {', '.join(keys)} WHERE id=?", tuple(vals))
    conn.commit()
    conn.close()


def learning_get(job_id: str):
    conn = db_server_conn()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM learning_jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def learning_append_log(path: str, line: str):
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] {line}\n")
    except Exception:
        pass


def learning_run_job(job_id: str):
    job = learning_get(job_id)
    if not job:
        return

    learning_update(job_id, status="running", ts_started=now_iso())
    learning_append_log(job["log_path"], f"JOB START: {job_id}")

    payload = json.loads(job.get("payload_json") or "{}")
    url = payload.get("url", "")

    if YT_LEARNER_CMD:
        try:
            learning_append_log(job["log_path"], f"RUN: {YT_LEARNER_CMD} {url}")
            with open(job["log_path"], "a", encoding="utf-8") as lf:
                p = subprocess.Popen(
                    f'{YT_LEARNER_CMD} "{url}" "{job_id}"',
                    shell=True,
                    stdout=lf,
                    stderr=lf,
                    cwd=BASE_DIR
                )
                code = p.wait()

            if code == 0:
                learning_update(job_id, status="done", ts_finished=now_iso(),
                                result_json=safe_json({"ok": True}))
                learning_append_log(job["log_path"], "JOB DONE (code=0)")
            else:
                learning_update(job_id, status="error", ts_finished=now_iso(),
                                result_json=safe_json({"ok": False, "code": code}))
                learning_append_log(job["log_path"], f"JOB ERROR (code={code})")
        except Exception as e:
            learning_update(job_id, status="error", ts_finished=now_iso(),
                            result_json=safe_json({"ok": False, "error": str(e)}))
            learning_append_log(job["log_path"], f"EXCEPTION: {e}")
    else:
        learning_append_log(job["log_path"], "YT_LEARNER_CMD 없음 → STUB 처리")
        learning_append_log(job["log_path"], f"url={url}")
        time.sleep(1)
        learning_update(job_id, status="stubbed", ts_finished=now_iso(),
                        result_json=safe_json({"ok": True, "stubbed": True}))
        learning_append_log(job["log_path"], "JOB STUBBED DONE")


def learning_stats():
    def fsize(p):
        try:
            return os.path.getsize(p)
        except Exception:
            return 0

    total = 0
    try:
        for fn in os.listdir(LEARNING_LOG_DIR):
            total += fsize(os.path.join(LEARNING_LOG_DIR, fn))
    except Exception:
        pass

    return {
        "server_db_size": fsize(SERVER_DB_PATH),
        "sim_db_size": fsize(SIM_DB_PATH),
        "learning_logs_size": total,
        "timestamp": now_iso()
    }


# ============================================================
# 6) Flask 앱/CORS/자동감사
# ============================================================
app = Flask(__name__)
app.secret_key = SECRET_KEY

CORS(app, resources={r"/*": {"origins": [
    "http://localhost:5001", "http://127.0.0.1:5001",
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:5500", "http://127.0.0.1:5500",
    "https://leemay.thetheunique.com"
]}})

init_server_db()
sim_trading = RealSimTrading()
SERVER_START_TS = time.time()


@app.after_request
def after(resp):
    try:
        p = request.path or ""
        if p.startswith("/image/") or p == "/health":
            return resp
        audit("API_CALL", "API_CALL", status_code=resp.status_code,
              payload={"q": request.query_string.decode("utf-8", "ignore")})
    except Exception:
        pass
    return resp


# ============================================================
# 7) 기본/정적
# ============================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {"EmayBrain": True, "YouTube": True}
    })


@app.route("/")
@app.route("/ops")
def serve_index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/dashboard")
def serve_dashboard():
    return send_from_directory(WEB_DIR, "dashboard.html")


@app.route("/health-ui")
def serve_health_ui():
    return send_from_directory(WEB_DIR, "health.html")


@app.route("/image/<filename>")
def serve_image(filename):
    filename = os.path.basename(filename)
    return send_from_directory(IMAGES_DIR, filename)


# ============================================================
# 8) 인증(세션)
# ============================================================
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or data.get("user") or "guest").strip()
    token = (data.get("admin_token") or "").strip()

    session["user_id"] = user_id
    if user_id == ADMIN_ID and token == ADMIN_TOKEN:
        session["is_admin"] = True
        return jsonify({"success": True, "user_id": user_id, "is_admin": True})

    session["is_admin"] = False
    return jsonify({"success": True, "user_id": user_id, "is_admin": False})


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/auth/whoami", methods=["GET"])
def whoami():
    return jsonify({"user_id": get_user_id(), "is_admin": is_admin(), "admin_id": ADMIN_ID})


# ============================================================
# 9) OPS API + CHAT API (UI 호환)
# ============================================================
def execute_bat_script_async(script_path: str) -> dict:
    try:
        if not os.path.exists(script_path):
            return {"ok": False, "msg": f"Missing: {script_path}"}
        log_ops(f"ASYNC START: {script_path}")
        subprocess.Popen(
            ["cmd.exe", "/c", script_path],
            cwd=BASE_DIR,
            creationflags=0x08000000
        )
        return {"ok": True, "msg": "started", "path": script_path}
    except Exception as e:
        log_ops(f"ASYNC ERROR: {e}")
        return {"ok": False, "msg": str(e)}


@app.route("/api/ops/control/start", methods=["POST"])
def ops_control_start():
    if not is_admin_request():
        return jsonify({"ok": False, "message": "Unauthorized"}), 401
    return jsonify(execute_bat_script_async(ALLOWED_OPS_SCRIPTS["control_start"]))


# --- UI 버튼: API(5001) 재시작 ---
@app.route("/api/ops/api/restart", methods=["POST"])
def ops_api_restart():
    if not is_admin_request():
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    bat_path = os.path.join(OPS_DIR, "04_OPS_RESTART_5001.bat")
    try:
        log_ops(f"RUN: {bat_path} (api restart request)")
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "", "/min", bat_path],
            cwd=BASE_DIR,
            creationflags=0x08000000
        )
        return jsonify({"ok": True, "message": "API restart scheduled (5001)."}), 200
    except Exception as e:
        log_ops(f"ERROR api_restart: {e}")
        return jsonify({"ok": False, "message": str(e)}), 500


# ----------------------------
# CHAT: 규칙 고정 (response/emotion/image_url)
# ----------------------------
def _resolve_emotion_filename(emotion: str) -> str:
    e = (emotion or "neutral").strip()
    fn = f"{e}.png"
    if not os.path.exists(os.path.join(IMAGES_DIR, fn)):
        e = "neutral"
    return e


def _save_chat_row(user_id: str, message: str, response: str, emotion: str):
    try:
        conn = db_server_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_history (ts, user_id, message, response, emotion) VALUES (?, ?, ?, ?, ?)",
            (now_iso(), user_id, message, response, emotion)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or data.get("text") or data.get("prompt") or "").strip()
    if not message:
        return jsonify({"ok": False, "message": "message가 비었습니다."}), 400

    emotion = _resolve_emotion_filename(get_real_emotion(message))
    image_url = f"/image/{emotion}.png"

    # 부팅/테스트용 스텁 응답 (나중에 LLM 연결하면 여기만 교체)
    response = (data.get("force_response") or "").strip()
    if not response:
        response = f"오케이. 감정={emotion}\n\n너의 메시지:\n{message}"

    _save_chat_row(get_user_id(), message, response, emotion)

    return jsonify({
        "ok": True,
        "response": response,
        "emotion": emotion,
        "image_url": image_url
    }), 200


@app.route("/api/chat", methods=["POST"])
def api_chat_alias():
    return chat()


@app.route("/api/chat/history", methods=["GET"])
def api_chat_history():
    limit = int(request.args.get("limit", "20"))
    limit = max(1, min(200, limit))

    conn = db_server_conn()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, ts, user_id, message, response, emotion "
        "FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()

    return jsonify({"ok": True, "history": [dict(r) for r in rows]}), 200


# --- 5000(트레이딩 엔진) 시작 ---
@app.route("/api/ops/bots/start", methods=["POST"])
def ops_bots_start():
    if not is_admin_request():
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    # SAFE 우선
    bat_path = ALLOWED_OPS_SCRIPTS["bots_start_safe"]
    if not os.path.exists(bat_path):
        bat_path = ALLOWED_OPS_SCRIPTS["bots_start"]

    if not os.path.exists(bat_path):
        return jsonify({"ok": False, "message": f"Missing bat: {bat_path}"}), 500

    if check_port_socket(5000):
        return jsonify({
            "ok": True,
            "message": "Already running",
            "port_active": True,
            "ai_log": latest_ai_trading_log()
        })

    log_path = os.path.join(LOG_DIR, "bots_start_last.log")
    try:
        log_ops(f"RUN: {bat_path}")
        with open(log_path, "ab") as f:
            p = subprocess.Popen(
                ["cmd.exe", "/c", bat_path],
                cwd=BASE_DIR,
                stdout=f,
                stderr=f,
                creationflags=0x08000000
            )

        for i in range(60):
            if check_port_socket(5000):
                return jsonify({
                    "ok": True,
                    "port_active": True,
                    "attempts": i + 1,
                    "pid": p.pid,
                    "ops_log": log_path,
                    "ai_log": latest_ai_trading_log()
                })
            time.sleep(0.5)

        return jsonify({
            "ok": False,
            "port_active": False,
            "message": "Timeout",
            "pid": p.pid,
            "ops_log": log_path,
            "ai_log": latest_ai_trading_log()
        })
    except Exception as e:
        log_ops(f"ERROR bots_start: {e}")
        log_ops(traceback.format_exc())
        return jsonify({"ok": False, "message": str(e)}), 500


@app.route("/api/ops/bots/stop", methods=["POST"])
def ops_bots_stop():
    if not is_admin_request():
        return jsonify({"ok": False, "message": "Unauthorized"}), 401
    return jsonify(execute_bat_script_async(ALLOWED_OPS_SCRIPTS["bots_stop"]))


@app.route("/api/ops/status", methods=["GET"])
def ops_status():
    try:
        conn = db_server_conn()
        cur = conn.cursor()
        count = int(cur.execute("SELECT count(*) FROM imported_messages").fetchone()[0])
        conn.close()
        intel_p = min(100, round((count / 10000) * 100, 2))
    except Exception:
        count, intel_p = 0, 0

    return jsonify({
        "timestamp": now_iso(),
        "memory_count": count,
        "intelligence_percent": intel_p,
        "ports": {
            "5001": True,
            "5000": check_port_socket(5000),
            "11434": check_port_socket(11434)
        },
        "uptime": int(time.time() - SERVER_START_TS),
        "ai_log": latest_ai_trading_log(),
        "ops_log": os.path.join(LOG_DIR, "bots_start_last.log"),
    })


@app.route("/api/ops/log/tail", methods=["GET", "POST"])
def ops_log_tail():
    try:
        if not is_admin_request():
            return jsonify({"ok": False, "message": "Unauthorized"}), 401

        if request.method == "POST":
            body = request.get_json(silent=True) or {}
            name = (body.get("name") or "").strip() or (request.args.get("name") or "").strip()
            lines = body.get("lines") or request.args.get("lines") or "200"
        else:
            name = (request.args.get("name") or "").strip()
            lines = request.args.get("lines") or "200"

        name_norm = name.replace(" ", "").lower().replace(".log", "")

        if name_norm in ("ops_api", "opsapilog"):
            path = OPS_LOG_FILE
        elif name_norm in ("bots_start_last", "bots_start_lastlog", "bots_start"):
            path = os.path.join(LOG_DIR, "bots_start_last.log")
        elif name_norm in ("ai_trading", "ai_latest", "aitrading"):
            path = latest_ai_trading_log()
        else:
            return jsonify({"ok": False, "message": "Invalid log name", "got": name}), 400

        return jsonify({"ok": True, "name": name, "path": path, "lines": _tail_lines(path, int(lines))})

    except Exception as e:
        log_ops("ERROR ops_log_tail: " + repr(e))
        log_ops(traceback.format_exc())
        return jsonify({"ok": False, "message": "Internal error", "error": str(e)}), 500


# ============================================================
# 10) Import API
# ============================================================
@app.route("/api/conversations/import", methods=["POST", "OPTIONS"])
def conversations_import():
    if request.method == "OPTIONS":
        return ("", 204)

    if not is_admin_request():
        return jsonify({"ok": False, "message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    content_hash = (data.get("content_hash") or "").strip()

    conn = db_server_conn()
    cur = conn.cursor()

    if content_hash:
        row = cur.execute("SELECT id FROM imported_messages WHERE content_hash=? LIMIT 1", (content_hash,)).fetchone()
        if row:
            conn.close()
            return jsonify({"ok": True, "deduped": True, "id": int(row[0])})

    cur.execute("""
        INSERT INTO imported_messages
        (ts, source, conversation_id, conversation_url, role, content, content_hash, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_iso(),
        (data.get("source") or "unknown"),
        (data.get("conversation_id") or ""),
        (data.get("conversation_url") or ""),
        (data.get("role") or ""),
        (data.get("content") or ""),
        content_hash,
        json.dumps(data, ensure_ascii=False)
    ))
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"ok": True, "id": int(new_id)})


# ============================================================
# 11) 시스템 상태
# ============================================================
@app.route("/api/system/status", methods=["GET"])
def system_status():
    disk = psutil.disk_usage(BASE_DIR)
    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.1),
        "memory": psutil.virtual_memory().percent,
        "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        "uptime_sec": int(time.time() - SERVER_START_TS),
        "timestamp": now_iso()
    })


# ============================================================
# 12) 지능-실행 직축 및 대량 로딩 API
# ============================================================
@app.route("/api/ops/strategy/apply", methods=["POST"])
def ops_strategy_apply():
    if not is_admin_request():
        return jsonify({"ok": False, "msg": "DENY"}), 403

    data = request.get_json(silent=True) or {}
    ratio = data.get("ratio", 70)

    path = os.path.join(BASE_DIR, "strategies", "current_strategy.json")
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump({"intel_ratio": int(ratio), "updated_at": now_iso(), "commander": "Yusong"}, f, indent=4, ensure_ascii=False)

    return jsonify({"ok": True, "message": "전략이 봇의 뇌에 이식되었습니다."})


@app.route("/api/ops/memory/bulk-load", methods=["POST"])
def ops_memory_bulk_load():
    if not is_admin_request():
        return jsonify({"ok": False, "msg": "DENY"}), 403

    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    if not url:
        return jsonify({"ok": False, "msg": "URL 누락"}), 400

    res = learning_create_job("bulk_youtube", {"url": url}, "Yusong")
    return jsonify({"ok": True, "message": "대량 지식 학습이 예약되었습니다.", "job_id": res["job_id"]})


# ============================================================
# 13) 시뮬 트레이딩 조회 API
# ============================================================
@app.route("/api/sim/status", methods=["GET"])
def api_sim_status():
    return jsonify(sim_trading.get_snapshot())


@app.route("/api/sim/history", methods=["GET"])
def api_sim_history():
    limit = request.args.get("limit", 20)
    return jsonify(sim_trading.history(limit))


@app.route("/api/sim/trade", methods=["POST"])
def api_sim_trade():
    if not is_admin_request():
        return jsonify({"ok": False, "msg": "DENY"}), 403

    data = request.get_json(silent=True) or {}
    res = sim_trading.execute_trade(
        coin=data.get("coin"),
        price=data.get("price"),
        amount=data.get("amount"),
        side=data.get("side"),
        strategy=data.get("strategy"),
        reason=data.get("reason")
    )
    return jsonify(res)


# ============================================================
# 14) 러닝 잡(YouTube) 상태 관리
# ============================================================
@app.route("/api/learning/jobs", methods=["GET"])
def api_learning_jobs():
    conn = db_server_conn()
    cur = conn.cursor()
    rows = [dict(r) for r in cur.execute("SELECT * FROM learning_jobs ORDER BY ts_created DESC LIMIT 50").fetchall()]
    conn.close()
    return jsonify(rows)


@app.route("/api/learning/stats", methods=["GET"])
def api_learning_stats_api():
    return jsonify(learning_stats())


# ============================================================
# 15) 시스템 상세 메트릭 (psutil 기반)
# ============================================================
@app.route("/api/system/metrics", methods=["GET"])
def api_system_metrics():
    return jsonify({
        "cpu_count": psutil.cpu_count(),
        "cpu_load": psutil.cpu_percent(interval=0.1),
        "mem_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "mem_used_percent": psutil.virtual_memory().percent,
        "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
        "net_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
    })


# ============================================================
# 16) 엔트리포인트
# ============================================================
if __name__ == "__main__":
    print("🚀 Lee May v3.3.1 통합 관제 서버 가동 (Port 5001)")
    print(f"📁 BASE_DIR: {BASE_DIR}")
    print(f"🧾 OPS_LOG:  {OPS_LOG_FILE}")
    app.run(host="0.0.0.0", port=5001, debug=False)