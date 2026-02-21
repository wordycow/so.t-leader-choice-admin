# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from datetime import datetime
import sys

# Windows 콘솔 인코딩 이슈 방지(가능한 경우)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

app = Flask(__name__)
CORS(app)

START = time.time()

def now():
    return datetime.now().isoformat(timespec="seconds")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "AI_TRADING_5000_STUB",
        "timestamp": now(),
        "uptime": int(time.time() - START)
    })

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"ok": True, "mode": "stub", "timestamp": now()})

@app.route("/api/trade", methods=["POST"])
def trade():
    data = request.get_json(silent=True) or {}
    return jsonify({
        "ok": False,
        "mode": "stub",
        "received": data,
        "message": "5000은 현재 스텁입니다. 실전 엔진 부팅 후 교체됩니다."
    })

if __name__ == "__main__":
    print("AI TRADING 5000 STUB SERVER (Port 5000)")
    app.run(host="0.0.0.0", port=5000, debug=False)