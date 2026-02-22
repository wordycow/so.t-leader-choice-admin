# -*- coding: utf-8 -*-
"""
LeeMay Memory (canonical)
- MongoDB Atlas(옵션): MONGO_URI 설정 시 사용
- 연결 실패/미설정이어도 서버는 죽지 않음
"""

from __future__ import annotations

import os
from datetime import datetime


def _env(name: str, default: str = "") -> str:
    v = os.environ.get(name, "").strip()
    return v if v else default


MONGO_URI = _env("MONGO_URI", "")
MONGO_DB = _env("MONGO_DB", "leemay")


class Memory:
    def __init__(self) -> None:
        self.enabled = False
        self.client = None
        self.db = None

        if not MONGO_URI:
            return

        try:
            from pymongo import MongoClient  # type: ignore

            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2500)
            self.client.admin.command("ping")
            self.db = self.client[MONGO_DB]
            self.enabled = True
        except Exception:
            self.enabled = False
            self.client = None
            self.db = None

    def save_chat(self, role: str, content: str, meta: dict | None = None) -> bool:
        if not self.enabled or not self.db:
            return False
        try:
            self.db.chat.insert_one(
                {
                    "ts": datetime.utcnow().isoformat(),
                    "role": role,
                    "content": content,
                    "meta": meta or {},
                }
            )
            return True
        except Exception:
            return False