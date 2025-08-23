from __future__ import annotations
from typing import Any
try:
    from smart_mail_agent.utils.log_writer import write_log as _w, log_to_db as _db  # type: ignore
except Exception:
    def _w(event: str, **fields: Any) -> None: pass
    def _db(*_a: Any, **_k: Any) -> None: pass
write_log = _w
log_to_db = _db
__all__ = ["write_log","log_to_db"]
