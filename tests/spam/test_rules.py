#!/usr/bin/env python3
# 檔案位置: tests/spam/test_rules.py
# 測試用途: 覆蓋 contains_keywords 與 link_ratio 的常見與邊界行為

from __future__ import annotations

from smart_mail_agent.spam.rules import contains_keywords, link_ratio


def test_contains_keywords_basic_case_insensitive_chinese():
    s = "恭喜您中獎，點此連結即可領取獎金"
    assert contains_keywords(s, ["中獎", "免費"])


def test_contains_keywords_basic_case_insensitive_english():
    s = "Please CLICK HERE to claim your reward."
    assert contains_keywords(s, ["click here"])


def test_contains_keywords_word_boundary_english():
    s = "The PRICELIST is ready."
    # 開啟詞邊界，"price" 不應命中 "pricelist"
    assert not contains_keywords(s, ["price"], match_word_boundary=True)
    # 關閉詞邊界，會命中
    assert contains_keywords(s, ["price"], match_word_boundary=False)


def test_link_ratio_plain_text_zero():
    s = "這是一段純文字，沒有任何連結。"
    assert link_ratio(s) == 0.0


def test_link_ratio_simple_html_between_0_and_1():
    s = '<p>看看這裡 <a href="https://example.com">點此</a> 了解詳情。</p>'
    r = link_ratio(s)
    assert 0.0 < r < 1.0


def test_link_ratio_many_links_high_ratio():
    s = """
    <div>
      <a href="#">免費</a>
      <a href="#">中獎</a>
      <a href="#">點此連結</a>
      <span>少量非連結文字</span>
    </div>
    """
    r = link_ratio(s)
    assert r > 0.4  # 多數可見文字在連結錨文字內


def test_link_ratio_edge_non_html_and_empty():
    assert link_ratio(None) == 0.0  # type: ignore[arg-type]
    assert link_ratio("") == 0.0
    assert 0.0 <= link_ratio("<a>  </a>") <= 1.0
