#!/usr/bin/env python3
# 檔案位置：src/modules/sales_notifier.py
# 模組用途：寄送報價 PDF 副本至內部業務信箱，支援 retry 機制與錯誤追蹤

import os
from datetime import datetime

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from utils.logger import logger
from utils.mailer import send_email_with_attachment


class EmailSendError(Exception):
    """自訂寄信失敗例外類型（for tenacity retry 判斷）"""

    pass


@retry(
    stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(EmailSendError)
)
def _send_sales_email(client_name: str, package: str, pdf_path: str, recipient_email: str) -> None:
    """
    執行實際寄信動作，內部函式支援 retry

    參數:
        client_name (str): 客戶名稱
        package (str): 報價方案
        pdf_path (str): 附件檔案路徑
        recipient_email (str): 業務信箱（從環境變數讀取）
    """
    if not os.path.exists(pdf_path):
        raise EmailSendError(f"[sales_notifier] 附件不存在：{pdf_path}")

    subject = f"[報價副本通知] {client_name} - {package} 方案"
    body = (
        "<p>系統自動通知業務部：</p>"
        "<ul>"
        f"<li>客戶名稱：{client_name}</li>"
        f"<li>報價方案：{package}</li>"
        f"<li>產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>"
        "</ul>"
        "<p>報價單 PDF 已附檔，請存檔備查。</p>"
    )

    try:
        send_email_with_attachment(
            recipient=recipient_email, subject=subject, body_html=body, attachment_path=pdf_path
        )
    except Exception as e:
        raise EmailSendError(f"[sales_notifier] 寄信失敗：{e}")


def notify_sales(client_name: str, package: str, pdf_path: str) -> bool:
    """
    外部呼叫函式：寄送報價 PDF 副本給內部業務信箱（從環境變數讀取）

    參數:
        client_name (str): 客戶名稱
        package (str): 方案名稱
        pdf_path (str): PDF 檔案路徑

    回傳:
        bool: 是否成功寄出
    """
    recipient_email = os.getenv("SALES_EMAIL")
    if not recipient_email:
        logger.error("[sales_notifier] 環境變數 SALES_EMAIL 未設定，略過寄送")
        return False

    try:
        _send_sales_email(client_name, package, pdf_path, recipient_email)
        logger.info("[sales_notifier] 業務副本已寄出：%s", recipient_email)
        return True
    except EmailSendError as e:
        logger.error("[sales_notifier] 業務寄送失敗（重試 3 次後仍失敗）：%s", str(e))
        return False
