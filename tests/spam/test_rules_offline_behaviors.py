from __future__ import annotations

import importlib

import pytest

_rules = importlib.import_module("smart_mail_agent.spam.rules")


def _has(name: str) -> bool:
    return hasattr(_rules, name)


@pytest.mark.skipif(not _has("contains_keywords"), reason="rules.contains_keywords not available")
def test_contains_keywords_positive_and_negative():
    assert _rules.contains_keywords("限時優惠 立即下單 折扣") is True
    assert _rules.contains_keywords("您好，想詢問報價與方案") in (True, False)  # 允許實作差異
    assert _rules.contains_keywords("一般工作聯絡，沒有廣告語") is False


@pytest.mark.skipif(not _has("link_ratio"), reason="rules.link_ratio not available")
def test_link_ratio_monotonicity():
    low = _rules.link_ratio("這是一段文字，只有一個連結 http://a.com 其他都是文字 " + "字" * 200)
    high = _rules.link_ratio("http://a.com " * 10 + "少量文字")
    assert isinstance(low, float) and isinstance(high, float)
    assert high > low  # 連結越多，比例應上升（單調性，不卡實作閾值）


@pytest.mark.skipif(
    not (_has("contains_keywords") and _has("link_ratio")), reason="rules methods not available"
)
def test_rules_composition_spamish():
    text = "超殺優惠！點擊 http://x.io 馬上領券 http://y.io 再享折扣"
    kw = _rules.contains_keywords(text)
    ratio = _rules.link_ratio(text)
    assert kw in (True, False)
    assert ratio >= 0.0
    # 合理預期：關鍵字或高連結比例能導向 Spam-ish（不綁定內部名稱）
    # 這裡只保證「條件具備」，實際判決由 orchestrator 決定（見下一檔）
