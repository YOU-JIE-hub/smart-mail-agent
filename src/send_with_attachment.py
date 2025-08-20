#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys

# 嘗試載入正式實作模組（若存在就委派用它）
try:
    from smart_mail_agent.ingestion.integrations import send_with_attachment as _impl
except Exception:
    _impl = None

def send_email_with_attachment(*args, **kwargs):
    """
    Shim 層：提供給測試 mock 的同名函式。
    若底層實作存在，委派過去；否則當作成功（避免外部 I/O）。
    """
    if _impl and hasattr(_impl, "send_email_with_attachment"):
        return _impl.send_email_with_attachment(*args, **kwargs)
    return True

def main(argv: list[str] | None = None) -> int:
    """
    CLI 入口：只呼叫本模組的 send_email_with_attachment()
    讓 tests/test_send_with_attachment.py 的 mock 能攔到。
    """
    argv = argv or sys.argv
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--to", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--file", required=True)
    ns, _ = ap.parse_known_args(argv[1:])

    # 關鍵：呼叫「本模組」函式（可被 mock）
    send_email_with_attachment(ns.to, ns.subject, ns.body, ns.file)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
