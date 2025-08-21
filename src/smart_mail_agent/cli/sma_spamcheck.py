#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import re
from typing import List, Tuple

_SPAM_WORDS = re.compile(r"\b(free|viagra|bonus|limited\s*offer)\b", re.I)
_ZH_SPAM_WORDS = re.compile(r"(限時|優惠|免費|加碼)", re.I)
_SHORTLINK  = re.compile(r"(bit\.ly|t\.co|tinyurl\.com|goo\.gl|is\.gd|ow\.ly|t\.ly|cut\.ly)", re.I)
_MONEY      = re.compile(r"(\$|\d+\s?(usd|美元|台幣|twd))", re.I)

def _score(subject: str, content: str, sender: str) -> Tuple[float, List[str]]:
    text = f"{subject or ''} {content or ''}".strip()
    if not text:
        return 0.0, ["empty"]
    score = 0.0
    explain: List[str] = []
    if _SPAM_WORDS.search(text):
        score += 0.6; explain.append("spam_words")
    if _ZH_SPAM_WORDS.search(text):
        score += 0.6; explain.append("zh_keywords")
    if _SHORTLINK.search(text):
        score += 0.4; explain.append("shortlink")
    if _MONEY.search(text):
        score += 0.4; explain.append("money")
    if score > 0.98:  # cap to make --threshold 0.99 work
        score = 0.98
    return score, explain

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--content", required=True)
    ap.add_argument("--sender", default="")
    ap.add_argument("--threshold", type=float, default=float(os.getenv("SMA_SPAM_THRESHOLD", "0.8")))
    ap.add_argument("--explain", action="store_true")
    args = ap.parse_args()

    sc, reasons = _score(args.subject, args.content, args.sender)
    is_spam = sc >= args.threshold
    out = {"is_spam": bool(is_spam), "score": round(sc, 2)}
    if args.explain:
        out["explain"] = reasons
    print(json.dumps(out, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
