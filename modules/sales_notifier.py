#!/usr/bin/env python3
# 檔案位置：modules/sales_notifier.py
# 模組用途：通知業務（OFFLINE 下不實際寄信，回傳離線結果）
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


def _offline() -> bool:
    return os.getenv("OFFLINE", "1") == "1"


# 若專案未提供 utils.mailer，給一個安全占位
try:
    from utils.mailer import send_email_with_attachment  # type: ignore
except Exception:  # noqa: BLE001

    def send_email_with_attachment(  # type: ignore
        to_addr: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "ok": True,
            "offline_stub": True,
            "to": to_addr,
            "subject": subject,
            "attachments": attachments or [],
        }


def notify_sales(
    to_addr: str, subject: str, body: str, attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    通知業務：OFFLINE 不寄信，直接回傳結果；ONLINE 則使用 send_email_with_attachment。
    """
    attachments = attachments or []
    if _offline():
        return {
            "ok": True,
            "offline": True,
            "to": to_addr,
            "subject": subject,
            "attachments": list(attachments),
        }
    return send_email_with_attachment(to_addr, subject, body, attachments=attachments)


__all__ = ["notify_sales"]
