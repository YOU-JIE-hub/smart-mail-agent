#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
from typing import List, Tuple

_SPAM_WORDS = re.compile(
    r"\b(free|viagra|bonus|limited\s*offer|lottery|winner|bitcoin|usdt)\b", re.I
)
_ZH_SPAM_WORDS = re.compile(r"(限時|優惠|免費|加碼|中獎|抽獎|比特幣|投資|博弈)", re.I)
_SHORTLINK = re.compile(r"(bit\.ly|t\.co|tinyurl\.com|goo\.gl|is\.gd|ow\.ly|t\.ly|cut\.ly)", re.I)
_MONEY = re.compile(r"(\$|\b\d{1,3}(,\d{3})*(\.\d+)?\b\s*(usd|美元|台幣|twd)?)", re.I)
_SUS_TLD = re.compile(r"\.(tk|top|xyz)(/|$)", re.I)


def _heuristics(subject: str, content: str, sender: str) -> Tuple[float, List[str]]:
    text = f"{subject or ''} {content or ''}".strip()
    reasons: List[str] = []
    score = 0.0

    if not text:
        return 0.0, ["empty"]

    if _SPAM_WORDS.search(text):
        score += 0.4
        reasons.append("spam_words")
    if _ZH_SPAM_WORDS.search(text):
        score += 0.4
        reasons.append("zh_keywords")
    if _SHORTLINK.search(text):
        score += 0.3
        reasons.append("shortlink")
    if _MONEY.search(text):
        score += 0.2
        reasons.append("money")
    if _SUS_TLD.search(text):
        score += 0.2
        reasons.append("suspicious_tld")

    if sender and sender.lower().endswith((".tk", ".top", ".xyz")):
        score += 0.2
        reasons.append("sender_tld")

    return min(score, 0.98), reasons


def _rules_score(subject: str, content: str, sender: str) -> Tuple[float, List[str]]:
    try:
        from smart_mail_agent.spam.rules import label_email  # type: ignore

        info = {
            "subject": subject or "",
            "text": content or "",
            "from": sender or "",
            "attachments": [],
            "links": [],
        }
        r = label_email(info)
        sc = float(r.get("score", 0.0))
        reasons = [str(x) for x in (r.get("reasons") or [])]
        if sc < 0.0:
            sc = 0.0
        if sc > 0.98:
            sc = 0.98
        return sc, reasons or (["rules"] if sc > 0 else [])
    except Exception:
        return 0.0, []


def _score(subject: str, content: str, sender: str) -> Tuple[float, List[str]]:
    s1, r1 = _heuristics(subject, content, sender)
    s2, r2 = _rules_score(subject, content, sender)
    reasons: List[str] = []
    for tag in r1 + r2:
        if tag not in reasons:
            reasons.append(tag)
    return max(s1, s2), reasons


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Smart Mail Agent - spam quick checker (JSON output)")
    p.add_argument("--subject", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--sender", required=True)
    p.add_argument("--threshold", type=float, default=0.8)
    p.add_argument("--explain", action="store_true", help="include 'explain' list in JSON")
    return p


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    score, reasons = _score(args.subject, args.content, args.sender)
    is_spam = bool(score >= float(args.threshold))
    payload = {"is_spam": is_spam, "score": round(score, 3)}
    if args.explain:
        payload["explain"] = reasons
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
