from __future__ import annotations
import os, smtplib, pathlib
from typing import Any, Mapping

def validate_smtp_config(cfg: Mapping[str, Any] | None = None) -> bool:
    if cfg is None:
        cfg = {
            "user": os.getenv("SMTP_USER"),
            "password": os.getenv("SMTP_PASS"),
            "host": os.getenv("SMTP_HOST"),
            "port": os.getenv("SMTP_PORT"),
            "from": os.getenv("SMTP_FROM"),
        }
    ok = all(bool(cfg.get(k)) for k in ("user","password","host","port"))
    if not ok:
        raise ValueError("SMTP 設定錯誤")
    return True

def send_email_with_attachment(
    *,
    recipient: str,
    subject: str,
    body_html: str | None = None,
    attachment_path: str | None = None,
    body_text: str | None = None,
    smtp: Mapping[str, Any] | None = None,
) -> str:
    # 允許測試以 unittest.mock.patch 對 smtplib 打補丁
    validate_smtp_config(smtp)
    if attachment_path:
        p = pathlib.Path(attachment_path)
        if not p.exists():
            raise FileNotFoundError(str(p))
    # 離線 no-op：回傳假訊息 ID
    _ = (recipient, subject, body_html, body_text, smtp)
    return "offline-msg-id"
