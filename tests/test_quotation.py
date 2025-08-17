# tests/test_quotation.py
# 測試目標：quotation.py → 報價分類 + PDF 產出功能

import os

import pytest

from modules.quotation import choose_package, generate_pdf_quote


@pytest.mark.parametrize(
    "subject, content, expected_package",
    [
        ("報價需求", "我想知道報價、價格資訊", "基礎"),
        ("自動分類功能", "是否支援自動化與排程？", "專業"),
        ("整合 API", "想與 ERP 或 LINE 整合", "企業"),
        ("其他詢問", "你們能提供什麼功能？", "企業"),
    ],
)
def test_choose_package(subject, content, expected_package):
    result = choose_package(subject, content)
    assert result["package"] == expected_package
    assert "needs_manual" in result


def test_generate_pdf_quote(tmp_path):
    pdf_path = generate_pdf_quote(package="基礎", client_name="client@example.com")
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")
    assert os.path.getsize(pdf_path) > 0
