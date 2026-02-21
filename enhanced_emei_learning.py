# -*- coding: utf-8 -*-
"""Fallback module: enhanced_emei_learning
- Missing in this repo build.
- Stub to prevent import crash.
"""

import time

class _DummyEnhancedEMEI:
    def __init__(self):
        self.created_at = time.time()
    def __getattr__(self, name):
        def _noop(*args, **kwargs):
            return None
        return _noop

_dummy_singleton = _DummyEnhancedEMEI()

def get_enhanced_emei(*args, **kwargs):
    return _dummy_singleton
