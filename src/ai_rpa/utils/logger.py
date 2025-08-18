#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/utils/logger.py
# 模組用途: 統一日誌設定，供各模組引用
from __future__ import annotations
import logging
from logging import Logger

def get_logger(name: str) -> Logger:
    """
    取得模組專用 logger，統一格式與等級。

    參數:
        name: 模組名稱（例如 "OCR", "SCRAPER"）
    回傳:
        logging.Logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
