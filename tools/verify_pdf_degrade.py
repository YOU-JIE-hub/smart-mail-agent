#!/usr/bin/env python3
from __future__ import annotations

import builtins
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for p in (ROOT, SRC):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

from src.utils.pdf_safe import write_pdf_or_txt


@contextmanager
def break_reportlab():
    real = builtins.__import__

    def fake(name, *a, **k):
        if name.startswith("reportlab"):
            raise ImportError("blocked")
        return real(name, *a, **k)

    builtins.__import__ = fake
    try:
        yield
    finally:
        builtins.__import__ = real


def main():
    with break_reportlab():
        p = write_pdf_or_txt(["中文測試", "ReportLab 缺失 → 降級 .txt"])
    p = Path(p)
    print(
        "[VERIFY] created:",
        p,
        "exists:",
        p.exists(),
        "size:",
        (p.stat().st_size if p.exists() else 0),
    )


if __name__ == "__main__":
    main()
