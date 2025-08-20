#!/usr/bin/env python3
# 檔案：src/send_with_attachment.py
# 目的：提供可測的 CLI main()，直接呼叫本模組的 send_email_with_attachment（可被 mock）
from __future__ import annotations

import argparse
import sys
from smart_mail_agent.ingestion.integrations.send_with_attachment import (
    send_email_with_attachment as _impl_send,
)

# 對外匯出給測試 mock.patch 使用
send_email_with_attachment = _impl_send  # noqa: N816
__all__ = ["send_email_with_attachment", "main"]

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="send_with_attachment.py", add_help=True)
    p.add_argument("--to", required=True, help="收件者 email")
    p.add_argument("--subject", required=True, help="郵件主旨")
    p.add_argument("--body", required=True, help="HTML 內文")
    p.add_argument("--file", required=True, help="要附加的檔案路徑")
    return p

def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    ns = parser.parse_args(argv)  # 預設使用 sys.argv[1:]
    ok = send_email_with_attachment(ns.to, ns.subject, ns.body, ns.file)
    print("郵件已送出" if ok else "郵件寄出失敗")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
