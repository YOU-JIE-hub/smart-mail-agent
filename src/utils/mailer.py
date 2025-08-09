#!/usr/bin/env python3
# 檔案位置：src/utils/mailer.py
# 模組用途：發送 HTML 郵件，可附帶 PDF，支援 SMTP_FROM、REPLY_TO，具完整錯誤處理

import os
import smtplib
from email.message import EmailMessage
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPException, SMTPServerDisconnected

from dotenv import load_dotenv

from utils.logger import logger

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
REPLY_TO = os.getenv("REPLY_TO", SMTP_USER)
SMTP_FROM = os.getenv("SMTP_FROM", f"Smart-Mail-Agent <{SMTP_USER}>")


def validate_smtp_config():
    """
    檢查 SMTP 設定是否齊全，若有缺少欄位則拋出例外。
    """
    required = ["SMTP_USER", "SMTP_PASS", "SMTP_HOST", "SMTP_PORT"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError(f"SMTP 設定錯誤，缺少欄位：{', '.join(missing)}")


def send_email_with_attachment(
    recipient: str, subject: str, body_html: str, attachment_path: str = None
) -> bool:
    """
    發送 HTML 郵件，可選擇附上 PDF 檔案

    參數:
        recipient (str): 收件人 Email
        subject (str): 郵件主旨
        body_html (str): HTML 內容
        attachment_path (str): 附件 PDF 路徑（可選）

    回傳:
        bool: 是否寄送成功

    例外:
        FileNotFoundError: 若附件路徑不存在
        ValueError: SMTP 設定缺失
        SMTPException 等: 其他發信錯誤
    """
    try:
        validate_smtp_config()

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = recipient
        msg["Reply-To"] = REPLY_TO
        msg.set_content("此郵件為 HTML 格式，請使用支援的郵件軟體開啟。")
        msg.add_alternative(body_html, subtype="html")

        if attachment_path:
            if not os.path.exists(attachment_path):
                logger.error("找不到附件：%s", attachment_path)
                raise FileNotFoundError(f"找不到附件：{attachment_path}")
            with open(attachment_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="pdf",
                    filename=os.path.basename(attachment_path),
                )

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)

        logger.info("郵件已成功寄出：%s → %s", subject, recipient)
        return True

    except SMTPAuthenticationError as e:
        logger.error("SMTP 認證失敗：%s", str(e))
        raise
    except SMTPConnectError as e:
        logger.error("SMTP 無法連線：%s", str(e))
        raise
    except SMTPServerDisconnected as e:
        logger.error("SMTP 被中斷：%s", str(e))
        raise
    except SMTPException as e:
        logger.error("SMTP 發信錯誤：%s", str(e))
        raise
    except Exception as e:
        logger.error("寄送郵件過程發生錯誤：%s", str(e))
        raise
