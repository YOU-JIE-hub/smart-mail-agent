import importlib, sys, pytest
sys.path.insert(0, "src")
rules = importlib.import_module("smart_mail_agent.spam.rules")

def test_rules_module_loads():
    assert rules is not None

def test_contains_keywords_if_present():
    fn = getattr(rules, "contains_keywords", None)
    if fn is None:
        pytest.skip("contains_keywords not implemented")
    assert fn("免費中獎", ["免費","中獎"]) is True
    assert fn("正常內容", ["免費","中獎"]) is False

def test_link_ratio_if_present():
    fn = getattr(rules, "link_ratio", None)
    if fn is None:
        pytest.skip("link_ratio not implemented")
    v = fn('<a href="#">a</a> 文本 <a href="#">b</a>')
    assert 0.0 <= v <= 1.0
