from __future__ import annotations

import importlib
import types

import pytest

ic = importlib.import_module("inference_classifier")


def _new_ic():
    # 兼容 class 名稱或工廠函式
    if hasattr(ic, "InferenceClassifier"):
        return ic.InferenceClassifier()
    if hasattr(ic, "new_classifier"):
        return ic.new_classifier()
    pytest.skip("No InferenceClassifier available")


def _call(clf, text: str):
    for name in ("predict", "__call__", "infer"):
        if hasattr(clf, name):
            fn = getattr(clf, name)
            try:
                return fn(text)
            except TypeError:
                continue
    pytest.skip("Classifier has no callable interface")


def test_pipe_raises_returns_safe_tuple(monkeypatch):
    clf = _new_ic()

    # 用 generator_throw 模擬例外
    def boom(_):
        raise RuntimeError("boom")

    # 嘗試常見內部屬性名稱
    for cand in ("_pipe", "pipe", "pipeline"):
        if hasattr(clf, cand):
            monkeypatch.setattr(clf, cand, boom, raising=True)
            break
    res = _call(clf, "hi")
    assert isinstance(res, (tuple, list)) and len(res) >= 1


def test_pipe_odd_shapes(monkeypatch):
    clf = _new_ic()
    # 形狀一：dict 缺鍵
    monkeypatch.setattr(clf, "pipe", lambda _: {"weird": 1}, raising=False)
    res1 = _call(clf, "x")
    assert isinstance(res1, (tuple, list))
    # 形狀二：list[dict] 但鍵不同
    monkeypatch.setattr(clf, "pipe", lambda _: [{"predicted_label": "其他"}], raising=False)
    res2 = _call(clf, "x")
    assert isinstance(res2, (tuple, list))
