from __future__ import annotations
import importlib
import logging
import sys

def test_get_logger_and_level(monkeypatch, caplog):
    monkeypatch.setenv("SMA_LOG_LEVEL", "DEBUG")
    sys.modules.pop("smart_mail_agent.utils.logger", None)
    logger_mod = importlib.import_module("smart_mail_agent.utils.logger")

    caplog.set_level(logging.DEBUG)
    lg = logger_mod.get_logger("sma.test")
    lg.debug("hello debug")
    assert any("hello debug" in rec.message for rec in caplog.records)

    # 不會重複掛 handler
    before = len(lg.handlers)
    lg2 = logger_mod.get_logger("sma.test")
    assert len(lg2.handlers) == before
