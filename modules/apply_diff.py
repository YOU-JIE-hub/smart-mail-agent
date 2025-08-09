#!/usr/bin/env python3
# 檔案位置：modules/apply_diff.py
# 模組用途：相容層，轉發至實作

try:
    from apply_diff import update_user_info
except Exception:  # pragma: no cover
    from src.apply_diff import update_user_info
