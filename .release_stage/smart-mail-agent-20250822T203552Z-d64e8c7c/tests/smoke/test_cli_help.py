import runpy
import sys
import pytest

@pytest.mark.parametrize("mod", [
    "smart_mail_agent.cli.sma",
    "smart_mail_agent.cli_spamcheck",
])
def test_cli_help_exits_cleanly(mod, monkeypatch):
    monkeypatch.setattr(sys, "argv", [mod.rsplit(".", 1)[-1], "--help"])
    with pytest.raises(SystemExit) as e:
        runpy.run_module(mod, run_name="__main__")
    # argparse --help 正常以 0 或 2 結束（部分實作用 0）
    assert e.value.code in (0, 2)
