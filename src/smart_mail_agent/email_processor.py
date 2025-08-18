from __future__ import annotations

import importlib as _im

# Forward smart_mail_agent.email_processor to the real module, without star-import.
_mod = _im.import_module("smart_mail_agent.ingestion.email_processor")
for _name in dir(_mod):
    globals()[_name] = getattr(_mod, _name)
__all__ = [n for n in dir(_mod) if not n.startswith("__")]
del _mod, _im
