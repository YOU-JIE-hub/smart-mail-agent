from __future__ import annotations
import argparse

def send_email_with_attachment(to: str, subject: str, body: str, file: str) -> bool:
    # 真實世界會寄信；測試中會被 mock 掉
    return True

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--file", required=True)
    ns = p.parse_args(argv)
    ok = send_email_with_attachment(ns.to, ns.subject, ns.body, ns.file)
    print("OK" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
