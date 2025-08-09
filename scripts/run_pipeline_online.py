#!/usr/bin/env python3
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# 基本清洗，避免空白造成 LOGIN 參數缺失
for k in ("IMAP_USER", "IMAP_PASS", "SMTP_USER", "SMTP_PASS"):
    v = os.getenv(k)
    if v is not None:
        os.environ[k] = v.strip()

# 預設線上模式（若你想離線可 export OFFLINE=1 覆蓋）
os.environ.setdefault("OFFLINE", "0")

# 轉呼叫 pipeline/main.py 並保留原始參數
target = str(ROOT / "pipeline" / "main.py")
sys.argv = ["pipeline/main.py", *sys.argv[1:]]
runpy.run_path(target, run_name="__main__")
