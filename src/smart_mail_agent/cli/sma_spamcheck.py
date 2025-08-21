#!/usr/bin/env python3
# 檔案位置: src/smart_mail_agent/cli/sma_spamcheck.py
# 模組用途: 輕量關鍵詞式 Spam Score CLI（維持舊介面：_score, build_parser, main）
from __future__ import annotations

import argparse
import re
from typing import List, Tuple

_SPAM_WORDS = re.compile(r"(free money|lottery|prize|winner|claim now|bitcoin|usdt)", re.I)
_ZH_SPAM_WORDS = re.compile(r"(免費|中獎|贏家|點此|限時|比特幣|USDT|投資|博弈)")
_SHORTLINK = re.compile(r"(bit\.ly|goo\.gl|t\.co|tinyurl\.com)", re.I)
_MONEY = re.compile(r"(\$|USD|NT\$|NTD|\d{1,3}(,\d{3})+)")

def _score(text: str) -> Tuple[float, List[str]]:
    explain: List[str] = []
    score = 0.0
    if _SPAM_WORDS.search(text):
        score += 0.6
        explain.append("spam_words")
    if _ZH_SPAM_WORDS.search(text):
        score += 0.6
        explain.append("zh_keywords")
    if _SHORTLINK.search(text):
        score += 0.4
        explain.append("shortlink")
    if _MONEY.search(text):
        score += 0.4
        explain.append("money")
    if score > 0.98:
        score = 0.98
    return score, explain

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Lightweight spam score checker")
    p.add_argument("--subject", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--threshold", type=float, default=0.8)
    return p

def main() -> int:
    args = build_parser().parse_args()
    text = f"{args.subject}\n{args.content}"
    score, explain = _score(text)
    print(f"score={score:.2f} tags={','.join(explain)}")
    return 0 if score < args.threshold else 1

if __name__ == "__main__":
    raise SystemExit(main())
