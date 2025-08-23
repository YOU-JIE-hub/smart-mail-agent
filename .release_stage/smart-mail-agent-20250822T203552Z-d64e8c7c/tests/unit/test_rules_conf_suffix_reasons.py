import textwrap

from smart_mail_agent.spam import rules


def test_conf_points_and_suffix_reason(tmp_path, monkeypatch):
    yml = textwrap.dedent(
        """
    keywords: {"FREE": 3}
    suspicious_domains: ["bit.ly"]
    suspicious_tlds: ["tk"]
    bad_extensions: [".exe"]
    whitelist_domains: ["example.com"]
    weights: {url_suspicious: 4, tld_suspicious: 3, attachment_executable: 5}
    thresholds: {suspect: 4, spam: 8}
    """
    ).strip()
    conf = tmp_path / "spam_rules.yaml"
    conf.write_text(yml, encoding="utf-8")
    monkeypatch.setattr(rules, "CONF_PATH", str(conf))
    monkeypatch.setattr(rules, "_CACHE", {"mtime": None, "rules": None}, raising=False)

    label, score_points, reasons = rules.label_email(
        "x@notwhitelisted.org",
        "FREE gift",
        "please click http://a.bit.ly/1 另有 http://abc.def.tk/x",
        ["mal.exe"],
    )
    assert label == "spam"
    assert score_points >= 8  # raw points (not normalized)
    assert any(r.startswith("url:") for r in reasons)
    assert any(r.startswith("tld:") for r in reasons)
