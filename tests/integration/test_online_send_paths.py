from __future__ import annotations

import importlib

oc = importlib.import_module("scripts.online_check")


def _env_ok(monkeypatch):
    monkeypatch.setenv("SMTP_USER", "u@example.com", prepend=False)
    monkeypatch.setenv("SMTP_PASS", "x", prepend=False)
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com", prepend=False)
    monkeypatch.setenv("SMTP_PORT", "465", prepend=False)
    monkeypatch.setenv("REPLY_TO", "r@example.com", prepend=False)


def test_missing_env_returns_2(monkeypatch):
    for k in ["SMTP_USER", "SMTP_PASS", "SMTP_HOST", "SMTP_PORT", "REPLY_TO"]:
        monkeypatch.delenv(k, raising=False)
    assert oc.main() == 2


def test_smtp_fail_returns_1(monkeypatch):
    _env_ok(monkeypatch)

    class Dummy:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def login(self, u, p):
            pass

        def send_message(self, msg):
            raise RuntimeError("network down")

    monkeypatch.setattr(oc.smtplib, "SMTP_SSL", Dummy)
    assert oc.main() == 1


def test_success_returns_0(monkeypatch):
    _env_ok(monkeypatch)

    class Dummy:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def login(self, u, p):
            pass

        def send_message(self, msg):
            return None

    monkeypatch.setattr(oc.smtplib, "SMTP_SSL", Dummy)
    assert oc.main() == 0
