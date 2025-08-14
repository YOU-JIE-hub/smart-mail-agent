from __future__ import annotations

import mimetypes
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional


def _env(cfg: Optional[Dict[str, Any]], key: str, default: Optional[str] = None) -> Optional[str]:
    return (cfg or {}).get(key) or os.getenv(key) or default


def validate_smtp_config(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    user = _env(cfg, "SMTP_USER") or _env(cfg, "SMTP_USERNAME")
    pwd = _env(cfg, "SMTP_PASS") or _env(cfg, "SMTP_PASSWORD")
    host = _env(cfg, "SMTP_HOST")
    port_raw = _env(cfg, "SMTP_PORT")
    sender = _env(cfg, "SMTP_FROM") or user
    try:
        port = int(port_raw) if port_raw is not None else 0
    except Exception:
        port = 0
    if not (user and pwd and host and port):
        raise ValueError("SMTP 設定錯誤：缺少必要欄位")
    return {"user": user, "password": pwd, "host": host, "port": port, "sender": sender}


def send_email_with_attachment(
    recipient: str,
    subject: str,
    body_html: str,
    attachment_path: str,
    cfg: Optional[Dict[str, Any]] = None,
) -> bool:
    conf = validate_smtp_config(cfg)
    p = Path(attachment_path)
    if not p.exists():
        raise FileNotFoundError(str(p))

    msg = MIMEMultipart()
    msg["From"] = conf["sender"]
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    ctype, _ = mimetypes.guess_type(p.name)
    subtype = (ctype or "application/octet-stream").split("/")[-1]
    with p.open("rb") as fh:
        part = MIMEApplication(fh.read(), _subtype=subtype)
    part.add_header("Content-Disposition", "attachment", filename=p.name)
    msg.attach(part)

    if conf["port"] == 465:
        with smtplib.SMTP_SSL(conf["host"], conf["port"]) as s:
            s.login(conf["user"], conf["password"])
            s.sendmail(conf["sender"], [recipient], msg.as_string())
    else:
        with smtplib.SMTP(conf["host"], conf["port"]) as s:
            use_tls = os.getenv("SMTP_USE_TLS", "1") not in ("0", "false", "False")
            if use_tls:
                s.starttls()
            s.login(conf["user"], conf["password"])
            s.sendmail(conf["sender"], [recipient], msg.as_string())
    return True
