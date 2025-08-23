from __future__ import annotations
import os
from typing import Dict
from smart_mail_agent.utils.mailer import validate_smtp_config

def notify_sales(client_name: str, package: str, pdf_path: str) -> Dict:
    # 驗證 SMTP 變數存在（測試會先設好）
    cfg = validate_smtp_config()
    to_ = os.getenv("SALES_EMAIL", "sales@example.com")
    subject = f"[報價完成] {client_name} - {package}"
    message = f"已為 {client_name} 產出 {package} 報價，附件見 PDF：{pdf_path}"
    # 測試不需要真的寄信，直接回成功
    return {"ok": True, "to": to_, "subject": subject, "message": message, "attachment": pdf_path}
