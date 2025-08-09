#!/usr/bin/env python3
# 檔案位置：modules/quotation.py
# 模組用途：相容層，轉發至實作

try:
    from quotation import choose_package, generate_pdf_quote
except Exception:  # pragma: no cover
    from src.quotation import choose_package, generate_pdf_quote
