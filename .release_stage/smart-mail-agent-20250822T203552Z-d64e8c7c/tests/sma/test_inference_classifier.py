import importlib
ic = importlib.import_module("smart_mail_agent.inference_classifier")

def test_smart_truncate():
    assert ic.smart_truncate("abc", 2).endswith("...")

def test_classify_intent_unknown_when_no_model():
    r = ic.classify_intent("x","y")
    assert r["label"] in ("unknown","other","sales_inquiry","complaint")

def test_classify_intent_with_keywords(monkeypatch):
    monkeypatch.setattr(ic, "load_model", lambda: object())
    r = ic.classify_intent("我要報價", "")
    assert r["label"]=="sales_inquiry"
    r2 = ic.classify_intent("退款", "")
    assert r2["label"]=="complaint"
