from __future__ import annotations
import argparse

def send_email_with_attachment(*, recipient: str, subject: str, body_html: str, attachment_path: str) -> bool:
    # 真實專案中會送信；測試中會被 mock。這裡回 True 當作成功。
    return True

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--file", required=True)
    a = p.parse_args()
    ok = send_email_with_attachment(recipient=a.to, subject=a.subject, body_html=a.body, attachment_path=a.file)
    print("OK" if ok else "FAILED")
    return 0 if ok else 2

if __name__ == "__main__":
    import sys
    sys.exit(main())
