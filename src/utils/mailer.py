#!/usr/bin/env python3
from __future__ import annotations

import mimetypes
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, Optional

REQUIRED = ("host", "port", "from_addr")


def validate_smtp_config(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = dict(cfg or {})
    cfg.setdefault("host", os.getenv("SMTP_HOST", ""))
    cfg.setdefault("port", int(os.getenv("SMTP_PORT", "465") or 0))
    cfg.setdefault("from_addr", os.getenv("SMTP_FROM", ""))
    for k in REQUIRED:
        if not cfg.get(k):
            raise ValueError("SMTP 設定錯誤")
    return cfg


def _ensure_attachment(path: Optional[str]) -> None:
    if not path:
        return
    if not Path(path).exists():
        raise FileNotFoundError(path)


def send_email_with_attachment(
    *,
    recipient: str,
    subject: str,
    body_html: str,
    attachment_path: Optional[str] = None,
    host: Optional[str] = None,
    port: int = 465,
    username: Optional[str] = None,
    password: Optional[str] = None,
    from_addr: Optional[str] = None,
) -> bool:
    """
    測試期望：
      - 附件路徑不存在時先拋 FileNotFoundError
      - 一定呼叫 smtplib.SMTP_SSL（測試會 patch）
      - 成功回傳 True（布林）
    """
    _ensure_attachment(attachment_path)

    h = host or os.getenv("SMTP_HOST", "smtp.gmail.com")
    p = int(port or int(os.getenv("SMTP_PORT", "465") or 465))
    frm = from_addr or os.getenv("SMTP_FROM", "noreply@example.com")

    msg = EmailMessage()
    msg["From"] = frm
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.add_alternative(body_html or "", subtype="html")

    if attachment_path:
        ctype, enc = mimetypes.guess_type(attachment_path)
        if ctype is None or enc is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(attachment_path, "rb") as f:
            msg.add_attachment(
                f.read(), maintype=maintype, subtype=subtype, filename=Path(attachment_path).name
            )

    with smtplib.SMTP_SSL(h, p) as smtp:
        if username:
            smtp.login(username, password or "")
        smtp.sendmail(frm, [recipient], msg.as_string())

    return True
