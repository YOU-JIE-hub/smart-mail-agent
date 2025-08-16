import json
import sys

from smart_mail_agent.spam import orchestrator_offline as oo


def test_cli_json_output(capsys, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["prog", "--subject", "Hello", "--content", "http://x.io", "--json"]
    )
    code = oo._main()
    assert code == 0
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert {"action", "reasons", "scores"} <= set(data.keys())
    assert isinstance(data["scores"].get("link_ratio", 0.0), float)
