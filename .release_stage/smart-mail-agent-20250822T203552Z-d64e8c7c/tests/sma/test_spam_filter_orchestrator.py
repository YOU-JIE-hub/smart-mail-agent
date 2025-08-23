import importlib
sf = importlib.import_module("smart_mail_agent.spam.spam_filter_orchestrator")
def test_spam_keywords_and_shortlink():
    r1 = sf.SpamFilterOrchestrator().is_legit("FREE gift","", "")
    assert r1["is_spam"] and "en_keywords" in r1["reasons"]
    r2 = sf.SpamFilterOrchestrator().is_legit("","bit.ly/abc", "")
    assert r2["is_spam"] and "shortlink" in r2["reasons"]
