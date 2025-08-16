from __future__ import annotations
import argparse
import sys

# 真實實作模組
from smart_mail_agent.ingestion.integrations import send_with_attachment as impl

# 對外暴露：讓 tests 用 mock.patch("send_with_attachment.send_email_with_attachment") 能打在這裡
send_email_with_attachment = impl.send_email_with_attachment  # type: ignore[attr-defined]

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Send email with a single attachment (CLI shim)")
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--file", required=True, dest="file")
    return p

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = _build_parser().parse_args(argv)

    # 重要：透過 shim 內的名稱呼叫，這樣 mock 得到呼叫
    ok = send_email_with_attachment(
        to=args.to,
        subject=args.subject,
        body=args.body,
        file_path=args.file,
    )
    print("郵件寄出成功" if ok else "郵件寄出失敗")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
