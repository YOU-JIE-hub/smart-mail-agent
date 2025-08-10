#!/usr/bin/env python3
from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from smtplib import (
    SMTPAuthenticationError,
    SMTPConnectError,
    SMTPException,
    SMTPServerDisconnected,
)

from dotenv import load_dotenv

from utils.logger import logger  # 專案內的單一 logger

# 載入 .env
load_dotenv()

# SMTP/寄件人設定
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT") or "465")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
REPLY_TO = os.getenv("REPLY_TO") or (SMTP_USER or "")
SMTP_FROM = os.getenv("SMTP_FROM") or (
    f"Smart-Mail-Agent <{SMTP_USER}>" if SMTP_USER else "Smart-Mail-Agent"
)


def validate_smtp_config() -> None:
    """檢查 SMTP 設定是否齊全，缺少則丟 ValueError。"""
    required = ["SMTP_USER", "SMTP_PASS", "SMTP_HOST", "SMTP_PORT"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise ValueError(f"SMTP 設定錯誤，缺少欄位：{', '.join(missing)}")


def send_email_with_attachment(
    recipient: str,
    subject: str,
    body_html: str,
    attachment_path: str | None = None,
) -> bool:
    """
    發送 HTML 郵件（可選 PDF 附件）。
    若環境變數 OFFLINE=1/true/yes/on，直接回傳成功，不做實際 SMTP 連線（給 CI 用）。
    """
    # ---- 離線模式：直接當作成功 ----
    if str(os.getenv("OFFLINE", "0")).lower() in ("1", "true", "yes", "on"):
        logger.info("OFFLINE=1 → 跳過實際 SMTP 寄送（回傳成功）")
        return True

    # 正常流程檢查設定
    validate_smtp_config()

    # 組裝 Email
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = recipient
    if REPLY_TO:
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

    # 寄送
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        logger.info("郵件已成功寄出：%s → %s", subject, recipient)
        return True

    except SMTPAuthenticationError as e:
        logger.error("SMTP 認證失敗：%s", e)
        raise
    except SMTPConnectError as e:
        logger.error("SMTP 無法連線：%s", e)
        raise
    except SMTPServerDisconnected as e:
        logger.error("SMTP 被中斷：%s", e)
        raise
    except SMTPException as e:
        logger.error("SMTP 發信錯誤：%s", e)
        raise
    except Exception as e:
        logger.error("寄送郵件過程發生錯誤：%s", e)
        raise
