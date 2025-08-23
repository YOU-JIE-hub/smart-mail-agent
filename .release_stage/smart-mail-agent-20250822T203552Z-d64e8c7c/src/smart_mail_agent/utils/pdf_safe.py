from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
import re

_ASCII_MIN, _ASCII_MAX = 32, 126

def _ascii_only(s: str) -> str:
    return "".join(ch if _ASCII_MIN <= ord(ch) <= _ASCII_MAX else "?" for ch in s)

def _escape_pdf_text(s: str) -> str:
    s = _ascii_only(s)
    s = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return _ascii_only(s)

def _write_minimal_pdf(lines: List[str], out_path: Path | str) -> Path:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    es = [_escape_pdf_text(x) for x in lines]
    content_lines = []
    y = 750
    for t in es:
        content_lines.append(f"BT /F1 12 Tf 72 {y} Td ({t}) Tj ET")
        y -= 14
    content_stream = "\n".join(content_lines).encode("ascii")

    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")  # 1
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")  # 2
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
    )  # 3
    objects.append(b"<< /Length %d >>\nstream\n" % len(content_stream) + content_stream + b"\nendstream")  # 4
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")  # 5

    xref_offsets: list[int] = [0]
    with p.open("wb") as f:
        f.write(header)
        for i, obj in enumerate(objects, start=1):
            xref_offsets.append(f.tell())
            f.write(f"{i} 0 obj\n".encode("ascii"))
            f.write(obj)
            f.write(b"\nendobj\n")
        xref_start = f.tell()
        f.write(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
        f.write(b"0000000000 65535 f \n")
        for off in xref_offsets[1:]:
            f.write(f"{off:010d} 00000 n \n".encode("ascii"))
        f.write(b"trailer\n")
        f.write(f"<< /Size {len(objects)+1} /Root 1 0 R >>\n".encode("ascii"))
        f.write(b"startxref\n")
        f.write(f"{xref_start}\n".encode("ascii"))
        f.write(b"%%EOF\n")
    return p

_SANITIZE_RE = re.compile(r"[^A-Za-z0-9 _.-]+")

def _sanitize_filename(name: str) -> str:
    name = name.strip()
    name = _SANITIZE_RE.sub("", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "output"

def write_pdf_or_txt(lines: Iterable[str], out_dir: Path | str, filename_hint: str) -> Path:
    out_dir = Path(out_dir)
    base = _sanitize_filename(filename_hint)
    pdf_path = out_dir / f"{base}.pdf"
    try:
        return _write_minimal_pdf(list(lines), pdf_path)
    except Exception:
        txt_path = out_dir / f"{base}.txt"
        out_dir.mkdir(parents=True, exist_ok=True)
        txt_path.write_text("\n".join(lines), encoding="utf-8", errors="replace")
        return txt_path
