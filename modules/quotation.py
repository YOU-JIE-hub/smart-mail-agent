#!/usr/bin/env python3
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union

PKG_BASIC = "基礎"
PKG_PRO = "專業"
PKG_ENT = "企業"
KW_ENT = ("整合", "API", "ERP", "LINE", "企業")
KW_PRO = ("自動化", "排程", "自動分類", "專業")


def choose_package(subject: str, content: str) -> str:
    text = f"{subject or ''} {content or ''}".lower()
    if any(k.lower() in text for k in KW_ENT):
        return PKG_ENT
    if any(k.lower() in text for k in KW_PRO):
        return PKG_PRO
    return PKG_BASIC


def _try_pdf(path: Path, title: str, lines: List[str]) -> bool:
    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.pdfbase import pdfmetrics  # type: ignore
        from reportlab.pdfbase.ttfonts import TTFont  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore

        font_path = os.getenv("FONT_TTF_PATH", "NotoSansTC-Regular.ttf")
        use_cjk = Path(font_path).exists()
        if use_cjk:
            pdfmetrics.registerFont(TTFont("CJK", font_path))
        c = canvas.Canvas(str(path), pagesize=A4)
        w, h = A4
        y = h - 72
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
                    y = h - 72
                    c.setFont("CJK" if use_cjk else "Helvetica", 11)
        c.showPage()
        c.save()
        return True
    except Exception:
        return False


def generate_pdf_quote(*args, **kwargs) -> str:
    """
    同時支援兩種測試用法：
      A) generate_pdf_quote(tmp_path)                -> 只指定輸出目錄
      B) generate_pdf_quote(package="基礎", client_name="client@example.com", output_dir="data/output")
    皆回傳實際產生的檔案路徑（pdf 或 txt）。
    """
    # 解析參數
    if len(args) == 1 and not kwargs:
        # A) 單一位置參數 = output_dir
        output_dir = str(args[0])
        package = PKG_BASIC
        client_name = "client@example.com"
    else:
        package = kwargs.get("package", PKG_BASIC)
        client_name = kwargs.get("client_name", "client@example.com")
        output_dir = kwargs.get("output_dir", "data/output")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf = Path(output_dir) / f"quotation_{ts}.pdf"
    txt = Path(output_dir) / f"quotation_{ts}.txt"

    lines = [f"客戶：{client_name}", f"方案：{package}", "項目：依方案提供", "金額：依方案報價"]
    if _try_pdf(pdf, f"報價單 - {client_name}", lines):
        return str(pdf)
    txt.write_text("報價單 - " + client_name + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    return str(txt)


__all__ = ["choose_package", "generate_pdf_quote"]
