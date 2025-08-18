from __future__ import annotations
import argparse, mimetypes, os, smtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger("sma")

def send_email_with_attachment(*, recipient: str, subject: str, body_html: str, attachment_path: str | None) -> bool:
    # 簡化：實作真正 SMTP，但測試會用 mock 取代本函式
    try:
        msg = EmailMessage()
        msg["From"] = os.getenv("REPLY_TO", "no-reply@example.com")
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.add_alternative(body_html or "", subtype="html")
        if attachment_path:
            ctype, _ = mimetypes.guess_type(attachment_path)
            maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
            with open(attachment_path, "rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(attachment_path))
        with smtplib.SMTP_SSL(os.getenv("SMTP_HOST","localhost"), int(os.getenv("SMTP_PORT","465"))) as s:
            s.login(os.getenv("SMTP_USER","user"), os.getenv("SMTP_PASS","pass"))
            s.send_message(msg)
        return True
    except Exception as e:
        logger.error("[SMTP] 寄信失敗：%s", e)
        return False

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--file")
    args = p.parse_args(argv)

    ok = send_email_with_attachment(recipient=args.to, subject=args.subject, body_html=args.body, attachment_path=args.file)
    print("郵件寄出成功" if ok else "郵件寄出失敗")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
