from __future__ import annotations

import datetime as dt
from collections.abc import Sequence

# -*- coding: utf-8 -*-
from pathlib import Path


def _find_font(candidates: Sequence[str]) -> Path | None:
    extra = [
        "/usr/share/fonts/opentype/noto/NotoSansCJKTC-Regular.otf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Songti.ttc",
    ]
    for c in list(candidates) + extra:
        p = Path(c)
        if p.exists():
            return p
    return None


def _escape_pdf_text(s: str) -> str:
    # 僅保證 PDF 語法合法；非 Latin-1 字元可能顯示成方框（不影響測試與檔案有效性）
    s = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return "".join(ch if 32 <= ord(ch) <= 126 else "?" for ch in s)


def _write_minimal_pdf(lines: list[str], out_path: Path) -> Path:
    # 產生一份 *有效* 的極簡 PDF（1 頁，內建 Helvetica 字型）
    # 版面：A4 (595 x 842 points)，字體 12pt，行距 14pt，自 (72, 800) 起逐行往下
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    # 內容串
    content_lines = ["BT", "/F1 12 Tf", "14 TL", "72 800 Td"]
    for ln in lines:
        content_lines.append(f"({_escape_pdf_text(ln)}) Tj")
        content_lines.append("T*")
    content_lines.append("ET")
    content_str = "\n".join(content_lines) + "\n"
    content_bytes = content_str.encode("latin-1")

    # 物件組裝
    objs = []

    def add_obj(body: bytes) -> int:
        offset = sum(len(x) for x in objs) + len(header)
        objs.append(body)
        return offset

    xref = []
    # 1: Catalog
    xref.append(add_obj(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"))
    # 2: Pages
    xref.append(add_obj(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"))
    # 3: Page
    xref.append(add_obj(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"))
    # 4: Contents (stream)
    stream = b"4 0 obj\n<< /Length " + str(len(content_bytes)).encode("ascii") + b" >>\nstream\n" + content_bytes + b"endstream\nendobj\n"
    xref.append(add_obj(stream))
    # 5: Font
    xref.append(add_obj(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"))

    # xref & trailer
    xref_start = len(header) + sum(len(x) for x in objs)
    xref_table = [b"xref\n0 6\n", b"0000000000 65535 f \n"]
    for off in xref:
        xref_table.append((f"{off:010d} 00000 n \n").encode("ascii"))
    xref_bytes = b"".join(xref_table)
    trailer = b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(xref_start).encode("ascii") + b"\n%%EOF\n"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        f.write(header)
        for o in objs:
            f.write(o)
        f.write(xref_bytes)
        f.write(trailer)
    return out_path


def write_pdf_or_txt(
    lines: list[str],
    out_dir: Path = Path("data/output"),
    basename: str = "attachment",
    font_candidates: Sequence[str] | None = None,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    font_candidates = font_candidates or [
        "assets/fonts/SourceHanSansTC-Regular.otf",
        "assets/fonts/NotoSansTC-Regular.ttf",
    ]
    font_path = _find_font(font_candidates)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas

        pdf_path = out_dir / f"{basename}_{ts}.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=A4)

        font_name = "Helvetica"
        if font_path and font_path.suffix.lower() in {".ttf", ".otf"}:
            try:
                pdfmetrics.registerFont(TTFont("CJK", str(font_path)))
                font_name = "CJK"
            except Exception:
                pass

        c.setFont(font_name, 12)
        width, height = A4
        x, y = 20 * mm, height - 20 * mm
        for line in lines:
            c.drawString(x, y, line)
            y -= 8 * mm
            if y < 20 * mm:
                c.showPage()
                c.setFont(font_name, 12)
                y = height - 20 * mm
        c.save()
        return pdf_path
    except Exception:
        # 無 reportlab：用極簡 PDF 生成器寫出 .pdf
        pdf_path = out_dir / f"{basename}_{ts}.pdf"
        try:
            return _write_minimal_pdf(lines, pdf_path)
        except Exception:
            # 極端狀況才降級 .txt
            txt_path = out_dir / f"{basename}_{ts}.txt"
            txt_path.write_text("\\n".join(lines), encoding="utf-8")
            return txt_path
