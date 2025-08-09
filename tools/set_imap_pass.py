#!/usr/bin/env python3
# 檔案：tools/set_imap_pass.py
# 用法：python tools/set_imap_pass.py --value '16碼AppPassword'
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--value", required=True, help="新的 IMAP App Password（16 碼，不要含空白）")
    args = ap.parse_args()

    val = re.sub(r"\s+", "", args.value.strip())
    if not val or len(val) < 16:
        print("[ERR] 看起來不像有效的 16 碼 App Password")
        return 2

    if not ENV.exists():
        print(f"[ERR] 找不到 {ENV}")
        return 3

    txt = ENV.read_text(encoding="utf-8")
    if "IMAP_PASS=" not in txt:
        txt += "\nIMAP_PASS=\n"
    txt = re.sub(r"^IMAP_PASS=.*$", f"IMAP_PASS={val}", txt, flags=re.MULTILINE)
    ENV.write_text(txt, encoding="utf-8")
    print("[OK] 已更新 .env 的 IMAP_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
