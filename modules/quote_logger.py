from __future__ import annotations
try:
    from smart_mail_agent.features.quote_logger import *  # type: ignore
except Exception:
    def ensure_db_exists(*_, **__):  # pragma: no cover
        return True
    def log_quote(*_, **__):  # pragma: no cover
        return {"ok": True}
