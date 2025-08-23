from __future__ import annotations
from pathlib import Path
from typing import List, Sequence, Union

# --- 嘗試委派到上游 utils.pdf_safe ---
try:
    from utils.pdf_safe import _escape_pdf_text as _escape_pdf_text_upstream  # type: ignore
except Exception:
    _escape_pdf_text_upstream = None  # type: ignore

try:
    from utils.pdf_safe import _write_minimal_pdf as _write_minimal_pdf_upstream  # type: ignore
except Exception:
    _write_minimal_pdf_upstream = None  # type: ignore


def _escape_pdf_text(s: str) -> str:
    """優先使用上游；否則提供保底跳脫：括號與反斜線跳脫、非 ASCII 以 UTF-8 八進位轉義。"""
    if _escape_pdf_text_upstream:
        return _escape_pdf_text_upstream(s)  # type: ignore[misc]

    out: List[str] = []
    for ch in s:
        code = ord(ch)
        if ch in ("\\", "(", ")"):
            out.append("\\" + ch)
        elif 32 <= code <= 126:
            out.append(ch)
        else:
            for b in ch.encode("utf-8"):
                out.append("\\" + oct(b)[2:].zfill(3))
    return "".join(out)


def _write_minimal_pdf(lines: Sequence[Union[str, int, float]], out_path: Union[str, Path]) -> Path:
    """優先委派上游；否則以簡潔合法的 PDF 結構產生單頁文件並回傳路徑。"""
    if _write_minimal_pdf_upstream:
        return _write_minimal_pdf_upstream(lines, out_path)  # type: ignore[misc]

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 準備內容（每行一段 text）
    content_cmds = []
    for idx, v in enumerate(lines):
        s = str(v)
        content_cmds.append(f"BT /F1 12 Tf 72 {750 - idx*16} Td ({_escape_pdf_text(s)}) Tj ET")
    content_stream = ("\n".join(content_cmds) + "\n").encode("latin-1", errors="ignore")

    # 構造物件
    objs = []
    objs.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objs.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objs.append(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
               b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>\nendobj\n")
    objs.append(b"4 0 obj\n<< /Length " + str(len(content_stream)).encode("ascii") + b" >>\nstream\n"
               + content_stream + b"endstream\nendobj\n")
    objs.append(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    header = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"
    body = bytearray()
    offsets = [0]   # xref entry 0: free
    cur = len(header)
    for obj in objs:
        offsets.append(cur)
        body.extend(obj)
        cur += len(obj)

    xref_start = len(header) + len(body)

    # xref（全部以 ASCII bytes 組合，避免 str/bytes 混用）
    xref_lines = [f"xref\n0 {len(offsets)}\n", "0000000000 65535 f \n"]
    for ofs in offsets[1:]:
        xref_lines.append(f"{ofs:010d} 00000 n \n")
    xref_bytes = "".join(xref_lines).encode("ascii")

    # trailer（全程 bytes）
    trailer_bytes = (
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n".encode("ascii")
        + str(xref_start).encode("ascii")
        + b"\n%%EOF\n"
    )

    with out.open("wb") as f:
        f.write(header)
        f.write(body)
        f.write(xref_bytes)
        f.write(trailer_bytes)

    return out


__all__ = ["_escape_pdf_text", "_write_minimal_pdf"]
