from __future__ import annotations
import importlib, logging, sys

def test_get_logger_and_level(monkeypatch, caplog):
    # 避免 reload 到 Logger 物件：先清掉再乾淨 import 模組
    monkeypatch.setenv("SMA_LOG_LEVEL", "DEBUG")
    sys.modules.pop("smart_mail_agent.utils.logger", None)
    logger_mod = importlib.import_module("smart_mail_agent.utils.logger")

    caplog.set_level(logging.DEBUG)
    lg = logger_mod.get_logger("sma.test")
    lg.debug("hello debug")
    assert any("hello debug" in rec.message for rec in caplog.records)

    before = len(lg.handlers)
    lg2 = logger_mod.get_logger("sma.test")
    assert len(lg2.handlers) == before
