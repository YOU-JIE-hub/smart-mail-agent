#!/usr/bin/env python3
# 檔案：tools/imap_pass_sanitize.py
# 目的：移除 .env 內 IMAP_PASS 的所有空白字元（避免貼入時混入空格、換行）

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"


def main() -> int:
    if not ENV.exists():
        print(f"[ERR] 找不到 {ENV}")
        return 2

    txt = ENV.read_text(encoding="utf-8")
    m = re.search(r"^IMAP_PASS=(.*)$", txt, flags=re.MULTILINE)
    if not m:
        print("[MISS] .env 內沒有 IMAP_PASS=… 這一行")
        return 3

    raw = m.group(1)
    cleaned = re.sub(r"\s+", "", raw)
    if cleaned == raw:
        print("[OK] IMAP_PASS 沒有空白，不需更動")
        return 0

    txt2 = txt[: m.start(1)] + cleaned + txt[m.end(1) :]
    ENV.write_text(txt2, encoding="utf-8")
    print("[FIX] 已移除 IMAP_PASS 的空白字元")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
