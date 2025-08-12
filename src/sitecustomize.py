# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
for p in (BASE, BASE.parent):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

try:
    import action_handler as ah
    from patches.handle_safe_patch import handle as patched_handle

    ah.handle = patched_handle
except Exception:
    pass
