import os, smtplib
from email.message import EmailMessage
import pytest

pytestmark = [pytest.mark.smtp, pytest.mark.online]

def test_smtp_send_smoke():
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    pwd  = os.environ["SMTP_PASS"]
    from_ = os.environ.get("SMTP_FROM", user)
    to = os.environ["SMTP_TO"]

    msg = EmailMessage()
    msg["Subject"] = "SMA CI SMTP smoke"
    msg["From"] = from_
    msg["To"] = to
    msg.set_content("Hello from CI (manual SMTP integration)")

    with smtplib.SMTP(host, port, timeout=30) as s:
        s.starttls()
        s.login(user, pwd)
        s.send_message(msg)
