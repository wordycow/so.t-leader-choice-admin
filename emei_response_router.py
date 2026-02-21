# -*- coding: utf-8 -*-
"""Fallback module: emei_response_router
- Missing in this repo build.
- Provides safe defaults so the bot can boot.
"""

class EmeiRouter:
    def __init__(self, *args, **kwargs):
        self.mode = "stub"

    def route(self, *args, **kwargs):
        # Return a harmless default
        return {"ok": True, "mode": self.mode, "note": "stub router"}

    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None
        return _noop
