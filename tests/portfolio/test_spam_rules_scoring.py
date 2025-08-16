import json
import pathlib
import tempfile
import textwrap

import src.smart_mail_agent.spam.rules as rules


def test_label_email_with_custom_rules(tmp_path, monkeypatch):
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
    monkeypatch.setattr(rules, "CONF_PATH", conf)
    monkeypatch.setattr(rules, "_CACHE", {"mtime": None, "rules": None}, raising=False)

    # URL + TLD + 附件 直接>=spam
    label, score, reasons = rules.label_email(
        "x@notwhitelisted.org",
        "FREE gift",
        "please click http://a.bit.ly/1 另有 http://abc.def.tk/x",
        ["mal.exe"],
    )
    assert label == "spam"
    assert score >= 8
    assert any(r.startswith("url:") for r in reasons)
