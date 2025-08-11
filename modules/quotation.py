#!/usr/bin/env python3
# 檔案位置：modules/quotation.py
# 模組用途：報價方案選擇與報價單輸出（PDF 若不可用則退回純文字）
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

PRICE_TABLE = {
    "Basic": 2000,
    "Standard": 5000,
    "Pro": 12000,
}


def choose_package(text: str) -> Dict[str, Any]:
    """
    依需求文字挑選方案：
      - 含「進階」「pro」=> Pro
      - 含「標準」「standard」=> Standard
      - 其他 => Basic
    回傳:
      dict: { name, price }
    """
    t = (text or "").lower()
    if ("進階" in t) or ("pro" in t):
        name = "Pro"
    elif ("標準" in t) or ("standard" in t):
        name = "Standard"
    else:
        name = "Basic"
    return {"name": name, "price": PRICE_TABLE[name]}


def _try_make_pdf(out_path: Path, title: str, lines: List[str]) -> bool:
    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.pdfbase import pdfmetrics  # type: ignore
        from reportlab.pdfbase.ttfonts import TTFont  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore

        font_path = os.getenv("FONT_TTF_PATH", "NotoSansTC-Regular.ttf")
        use_cjk = Path(font_path).exists()
        if use_cjk:
            pdfmetrics.registerFont(TTFont("CJK", font_path))

        c = canvas.Canvas(str(out_path), pagesize=A4)
        width, height = A4
        y = height - 72
        c.setFont("CJK" if use_cjk else "Helvetica", 14)
        c.drawString(72, y, title)
        y -= 28
        c.setFont("CJK" if use_cjk else "Helvetica", 11)
        for p in lines:
            for ln in p.split("\n"):
                c.drawString(72, y, ln)
                y -= 18
                if y < 72:
                    c.showPage()
                    y = height - 72
                    c.setFont("CJK" if use_cjk else "Helvetica", 11)
        c.showPage()
        c.save()
        return True
    except Exception:
        return False


def generate_pdf_quote(output_dir: str, customer: str, items: List[Dict[str, Any]]) -> str:
    """
    產生報價單。若無 reportlab 或字型，退回 .txt，但仍保證有檔案。
    參數:
        output_dir: 輸出目錄
        customer: 客戶名稱
        items: [{name, qty, unit_price}]
    回傳:
        檔案路徑（pdf 或 txt）
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf = Path(output_dir) / f"quotation_{ts}.pdf"
    txt = Path(output_dir) / f"quotation_{ts}.txt"

    lines = []
    total = 0.0
    for it in items:
        name = str(it.get("name", "項目"))
        qty = int(it.get("qty", 1))
        unit = float(it.get("unit_price", 0.0))
        amt = qty * unit
        total += amt
        lines.append(f"{name}: {qty} x {unit} = {amt}")
    lines.append(f"總計：{total}")

    if _try_make_pdf(pdf, f"報價單 - {customer}", lines):
        return str(pdf)
    txt.write_text("報價單 - " + customer + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return str(txt)


__all__ = ["choose_package", "generate_pdf_quote"]
