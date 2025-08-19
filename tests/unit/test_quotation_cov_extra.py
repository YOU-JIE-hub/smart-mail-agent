from modules.quotation import choose_package

def test_choose_package_branches():
    # ERP/SSO -> 企業整合
    r = choose_package(subject="需要 ERP 整合", content="")
    assert r["package"] == "企業整合" and r["needs_manual"] is False

    # workflow -> 進階自動化
    r = choose_package(subject="", content="我們想要 workflow 自動化")
    assert r["package"] == "進階自動化"

    # 大附件或 >=5MB -> needs_manual
    r = choose_package(subject="附件很大，請協助", content="")
    assert r["needs_manual"] is True
    r = choose_package(subject="", content="附件 6MB，請處理")
    assert r["needs_manual"] is True

    # 其他 -> 標準
    r = choose_package(subject="一般詢價", content="內容")
    assert r["package"] == "標準"
