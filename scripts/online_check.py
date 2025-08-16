#!/usr/bin/env python3
from __future__ import annotations
import os, sys, smtplib, ssl, time
from email.message import EmailMessage

def main() -> int:
    user = os.getenv("SMTP_USER") or ""
    pw   = os.getenv("SMTP_PASS") or ""
    host = os.getenv("SMTP_HOST") or ""
    port = int(os.getenv("SMTP_PORT") or "465")
    to   = os.getenv("REPLY_TO") or user

    if not all([user, pw, host, port, to]):
        print("缺少必要環境變數 (SMTP_USER/SMTP_PASS/SMTP_HOST/SMTP_PORT/REPLY_TO)", file=sys.stderr)
        return 2

    msg = EmailMessage()
    msg["Subject"] = f"[Online Check] Smart Mail Agent smoke {time.strftime('%Y-%m-%d %H:%M:%S')}"
    msg["From"] = user
    msg["To"] = to
    msg.set_content("這是一封線上冒煙測試信（請忽略）。")

    try:
        with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=20) as s:
            s.login(user, pw)
            s.send_message(msg)
    except Exception as e:
        print(f"寄信失敗: {e}", file=sys.stderr)
        return 1

    print("SMTP 寄信成功")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
