#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, sys
from typing import List, Tuple

_SPAM_WORDS = re.compile(r"\b(free|viagra|bonus|limited\s*offer)\b", re.I)
_SHORTLINK = re.compile(r"(bit\.ly|t\.co|tinyurl\.com|goo\.gl|is\.gd|ow\.ly|t\.ly|cut\.ly)", re.I)
_MONEY = re.compile(r"(\$|\d+\s?(usd|美元|台幣|twd))", re.I)

def _score(subject: str, content: str, sender: str) -> Tuple[float, List[str]]:
    text = f"{subject or ''} {content or ''}"
    reasons: List[str] = []
    score = 0.0

    if not text.strip():
        # 空內容當 ham 提示
        return 0.0, ["empty"]

    if _SPAM_WORDS.search(text):
        score = max(score, 1.0); reasons.append("spam_words")
    if _SHORTLINK.search(text):
        score = max(score, 1.0); reasons.append("shortlink")
    if _MONEY.search(text):
        score = max(score, 1.0); reasons.append("money")

    return min(score, 1.0), reasons or ["heuristics"]

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cli_spamcheck.py")
    p.add_argument("--subject", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--sender", default="")
    # threshold: 預設 0.5，支援環境變數覆寫
    default_thr = float(os.getenv("SPAM_THRESHOLD", "0.5"))
    p.add_argument("--threshold", type=float, default=default_thr)
    # explain: 是否輸出 reasons
    p.add_argument("--explain", action="store_true")
    return p

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    score, reasons = _score(args.subject, args.content, args.sender)
    is_spam = bool(score >= float(args.threshold))

    payload = {"is_spam": is_spam, "score": round(float(score), 3)}
    if args.explain:
        payload["reasons"] = reasons

    # 一律 stdout 印 JSON，並以 0 結束（測試用 check_output）
    print(json.dumps(payload, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
