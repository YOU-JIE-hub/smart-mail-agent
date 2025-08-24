from __future__ import annotations

import argparse
import sys


def send_email_with_attachment(to: str, subject: str, body: str, file: str) -> bool:
    # 真實實作由測試 mock；此處僅提供函式存在
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--file", required=True)
    ns = ap.parse_args(argv)
    ok = send_email_with_attachment(ns.to, ns.subject, ns.body, ns.file)
    print("OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
