from __future__ import annotations

import importlib as _im

# Forward to top-level smart_mail_agent.utils.pdf_safe (include privates).
_mod = _im.import_module("smart_mail_agent.utils.pdf_safe")
for _n in dir(_mod):
    globals()[_n] = getattr(_mod, _n)
__all__ = [n for n in dir(_mod) if not n.startswith("__")]
del _mod, _im
