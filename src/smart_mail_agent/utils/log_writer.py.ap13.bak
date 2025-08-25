from __future__ import annotations

from typing import Any

# 盡量轉接到觀測模組；若該模組不存在，提供安全降級實作
try:
    # 正式實作（若存在）
    from smart_mail_agent.observability.log_writer import (
        write_log as _write_log,  # type: ignore[attr-defined]
    )
except Exception:  # pragma: no cover

    def _write_log(event: str, **fields: Any) -> None:  # 最小可用 stub
        import json
        import logging

        logging.getLogger("SMA").info("[event=%s] %s", event, json.dumps(fields, ensure_ascii=False))


try:
    from smart_mail_agent.observability.log_writer import (
        log_to_db as _log_to_db,  # type: ignore[attr-defined]
    )
except Exception:  # pragma: no cover

    def _log_to_db(*_a: Any, **_k: Any) -> None:
        # 安全降級：什麼都不做（保持 API 存在以通過舊測試 import）
        return None


write_log = _write_log
log_to_db = _log_to_db  # type: ignore[name-defined]
__all__ = ["write_log", "log_to_db"]
