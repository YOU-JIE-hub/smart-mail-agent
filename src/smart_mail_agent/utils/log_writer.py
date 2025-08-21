from __future__ import annotations

try:
    # 正式實作（若有）
    from smart_mail_agent.observability.log_writer import write_log as _write_log  # type: ignore
except Exception:
    def _write_log(*args, **kwargs):  # 安全退路：不做事、不報錯
        return None

def write_log(*args, **kwargs):
    """Thin-compat wrapper expected by legacy imports/tests."""
    return _write_log(*args, **kwargs)

__all__ = ["write_log"]
