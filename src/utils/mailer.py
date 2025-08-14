from __future__ import annotations

import mimetypes
import os
import pathlib
import smtplib
from email.message import EmailMessage
from typing import Iterable, Mapping, Optional, Tuple

OFFLINE = str(os.getenv("OFFLINE", "0")) == "1"


def validate_smtp_config(cfg: Mapping[str, str]) -> Tuple[bool, str]:
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM"]
    missing = [k for k in required if not str(cfg.get(k, "")).strip()]
    if missing:
        return False, f"missing: {', '.join(missing)}"
    try:
        int(cfg["SMTP_PORT"])
    except Exception:
        return False, "SMTP_PORT must be integer"
    return True, ""


def send_email_with_attachment(
    to: str,
    subject: str,
    body: str,
    attachments: Optional[Iterable[str]] = None,
    cfg: Optional[Mapping[str, str]] = None,
    use_tls: Optional[bool] = None,
    dry_run: Optional[bool] = None,
) -> bool:
    cfg_all = dict(os.environ)
    if cfg:
        cfg_all.update({k: str(v) for k, v in cfg.items()})
    ok, msg = validate_smtp_config(cfg_all)
    if dry_run is None:
        dry_run = OFFLINE or str(cfg_all.get("DRY_RUN", "0")) == "1"
    if dry_run:
        return ok
    if not ok:
        return False

    host = cfg_all["SMTP_HOST"]
    port = int(cfg_all["SMTP_PORT"])
    user = cfg_all["SMTP_USERNAME"]
    pwd = cfg_all["SMTP_PASSWORD"]
    from_addr = cfg_all["SMTP_FROM"]
    if use_tls is None:
        use_tls = str(cfg_all.get("SMTP_USE_TLS", "1")).lower() not in ("0", "false", "no")

    msg_obj = EmailMessage()
    msg_obj["From"] = from_addr
    msg_obj["To"] = to
    msg_obj["Subject"] = subject
    msg_obj.set_content(body)

    for p in attachments or []:
        path = pathlib.Path(p)
        if not path.is_file():
            continue
        ctype, _ = mimetypes.guess_type(path.name)
        if not ctype:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        msg_obj.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)

    smtp = smtplib.SMTP(host, port, timeout=10)
    try:
        if use_tls:
            smtp.starttls()
        smtp.login(user, pwd)
        smtp.send_message(msg_obj)
    finally:
        try:
            smtp.quit()
        except Exception:
            pass
    return True


__all__ = ["validate_smtp_config", "send_email_with_attachment"]
