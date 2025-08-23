from __future__ import annotations
import logging, os, sys
__all__ = ["get_logger"]

_LEVELS = {
    "CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, "WARNING": logging.WARNING,
    "INFO": logging.INFO, "DEBUG": logging.DEBUG, "NOTSET": logging.NOTSET,
}

def _level_from_env() -> int:
    lv = os.getenv("SMA_LOG_LEVEL","INFO").upper()
    return _LEVELS.get(lv, logging.INFO)

_configured = False
def _configure_root() -> logging.Logger:
    global _configured
    root = logging.getLogger("smart_mail_agent")
    if not _configured:
        root.setLevel(_level_from_env())
        if not root.handlers:
            h = logging.StreamHandler(sys.stderr)
            h.setFormatter(logging.Formatter("[%(levelname)s] %(name)s:%(filename)s:%(lineno)d %(message)s"))
            root.addHandler(h)
        _configured = True
    return root

def get_logger(name: str | None = None) -> logging.Logger:
    root = _configure_root()
    return root if not name else logging.getLogger(name)

# 保留舊用法：from smart_mail_agent.utils.logger import logger
logger = get_logger("smart_mail_agent")
