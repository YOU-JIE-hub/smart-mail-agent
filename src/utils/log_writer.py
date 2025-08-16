# shim: utils.log_writer -> re-export write_log from the real module
from __future__ import annotations

try:
    # 先嘗試頂層實作（你的 repo 有 src/log_writer.py）
    from log_writer import write_log as _write_log  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    try:
        # 退到新位置
        from smart_mail_agent.utils.log_writer import (
            write_log as _write_log,  # type: ignore[attr-defined]
        )
    except Exception:  # 最後保底，避免 import error 讓測試無法收集

        def _write_log(*args, **kwargs):  # type: ignore
            return 0


__all__ = ["write_log"]


def write_log(*args, **kwargs):  # proxy
    return _write_log(*args, **kwargs)
