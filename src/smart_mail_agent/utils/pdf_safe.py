from __future__ import annotations

from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def _escape_pdf_text(text: str) -> str:
    # 保留可列印字元與常用空白控制字元，避免 ReportLab 例外
    if text is None:
        return ""
    allowed = set("\n\t\r ")
    return "".join(ch for ch in str(text) if ch.isprintable() or ch in allowed)


def ensure_font(font_path: Optional[str]) -> str:
    # 外部可傳入字型；否則用專案 assets 預設路徑
    fp = font_path or "assets/fonts/NotoSansTC-Regular.ttf"
    try:
        pdfmetrics.registerFont(TTFont("NotoSansTC", fp))
        return "NotoSansTC"
    except Exception:
        # 若註冊失敗，退回內建字型（英數正常，中文將可能方塊）
        return "Helvetica"


def write_text_pdf(text: str, output_path: str | Path, font_path: Optional[str] = None) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out), pagesize=A4)
    font_name = ensure_font(font_path)
    c.setFont(font_name, 12)
    width, height = A4
    x, y = 40, height - 40
    for line in _escape_pdf_text(text).splitlines() or ["(empty)"]:
        c.drawString(x, y, line[:180])
        y -= 18
        if y < 40:
            c.showPage()
            c.setFont(font_name, 12)
            y = height - 40
    c.save()
    return out


def write_pdf_or_txt(text: str, output_path: str | Path, font_path: Optional[str] = None) -> Path:
    out = Path(output_path)
    if out.suffix.lower() == ".pdf":
        return write_text_pdf(text, out, font_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_escape_pdf_text(text), encoding="utf-8")
    return out
