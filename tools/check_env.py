#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_DIRS = [ROOT / "logs", ROOT / "data" / "output"]
REQ_TPLS = [
    ROOT / "templates" / "sales_inquiry_reply.j2",
    ROOT / "templates" / "complaint_low.j2",
    ROOT / "templates" / "complaint_med.j2",
    ROOT / "templates" / "complaint_high.j2",
    ROOT / "templates" / "needs_summary.md.j2",
]
POLICY = ROOT / "configs" / "policy.yaml"
DEFAULT_FONT = ROOT / "assets" / "fonts" / "NotoSansTC-Regular.ttf"


def main() -> int:
    print("=== Environment Self-Check ===")
    print("\n[Directories]")
    for d in REQ_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        print(f"- {d}: ok")
    print("\n[Templates]")
    for t in REQ_TPLS:
        print(f"- {t}: {'exists' if t.exists() else 'missing'}")
    print("\n[Policy]")
    print(f"- {POLICY}: {'exists' if POLICY.exists() else 'missing'}")
    print("\n[Fonts]")
    font_path = os.getenv("SMA_PDF_FONT_PATH") or os.getenv("FONT_PATH") or str(DEFAULT_FONT)
    fp = Path(font_path if Path(font_path).is_absolute() else ROOT / font_path)
    print(f"- {fp}: {'exists' if fp.exists() else 'missing'}")
    if not fp.exists():
        print("建議：提供中文字型；否則 PDF 流程會降級為 .txt（非致命）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
