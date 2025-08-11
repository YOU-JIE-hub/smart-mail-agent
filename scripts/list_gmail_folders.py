#!/usr/bin/env python3
# scripts/list_gmail_folders.py
from __future__ import annotations

import imaplib
import os
import sys

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass


def require_env(keys: list[str]) -> list[str]:
    miss = [k for k in keys if not os.getenv(k)]
    if miss:
        print("[MISS] 缺少環境變數：", ", ".join(miss))
    return miss


def main() -> int:
    if os.getenv("OFFLINE", "0") == "1":
        print("[SKIP] OFFLINE=1：略過 IMAP 列表連線")
        return 0
    if require_env(["IMAP_HOST", "IMAP_USER", "IMAP_PASS"]):
        return 2
    host = os.getenv("IMAP_HOST")
    user = os.getenv("IMAP_USER")
    pwd = os.getenv("IMAP_PASS")
    with imaplib.IMAP4_SSL(host) as imap:
        imap.login(user, pwd)
        typ, mailboxes = imap.list()
        print("\nGmail 可用資料夾：\n")
        for box in mailboxes or []:
            print(box.decode())
    return 0


if __name__ == "__main__":
    sys.exit(main())
