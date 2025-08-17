from __future__ import annotations

import sys

# -*- coding: utf-8 -*-
from pathlib import Path

BASE = Path(__file__).resolve().parent
for p in (BASE, BASE.parent):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

try:
    from patches.handle_safe_patch import handle as patched_handle

    import action_handler as ah

    ah.handle = patched_handle
except Exception:
    pass
