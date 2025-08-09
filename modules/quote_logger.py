#!/usr/bin/env python3
# 檔案位置：modules/quote_logger.py
# 模組用途：相容層，轉發至實作

try:
    from quote_logger import ensure_db_exists, log_quote
except Exception:  # pragma: no cover
    from src.quote_logger import ensure_db_exists, log_quote
