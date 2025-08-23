import io
import runpy
import sys
import contextlib
import pytest

@pytest.mark.parametrize("mod", ["smart_mail_agent.cli.sma"])
def test_cli_version_exits_cleanly(mod, monkeypatch):
    monkeypatch.setattr(sys, "argv", [mod.rsplit(".", 1)[-1], "--version"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        with pytest.raises(SystemExit) as e:
            runpy.run_module(mod, run_name="__main__")
    assert e.value.code == 0
    out = buf.getvalue()
    assert "smart-mail-agent" in out
