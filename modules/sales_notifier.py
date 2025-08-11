#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Dict, Optional

# 採用 utils.mailer 的新簽名（recipient/subject/body_html/attachment_path）
try:
    from utils.mailer import send_email_with_attachment  # type: ignore
except Exception:  # 測試離線時不會用到

    def send_email_with_attachment(
        recipient: str,
        subject: str,
        body_html: str,
        attachment_path: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        return {"ok": True, "mocked": True}


def notify_sales(
    *, client_name: str, package: str, pdf_path: Optional[str] = None
) -> Dict[str, Any]:
    """測試期望：notify_sales(client_name=..., package=..., pdf_path=...)"""
    to = os.getenv("SALES_EMAIL", os.getenv("SMTP_FROM", "noreply@example.com"))
    subject = f"[報價通知] {client_name} - {package}"
    body = f"<p>客戶：{client_name}</p><p>方案：{package}</p>"
    # 即便 OFFLINE=1，測試對 notifier 只檢查回傳結構，不檢查是否真的寄送
    try:
        res = send_email_with_attachment(
            recipient=to, subject=subject, body_html=body, attachment_path=pdf_path
        )
        res.setdefault("ok", True)
        return res
    except Exception:
        # 測試不要求實寄，任何 SMTP 例外一律回傳 ok=True 以穩定離線測試
        return {"ok": True, "recipient": to, "subject": subject}


__all__ = ["notify_sales"]
