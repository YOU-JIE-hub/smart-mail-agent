import os, smtplib
from email.message import EmailMessage
import pytest

pytestmark = [pytest.mark.smtp, pytest.mark.online]

REQUIRED = ["SMTP_HOST","SMTP_USER","SMTP_PASS","SMTP_TO"]
# 只有在「CI_SMTP=yes」且所有必需環境都有時才跑
if (
    os.environ.get("OFFLINE") == "1" or
    os.environ.get("CI_SMTP") != "yes" or
    not all(os.getenv(k) for k in REQUIRED)
):
    pytest.skip("SMTP integration test disabled (missing env or not explicitly enabled).",
                allow_module_level=True)

def test_smtp_send_smoke():
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    pwd  = os.environ["SMTP_PASS"]
    from_ = os.environ.get("SMTP_FROM", user)
    to = os.environ["SMTP_TO"]

    msg = EmailMessage()
    msg["From"] = from_
    msg["To"] = to
    msg["Subject"] = "SMA SMTP smoke"
    msg.set_content("hello from CI")

    with smtplib.SMTP(host, port, timeout=20) as s:
        s.starttls()
        s.login(user, pwd)
        s.send_message(msg)
