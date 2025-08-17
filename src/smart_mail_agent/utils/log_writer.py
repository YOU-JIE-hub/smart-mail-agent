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

        logging.getLogger("sma").info(
            "[compat.write_log] %s %s", event, json.dumps(fields, ensure_ascii=False)
        )


# 可選：有些舊測試會找 log_to_db；若沒有就提供 no-op
try:  # pragma: no cover
    from smart_mail_agent.observability.log_writer import (
        log_to_db as _log_to_db,  # type: ignore[attr-defined]
    )
except Exception:  # pragma: no cover

    def _log_to_db(*_a: Any, **_k: Any) -> None:
        return None


write_log = _write_log
log_to_db = _log_to_db  # type: ignore[name-defined]
__all__ = ["write_log", "log_to_db"]
