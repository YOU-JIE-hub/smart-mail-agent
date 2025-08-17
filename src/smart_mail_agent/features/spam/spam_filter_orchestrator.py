from __future__ import annotations

# Auto-generated compat proxy: src/spam/spam_filter_orchestrator.py
from importlib import import_module as _imp

_mod = _imp("smart_mail_agent.spam.spam_filter_orchestrator")
# re-export public names
for _k in dir(_mod):
    if not _k.startswith("_"):
        globals()[_k] = getattr(_mod, _k)
