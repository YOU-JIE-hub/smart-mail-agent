from __future__ import annotations

import re
from pathlib import Path
from typing import Any

__all__ = ["write_pdf_or_txt"]


def _sanitize_filename(name: str) -> str:
    # 只保留安全字元，避免 ../ 等跳脫
    base = Path(name).name
    base = re.sub(r"[^A-Za-z0-9_.-]+", "_", base).strip("._")
    return base or "document.pdf"


def _try_write_pdf(
    text: str, target: Path, *, font_path: str | None = None
) -> Path | None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics  # type: ignore
        from reportlab.pdfbase.ttfonts import TTFont  # type: ignore
        from reportlab.pdfgen import canvas
    except Exception:
        return None

    target = target.with_suffix(".pdf")
    try:
        font_name = "Helvetica"
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("CompatFont", font_path))
                font_name = "CompatFont"
            except Exception:
                font_name = "Helvetica"

        c = canvas.Canvas(str(target), pagesize=A4)
        c.setFont(font_name, 12)
        width, height = A4
        y = height - 72
        for line in text.splitlines() or [""]:
            c.drawString(72, y, line)
            y -= 16
            if y < 72:
                c.showPage()
                c.setFont(font_name, 12)
                y = height - 72
        c.save()
        return target
    except Exception:
        return None


def _to_text(data: Any) -> str:
    if isinstance(data, list | tuple | set):
        return "\n".join(str(x) for x in data)
    return "" if data is None else str(data)


def write_pdf_or_txt(
    data: Any,
    outdir_or_path: str | Path,
    basename: str | None = None,
    *,
    font_path: str | None = None,
) -> str:
    """
    新式：write_pdf_or_txt(data, outdir, basename)
    舊式：write_pdf_or_txt(data, final_path)

    - 會嘗試寫 PDF；失敗回退 .txt
    - 自動清理 basename，禁止路徑跳脫；最終輸出「一定」位於 outdir 下
    - 回傳實際寫出的檔案路徑（str）
    """
    text = _to_text(data)

    p = Path(outdir_or_path)
    # 舊式：第二參數就是最終檔案路徑
    if basename is None:
        dest_dir = p.parent
        dest_dir.mkdir(parents=True, exist_ok=True)
        safe_name = _sanitize_filename(p.name or "document.pdf")
        target = dest_dir / safe_name
    else:
        # 新式：指定目錄 + 檔名
        dest_dir = p
        dest_dir.mkdir(parents=True, exist_ok=True)
        safe_name = _sanitize_filename(basename)
        # 預設加 .pdf
        if not (safe_name.endswith(".pdf") or safe_name.endswith(".txt")):
            safe_name += ".pdf"
        target = dest_dir / safe_name

    # 強制限制在 dest_dir 裡
    try:
        target.resolve().relative_to(dest_dir.resolve())
    except Exception:
        target = dest_dir / target.name

    # 先試 PDF，否則 TXT
    written = _try_write_pdf(text, target, font_path=font_path)
    if written:
        return str(written)

    target_txt = target.with_suffix(".txt")
    target_txt.write_text(text, encoding="utf-8")
    return str(target_txt)


def _escape_pdf_text(s: str) -> str:
    """Escape into ASCII-printable-only for PDF text objects.
    - backslash -> \\\\
    - ( and )  -> \\( and \\)
    - keep \n/\r/\t; other control chars -> space
    - non-ASCII -> space
    """
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    out = []
    for ch in s:
        o = ord(ch)
        # control chars except \n \r \t -> space
        if o < 32 and ch not in ("\n", "\r", "\t"):
            out.append(" ")
            continue
        # restrict to ASCII printable
        if o > 126:
            out.append(" ")
            continue
        if ch == "\\":
            out.append("\\\\")
        elif ch == "(":
            out.append("\\(")
        elif ch == ")":
            out.append("\\)")
        else:
            out.append(ch)
    return "".join(out)


def _write_minimal_pdf(lines, out_path):
    """Write a tiny valid PDF with Helvetica using only ASCII content.
    lines: Iterable[str]; out_path: str|Path
    Returns: Path
    """
    from pathlib import Path

    out = Path(out_path).with_suffix(".pdf")
    # escape & join content
    esc = [_escape_pdf_text(str(line)) for line in lines]
    # PDF content stream: move text down each line with T*
    # Start at (72, 720). T* uses leading = 14pt by default after TL/leading set.
    content_ops = ["BT", "/F1 12 Tf", "72 720 Td", "14 TL"]
    for i, s in enumerate(esc):
        if i == 0:
            content_ops.append(f"({s}) Tj")
        else:
            content_ops.append("T*")
            content_ops.append(f"({s}) Tj")
    content_ops.append("ET")
    content = "\n".join(content_ops).encode("latin-1", "replace")
    stream_len = len(content)

    objs = []
    # 1: Catalog
    objs.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    # 2: Pages
    objs.append(b"2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n")
    # 3: Page
    objs.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    )
    # 4: Font
    objs.append(
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    )
    # 5: Contents
    objs.append(
        b"5 0 obj\n<< /Length "
        + str(stream_len).encode("ascii")
        + b" >>\nstream\n"
        + content
        + b"\nendstream\nendobj\n"
    )

    # Assemble with xref
    parts = []
    parts.append(b"%PDF-1.4\n")
    offsets = [0]  # object 0 is the free object
    for obj in objs:
        offsets.append(sum(len(x) for x in parts))  # byte offset of this obj
        parts.append(obj)

    xref_pos = sum(len(x) for x in parts)
    # xref table
    xref = [b"xref\n", f"0 {len(offsets)}\n".encode("ascii")]
    xref.append(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        xref.append(f"{off:010d} 00000 n \n".encode("ascii"))

    trailer = (
        b"trailer\n<< /Size "
        + str(len(offsets)).encode("ascii")
        + b" /Root 1 0 R >>\nstartxref\n"
        + str(xref_pos).encode("ascii")
        + b"\n%%EOF\n"
    )

    with out.open("wb") as f:
        for part in parts:
            f.write(part)
        for row in xref:
            f.write(row)
        f.write(trailer)

    return out
