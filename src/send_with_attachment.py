from __future__ import annotations
import argparse
from smart_mail_agent.ingestion.integrations.send_with_attachment import (
    send_email_with_attachment as _impl_send,
)
send_email_with_attachment = _impl_send
def _parser():
    p=argparse.ArgumentParser(prog="send_with_attachment.py")
    p.add_argument("--to",required=True); p.add_argument("--subject",required=True)
    p.add_argument("--body",required=True); p.add_argument("--file",required=True)
    return p
def main()->int|None:
    a=_parser().parse_args()
    ok=send_email_with_attachment(a.to,a.subject,a.body,a.file)
    return 0 if ok else 1
if __name__=="__main__": raise SystemExit(main() or 0)
