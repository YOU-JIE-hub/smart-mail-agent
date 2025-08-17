#!/usr/bin/env python3
# 檔案位置：tests/test_sales_notifier.py
# 測試模組：sales_notifier.py（寄送報價副本給業務）

import os
import tempfile

import pytest
from modules.sales_notifier import notify_sales


@pytest.mark.parametrize(
    "client_name, package",
    [
        ("test_client", "基礎"),
        ("test_corp", "企業"),
    ],
)
def test_notify_sales_success(client_name, package):
    # 建立臨時 PDF 模擬檔案
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        tmp_pdf.write(b"%PDF-1.4\n% Mock PDF Content")
        pdf_path = tmp_pdf.name

    # 模擬設定 .env 所需的環境變數（如未在環境中預設）
    os.environ["SALES_EMAIL"] = os.getenv("SALES_EMAIL", "h125872359@gmail.com")
    os.environ["SMTP_USER"] = os.getenv("SMTP_USER", "h125872359@gmail.com")
    os.environ["SMTP_PASS"] = os.getenv("SMTP_PASS", "ynqpzewlfiuycaxf")
    os.environ["SMTP_HOST"] = os.getenv("SMTP_HOST", "smtp.gmail.com")
    os.environ["SMTP_PORT"] = os.getenv("SMTP_PORT", "465")

    result = notify_sales(
        client_name=client_name,
        package=package,
        pdf_path=pdf_path,
    )

    # 清理測試檔案
    os.remove(pdf_path)

    assert result is True
