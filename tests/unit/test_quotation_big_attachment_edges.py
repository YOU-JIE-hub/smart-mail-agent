import importlib
import pytest

choose_package = importlib.import_module("modules.quotation").choose_package

CANON = {"標準", "企業整合", "進階自動化"}

@pytest.mark.parametrize(
    "text,expected_manual,expected_pkg_when_manual",
    [
        ("附件 5MB", True, "標準"),
        ("附件 5 mb", True, "標準"),
        ("附件 5 Mb", True, "標準"),
        ("附件 6 MB 與 ERP", True, "標準"),  # 有高階關鍵字也要被大附件覆蓋
        ("檔案太大，請協助", True, "標準"),     # 關鍵字無數字也要觸發
        ("大附件，請協助", True, "標準"),
        ("附件很大", True, "標準"),
        ("附件過大", True, "標準"),
        ("檔案過大", True, "標準"),
        ("6Mb", True, "標準"),                # 英文字母大小寫
        ("附件 4.9MB", False, None),          # 邊界：< 5MB 不觸發
        ("附件 4 MB", False, None),
    ],
)
def test_big_attachment_edges(text, expected_manual, expected_pkg_when_manual):
    r = choose_package(subject="", content=text)
    assert "package" in r and "needs_manual" in r
    assert bool(r["needs_manual"]) is expected_manual
    if expected_manual:
        assert r["package"] == expected_pkg_when_manual
    else:
        assert isinstance(r["package"], str) and r["package"] in CANON


def test_big_attachment_in_subject():
    r = choose_package(subject="附件 6MB", content="")
    assert r["needs_manual"] is True
    assert r["package"] == "標準"
