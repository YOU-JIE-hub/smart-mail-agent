#!/usr/bin/env python3
# 檔案位置：modules/sales_notifier.py
# 模組用途：相容層，轉發至實作

try:
    from sales_notifier import notify_sales
except Exception:  # pragma: no cover
    from src.sales_notifier import notify_sales
