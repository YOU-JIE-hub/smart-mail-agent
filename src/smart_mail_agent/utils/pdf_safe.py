#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List

ALLOWED_EXT = ".pdf"


def _escape_pdf_text(s: str) -> str:
    out: List[str] = []
    for ch in s:
        if ch in ("(", ")", "\\"):
            out.append("\\" + ch)
        else:
            o = ord(ch)
            out.append(ch if 32 <= o <= 126 else "?")
    return "".join(out)


def _write_minimal_pdf(lines: Iterable[str], outfile: os.PathLike | str) -> Path:
    path = Path(outfile)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\\n".join(_escape_pdf_text(x) for x in lines)

    content_stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("latin1", "ignore")
    parts: List[bytes] = []

    def add(b: bytes):
        parts.append(b)

    add(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    def obj(i: int, body: bytes):
        add(f"{i} 0 obj\n".encode("ascii"))
        add(body)
        add(b"\nendobj\n")

    obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    obj(
        3,
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
    )
    obj(4, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    stream = b"<< /Length %d >>\nstream\n" % len(content_stream) + content_stream + b"\nendstream"
    obj(5, stream)

    xref_pos = sum(len(x) for x in parts)
    offsets = [0]
    cur = 0
    for x in parts:
        cur += len(x)
        offsets.append(cur)
    obj_starts = [offsets[1], offsets[2], offsets[3], offsets[4], offsets[5]]
    xref = (
        "xref\n0 6\n0000000000 65535 f \n"
        + "\n".join(f"{off:010d} 00000 n " for off in obj_starts)
        + "\n"
    )
    trailer = f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")

    with path.open("wb") as f:
        for x in parts:
            f.write(x)
        f.write(xref.encode("ascii"))
        f.write(trailer)
    return path


def safe_write_pdf_stub(text: str, outdir: str, filename: str) -> str:
    if not outdir or not filename:
        raise ValueError("outdir/filename required")
    base = os.path.basename(filename)
    if not base.lower().endswith(ALLOWED_EXT):
        base += ALLOWED_EXT
    dest = Path(outdir) / base
    dest.parent.mkdir(parents=True, exist_ok=True)
    _write_minimal_pdf([text], dest)
    return str(dest)
