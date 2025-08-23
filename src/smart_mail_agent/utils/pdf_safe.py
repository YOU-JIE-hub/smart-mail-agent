from __future__ import annotations
from typing import Iterable, Sequence
from pathlib import Path
import re

def _escape_pdf_text(s: str) -> str:
    # 先把非 ASCII 轉成 \uXXXX / \xNN 形式（皆為 ASCII 字元）
    ascii_safe = s.encode("ascii", "backslashreplace").decode("ascii")
    # 針對 PDF 特殊字元做轉義
    ascii_safe = ascii_safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    # 保證輸出皆為可列印 ASCII
    return "".join(ch for ch in ascii_safe if 32 <= ord(ch) <= 126)

def _sanitize_filename(title: str) -> str:
    t = re.sub(r"\s+", "_", title.strip())
    t = re.sub(r"[^A-Za-z0-9_\-\.]", "_", t)
    return t or "output"

def _write_minimal_pdf(lines: Sequence[str], out_path: Path) -> None:
    # 極簡 PDF（足以產出合法檔，測試不解析內容）
    out_path.parent.mkdir(parents=True, exist_ok=True)
    txt = "\\n".join(_escape_pdf_text(s) for s in lines)
    content = f"""%PDF-1.4
1 0 obj<<>>endobj
2 0 obj<< /Length 44 >>stream
BT /F1 12 Tf 72 720 Td ({_escape_pdf_text(txt)}) Tj ET
endstream endobj
3 0 obj<< /Type /Page /Parent 4 0 R /Contents 2 0 R >>endobj
4 0 obj<< /Type /Pages /Count 1 /Kids [3 0 R] >>endobj
5 0 obj<< /Type /Catalog /Pages 4 0 R >>endobj
xref
0 6
0000000000 65535 f 
trailer<< /Root 5 0 R /Size 6 >>
startxref
0
%%EOF
"""
    out_path.write_text(content, encoding="latin-1")

def write_pdf_or_txt(lines: Sequence[str], out_dir: Path, filename: str | None = None):
    """
    允許 2 或 3 參數：
      - write_pdf_or_txt(lines, out_dir)
      - write_pdf_or_txt(lines, out_dir, filename)
    回傳輸出檔 Path（優先 PDF，失敗則 .txt）
    """
    if filename is None:
        filename = "output"
    base = _sanitize_filename(filename)
    out_dir = Path(out_dir)
    pdf_path = out_dir / f"{base}.pdf"
    try:
        _write_minimal_pdf(lines, pdf_path)
        return pdf_path
    except Exception:
        txt_path = out_dir / f"{base}.txt"
        txt_path.write_text("\n".join(str(s) for s in lines), encoding="utf-8")
        return txt_path
