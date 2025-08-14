import logging
import os
import sys

_LOG_LEVEL = os.getenv("SMA_LOG_LEVEL", "INFO").upper()
_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter(_FMT))
logger = logging.getLogger("sma")
if not logger.handlers:
    logger.addHandler(_handler)
logger.setLevel(_LOG_LEVEL)


def get_logger(name: str = "sma") -> logging.Logger:
    lg = logging.getLogger(name)
    if not lg.handlers:
        lg.addHandler(_handler)
        lg.setLevel(_LOG_LEVEL)
    return lg
