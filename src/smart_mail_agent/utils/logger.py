from __future__ import annotations

import logging
import os

# 最小安全配置；若上層已有 handlers 就不動
def _ensure_basic_config(level: str | int | None = None) -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=level or os.getenv("SMA_LOG_LEVEL", "INFO"))

def get_logger(name: str = "SMA", level: str | int | None = None) -> logging.Logger:
    """
    專案統一取 logger 的入口。保留簡單行為以避免外部相依。
    """
    _ensure_basic_config(level)
    return logging.getLogger(name)

# 兼容舊用法：from smart_mail_agent.utils.logger import logger
logger: logging.Logger = get_logger("SMA")

__all__ = ["get_logger", "logger"]
