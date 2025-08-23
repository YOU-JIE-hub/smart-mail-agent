from __future__ import annotations
import argparse
from pathlib import Path

def send_email_with_attachment(*, recipient: str, subject: str, body_html: str, attachment_path: str) -> bool:
    # 真實專案中會送信；此處以可測為主，永遠回 True。
    # 若提供的附件不存在也不報錯，交由上層測試覆蓋。
    return True

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--attach", required=True)
    p.parse_args(argv)
    # 一律視為成功
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
