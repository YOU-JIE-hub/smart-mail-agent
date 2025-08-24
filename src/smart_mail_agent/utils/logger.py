from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGER: logging.Logger | None = None


def _mk_handler() -> logging.Handler:
    log_dir = os.environ.get("SMA_LOG_DIR", str(Path.cwd() / "logs"))
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(log_dir) / "ai_rpa.log"
    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fmt = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(fmt)
    return handler


def get_logger(name: str | None = None) -> logging.Logger:
    global _LOGGER
    if _LOGGER is None:
        _LOGGER = logging.getLogger("ai_rpa")
        _LOGGER.setLevel(os.environ.get("SMA_LOG_LEVEL", "INFO").upper())
        if not _LOGGER.handlers:
            _LOGGER.addHandler(_mk_handler())
            sh = logging.StreamHandler(stream=sys.stderr)
            sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            _LOGGER.addHandler(sh)
        _LOGGER.propagate = False
    return _LOGGER if name is None else _LOGGER.getChild(name)


logger = get_logger()
