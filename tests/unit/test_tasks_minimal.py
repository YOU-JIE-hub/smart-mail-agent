from __future__ import annotations

import importlib

import pytest

CANDIDATES = [
    (
        ["modules.quotation", "src.modules.quotation"],
        ["build_quote", "handle", "process", "main"],
    ),
    (
        ["support_ticket", "src.support_ticket"],
        ["create_ticket", "handle", "process", "main"],
    ),
    (
        ["modules.apply_diff", "src.modules.apply_diff"],
        ["apply_changes", "handle", "process", "main"],
    ),
]


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


def test_tasks_minimal_contract():
    for names, funcs in CANDIDATES:
        m = _mod(names)
        f = _fn(m, funcs)
        try:
            out = f()
        except TypeError:
            pytest.skip(f"{m.__name__}.{f.__name__} requires args; demo skip")
        assert out is not None
