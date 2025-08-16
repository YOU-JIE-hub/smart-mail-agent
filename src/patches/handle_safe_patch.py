from __future__ import annotations

try:
    from utils.pdf_safe import write_pdf_or_txt  # re-export for tests
except Exception:

    def write_pdf_or_txt(path, text):  # pragma: no cover
        from pathlib import Path

        Path(path).write_text(str(text), encoding="utf-8")


__all__ = ["write_pdf_or_txt"]
