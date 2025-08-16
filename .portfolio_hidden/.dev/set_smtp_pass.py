#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--value", required=True, help="新的 SMTP App Password（16 碼，不要含空白）")
    args = ap.parse_args()
    val = re.sub(r"\s+", "", args.value.strip())
    if not val or len(val) < 16:
        print("[ERR] 看起來不像有效的 16 碼 App Password")
        return 2
    if not ENV.exists():
        print(f"[ERR] 找不到 {ENV}")
        return 3
    txt = ENV.read_text(encoding="utf-8")
    if "SMTP_PASS=" not in txt:
        txt += "\nSMTP_PASS=\n"
    txt = re.sub(r"^SMTP_PASS=.*$", f"SMTP_PASS={val}", txt, flags=re.MULTILINE)
    ENV.write_text(txt, encoding="utf-8")
    print("[OK] 已更新 .env 的 SMTP_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
