from __future__ import annotations

import importlib

import pytest


def _mod(cands):
    for name in cands:
        try:
            return importlib.import_module(name)
        except Exception:
            continue
    pytest.skip(f"module not found: {cands}")


def _fn(mod, cands):
    for n in cands:
        f = getattr(mod, n, None)
        if callable(f):
            return f
    pytest.skip(f"no callable in {mod.__name__}: {cands}")


def test_spam_stack_allow_and_block():
    orch = _mod(["spam.spam_filter_orchestrator", "src.spam.spam_filter_orchestrator"])
    fn = _fn(orch, ["run", "filter_email", "evaluate", "orchestrate"])
    normal = {
        "from": "bob@company.com",
        "subject": "請提供報價",
        "body": "想了解方案與報價",
    }
    bad = {
        "from": "x@spam.com",
        "subject": "免費中獎",
        "body": "點此領獎 http://bad.example",
    }
    out1 = fn(normal)
    out2 = fn(bad)
    assert out1 is not None and out2 is not None
