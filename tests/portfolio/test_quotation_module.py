import importlib

q = importlib.import_module("modules.quotation")  # shim 到 src/smart_mail_agent/...


def test_choose_package_contract():
    res = q.choose_package("詢價單：附件很大", "需要正式報價，附件 6MB")
    assert isinstance(res, dict)
    assert "package" in res and isinstance(res["package"], str)
    assert "needs_manual" in res and isinstance(res["needs_manual"], bool)
