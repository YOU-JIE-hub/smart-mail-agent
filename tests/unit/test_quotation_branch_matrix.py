from __future__ import annotations
import pytest
from modules.quotation import choose_package

CASES = [
    # ERP/SSO -> 企業整合
    ("需要 ERP 整合", "", "企業整合", False),
    ("", "我們計畫導入 SSO 與 ERP", "企業整合", False),
    # workflow 關鍵字 -> 進階自動化
    ("Workflow 引擎", "", "進階自動化", False),
    ("", "workflow 自動化與表單審批", "進階自動化", False),
    # 大附件 / >=5MB -> 需要人工
    ("附件很大，請協助", "", "標準", True),
    ("", "附件 6MB，請處理", "標準", True),
    ("", "有個 5MB 附件在內", "標準", True),  # 邊界值
    # 沒命中關鍵字 -> 標準
    ("一般詢價", "想瞭解產品", "標準", False),
]

@pytest.mark.parametrize("subject,content,expect_pkg,expect_manual", CASES)
def test_choose_package_matrix(subject, content, expect_pkg, expect_manual):
    r = choose_package(subject=subject, content=content)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r
    assert r["package"] == expect_pkg
    assert r["needs_manual"] == expect_manual
