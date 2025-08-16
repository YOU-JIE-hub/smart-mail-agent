from smart_mail_agent.spam.orchestrator_offline import SpamFilterOrchestratorOffline, Thresholds


def test_hidden_and_empty_href_not_counted():
    html = """
    <div hidden><a href="http://x.invalid">hidden</a></div>
    <div style="display: none"><a href="http://x.invalid">hidden2</a></div>
    <a href="#">empty</a>
    <a>missing</a>
    Visible text with little links.
    """
    orch = SpamFilterOrchestratorOffline(
        thresholds=Thresholds(link_ratio_drop=0.80, link_ratio_review=0.50)
    )
    out = orch.decide("通知", html)
    assert out["action"] in ("route", "review")


def test_nested_like_links_and_whitespaces():
    html = '<a href="http://a">A</a>   \n\n  lots \n of   spaces   and text'
    orch = SpamFilterOrchestratorOffline(
        thresholds=Thresholds(link_ratio_drop=0.20, link_ratio_review=0.10)
    )
    out = orch.decide("x", html)
    assert out["action"] in ("drop", "review")
