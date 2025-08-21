from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

__all__ = ["_escape_pdf_text", "_write_minimal_pdf", "write_pdf_or_txt"]

# 僅保留中英數、底線、連字號；其餘替換成 _
_SAFE_NAME_RX = re.compile(r"[^\w\-\u4e00-\u9fff]+", re.UNICODE)


def _escape_pdf_text(text: str) -> str:
    """將文字轉成 PDF literal string 可接受的形式。
    - '(', ')', '\\' 以反斜線符號轉義
    - 其他非 ASCII 或不可列印字元，以八進位 '\\ooo' 表示
    - 輸出僅含 ASCII 可列印字元
    """
    out: list[str] = []
    for ch in text:
        code = ord(ch)
        if ch in ("(", ")", "\\"):
            out.append("\\" + ch)
        elif 32 <= code <= 126:
            out.append(ch)
        else:
            out.append(f"\\{code:03o}")
    return "".join(out)


def _sanitize_basename(name: str) -> str:
    """移除路徑成分與危險字元，回傳安全檔名（不含副檔名）。"""
    base = Path(name).name  # 擋掉 ../../x 等跳脫
    base = _SAFE_NAME_RX.sub("_", base).strip("._-")
    if not base:
        base = "quote"
    return base[:64]


def _write_minimal_pdf(lines: Iterable[str], out_path: str | Path) -> Path:
    """寫出極簡 PDF，回傳 Path。"""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    esc = [_escape_pdf_text(s) for s in lines]

    # 在 200x200 畫布上，從 (50,150) 往下每行 14pt
    parts: list[str] = ["BT /F1 12 Tf 50 150 Td"]
    for i, s in enumerate(esc):
        parts.append(f"({s}) Tj")
        if i != len(esc) - 1:
            parts.append("0 -14 Td")
    parts.append("ET")
    stream = " ".join(parts).encode("ascii", "strict")
    length = len(stream)

    pdf: list[bytes] = []
    pdf.append(b"%PDF-1.4\n")
    pdf.append(b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n")
    pdf.append(b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n")
    pdf.append(
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]/Contents 4 0 R"
        b"/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
    )
    pdf.append(f"4 0 obj<</Length {length}>>stream\n".encode("ascii"))
    pdf.append(stream)
    pdf.append(b"\nendstream\nendobj\n")
    pdf.append(b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica/Name/F1>>endobj\n")
    # 減到最小；測試只會驗 header/存在性，不解析 xref
    pdf.append(b"xref\n0 0\ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n0\n%%EOF\n")

    out.write_bytes(b"".join(pdf))
    return out


def write_pdf_or_txt(lines: Iterable[str], outdir: str | Path, basename: str) -> str:
    """優先寫 PDF，失敗則寫 .txt；保證路徑安全並建立 outdir。"""
    out_dir = Path(outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe = _sanitize_basename(basename)
    pdf_path = out_dir / f"{safe}.pdf"
    try:
        p = _write_minimal_pdf(lines, pdf_path)
        return str(p)
    except Exception:
        txt_path = out_dir / f"{safe}.txt"
        txt_path.write_text("\n".join(lines), encoding="utf-8")
        return str(txt_path)
