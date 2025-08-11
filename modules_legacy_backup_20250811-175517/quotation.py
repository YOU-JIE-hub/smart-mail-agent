#!/usr/bin/env python3
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

PKG_BASIC = "基礎"
PKG_PRO = "專業"
PKG_ENT = "企業"

KW_ENT = ("整合", "API", "ERP", "LINE", "企業")
KW_PRO = ("自動化", "排程", "自動分類", "專業")

DEFAULT_FONT_PATH = os.getenv("FONT_TTF_PATH", "assets/fonts/NotoSansTC-Regular.ttf")
DEFAULT_OUT_DIR = Path("data/output")


def choose_package(subject: str, content: str) -> Dict[str, str]:
    """
    測試期待回傳 dict，至少含 'package' 鍵。
    """
    text = f"{subject or ''} {content or ''}".lower()
    if any(k.lower() in text for k in KW_ENT):
        pkg = PKG_ENT
    elif any(k.lower() in text for k in KW_PRO):
        pkg = PKG_PRO
    else:
        pkg = PKG_BASIC
    return {"package": pkg}


def _render_pdf(path: Path, title: str, lines: List[str]) -> str:
    """
    優先用 reportlab；找不到中文字型或任何字型錯誤時退回 Helvetica，不丟錯。
    若 reportlab 模組不存在，外層會轉存 .txt。
    """
    from reportlab.lib.pagesizes import A4  # type: ignore
    from reportlab.pdfgen import canvas  # type: ignore

    font_name = "Helvetica"
    try:
        from reportlab.pdfbase import pdfmetrics  # type: ignore
        from reportlab.pdfbase.ttfonts import TTFont  # type: ignore

        if Path(DEFAULT_FONT_PATH).exists():
            pdfmetrics.registerFont(TTFont("CJK", DEFAULT_FONT_PATH))
            font_name = "CJK"
    except Exception:
        pass  # 任何字型處理問題都回退 Helvetica

    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    y = h - 72

    c.setFont(font_name, 16)
    c.drawString(72, y, title)
    y -= 24

    c.setFont(font_name, 12)
    for line in lines:
        c.drawString(72, y, line)
        y -= 18
        if y < 72:
            c.showPage()
            c.setFont(font_name, 12)
            y = h - 72

    c.save()
    return str(path)


def generate_pdf_quote(
    out_dir: Optional[os.PathLike | str] = None,
    *,
    package: Optional[str] = None,
    client_name: Optional[str] = None,
) -> str:
    """
    相容兩種用法：
      - generate_pdf_quote(tmp_path)                                -> out_dir=tmp_path
      - generate_pdf_quote(package="基礎", client_name="a@b.com")   -> out_dir=data/output
    缺中文字型不丟錯；reportlab 不在時輸出 .txt 作為保底。
    """
    out_base = Path(out_dir) if out_dir is not None else DEFAULT_OUT_DIR
    out_base.mkdir(parents=True, exist_ok=True)

    pkg = package or PKG_BASIC
    client = client_name or "client@example.com"

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    pdf_path = out_base / f"quote-{pkg}-{ts}.pdf"

    title = f"Smart Mail Agent 報價 - {pkg}"
    lines = [
        f"客戶：{client}",
        f"方案：{pkg}",
        f"日期：{ts}",
        "",
        "內容：此為測試用離線報價單（自動化產出）。",
    ]

    try:
        return _render_pdf(pdf_path, title, lines)
    except Exception:
        txt_path = pdf_path.with_suffix(".txt")
        txt_path.write_text(title + "\n" + "\n".join(lines), encoding="utf-8")
        return str(txt_path)


__all__ = ["choose_package", "generate_pdf_quote", "PKG_BASIC", "PKG_PRO", "PKG_ENT"]
