import types, builtins
import importlib
import src.patches.handle_router_patch as hr

def test_normalize_alias():
    assert hr._normalize("sales") == "sales_inquiry"
    assert hr._normalize("complain") == "complaint"
    assert hr._normalize("other") == "other"

def test_handle_import_sales_and_complaint(monkeypatch):
    called = []
    def fake_import(name):
        m = types.SimpleNamespace()
        def _handle(req): 
            called.append(name)
            return {"action": name.split(".")[-1]}
        m.handle = _handle
        return m
    monkeypatch.setattr(importlib, "import_module", fake_import)
    assert hr.handle({"predicted_label": "sales"})["action"] == "sales_inquiry"
    assert hr.handle({"predicted_label": "complaint"})["action"] == "complaint"

def test_handle_fallback_general(monkeypatch):
    # 讓 _get_orig 回傳 None，走 fallback
    monkeypatch.setattr(hr, "_get_orig", lambda: None)
    out = hr.handle({"predicted_label": "unknown"})
    assert out["action"] == "reply_general" or out.get("subject", "").startswith("[自動回覆]")
