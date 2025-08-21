import importlib

qmod = importlib.import_module("modules.quotation")
choose_package = qmod.choose_package

# 幫手：同一批輸入，分別以 kwargs（新路徑）與位置參數（legacy 路徑）呼叫
def call_kwargs(subj, cont):
    return choose_package(subject=subj, content=cont)
def call_legacy(subj, cont):
    return choose_package(subj, cont)

def test_pricing_keywords_on_both_paths():
    subj = "報價需求"
    cont = "我想知道報價、價格資訊"
    r1 = call_kwargs(subj, cont)
    r2 = call_legacy(subj, cont)
    assert r1["package"] == "標準" and not r1["needs_manual"]
    assert r2["package"] == "基礎" and not r2["needs_manual"]

def test_enterprise_keywords_on_both_paths():
    subj = "需要 ERP 整合"
    r1 = call_kwargs(subj, "")
    r2 = call_legacy(subj, "")
    assert r1["package"] == "企業整合" and not r1["needs_manual"]
    assert r2["package"] == "企業" and not r2["needs_manual"]

def test_automation_keywords_on_both_paths():
    cont = "workflow 自動化與表單審批"
    r1 = call_kwargs("", cont)
    r2 = call_legacy("", cont)
    assert r1["package"] == "進階自動化" and not r1["needs_manual"]
    assert r2["package"] == "專業" and not r2["needs_manual"]

def test_generic_fallback_legacy_is_enterprise_kwargs_is_standard():
    r1 = call_kwargs("", "")
    r2 = call_legacy("", "")
    assert r1["package"] == "標準" and not r1["needs_manual"]
    assert r2["package"] == "企業" and not r2["needs_manual"]

def test_big_attachment_numeric_thresholds_and_keywords():
    # <5MB 不觸發人工
    assert call_kwargs("", "附件 4.9MB")["needs_manual"] is False
    # =5MB 觸發人工
    r5 = call_kwargs("", "附件 5MB")
    assert r5["needs_manual"] is True and r5["package"] == "標準"
    # >5MB 觸發人工
    r6 = call_kwargs("", "附件 6 MB")
    assert r6["needs_manual"] is True and r6["package"] == "標準"
    # 關鍵字不帶數字也要觸發人工
    rkw = call_kwargs("", "檔案太大，請協助")
    assert rkw["needs_manual"] is True and rkw["package"] == "標準"

def test_big_attachment_overrides_other_keywords():
    # 即使含 ERP/SSO/Workflow，也被大附件覆蓋成 標準 + 需要人工
    for text in ["附件 6MB 與 ERP", "workflow 與附件很大", "SSO + 附件過大"]:
        r = call_kwargs("", text)
        assert r["needs_manual"] is True and r["package"] == "標準"

def test_idempotence_and_no_state_leak():
    samples = [
        ("需要 ERP 整合", ""),
        ("", "workflow 自動化"),
        ("", "附件 6MB"),
        ("報價需求", "想知道價格"),
        ("", ""),
    ]
    for _ in range(3):
        for subj, cont in samples:
            r = call_kwargs(subj, cont)
            assert "package" in r and "needs_manual" in r
