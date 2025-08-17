from __future__ import annotations

import argparse
import json
import os
import re
from collections.abc import Iterable

# 高訊號關鍵字（單獨命中就可觀）
STRONG_WORDS: tuple[str, ...] = (
    # en
    "free",
    "bonus",
    "win",
    "prize",
    "buy now",
    "act now",
    "urgent",
    "guarantee",
    "risk-free",
    "cash",
    "crypto",
    "investment",
    "lottery",
    "casino",
    "sex",
    "viagra",
    "rx",
    # zh
    "免費",
    "中獎",
    "成人",
    "博彩",
    "加密",
)

# 低訊號關鍵字（需搭配連結/金額才像垃圾）
WEAK_WORDS: tuple[str, ...] = (
    # en
    "offer",
    "limited",
    "deal",
    "discount",
    "sale",
    "promotion",
    "reward",
    "gift",
    "award",
    "subscribe",
    "click",
    # zh
    "限時",
    "優惠",
    "折扣",
    "點擊",
)

# 常見短網址與連結線索
URL_HINTS: tuple[str, ...] = (
    "http://",
    "https://",
    "bit.ly",
    "tinyurl",
    "goo.gl",
    "t.co",
    "is.gd",
)

# 金額線索
MONEY_RE = re.compile(r"(?:usd|ntd|新台幣|\$)\s*\d", re.I)

# 可由環境變數覆寫的權重與門檻
DEFAULT_THRESHOLD = float(os.getenv("SMA_THRESHOLD", "0.5"))
URL_WEIGHT = float(os.getenv("SMA_URL_WEIGHT", "0.40"))
STRONG_WEIGHT = float(os.getenv("SMA_STRONG_WEIGHT", "0.35"))
STRONG_BONUS = float(os.getenv("SMA_STRONG_BONUS", "0.10"))  # 強字 + (url|money) 額外加分
WEAK_WEIGHT = float(os.getenv("SMA_WEAK_WEIGHT", "0.20"))
MONEY_WEIGHT = float(os.getenv("SMA_MONEY_WEIGHT", "0.25"))


def _hits(text: str, needles: Iterable[str]) -> list[str]:
    t = text.lower()
    return [kw for kw in needles if kw in t]


def _score(
    subject: str, content: str, sender: str, *, want_explain: bool = False
) -> tuple[float, list[str]]:
    text = " ".join([subject or "", content or "", sender or ""])
    t = text.lower()
    reasons: list[str] = []

    strong = _hits(t, STRONG_WORDS)
    weak = _hits(t, WEAK_WORDS)
    url_hits = [h for h in URL_HINTS if h in t]
    money = bool(MONEY_RE.search(text))

    score = 0.0
    if strong:
        score += STRONG_WEIGHT
        if want_explain:
            reasons.append(f"strong keywords: {', '.join(strong)} (+{STRONG_WEIGHT:.2f})")
    if weak:
        score += WEAK_WEIGHT
        if want_explain:
            reasons.append(f"weak keywords: {', '.join(weak)} (+{WEAK_WEIGHT:.2f})")
    if url_hits:
        score += URL_WEIGHT
        if want_explain:
            reasons.append(f"url/shortlink: {', '.join(sorted(set(url_hits)))} (+{URL_WEIGHT:.2f})")
    if money:
        score += MONEY_WEIGHT
        if want_explain:
            reasons.append(f"mentions money (+{MONEY_WEIGHT:.2f})")
    if strong and (url_hits or money):
        score += STRONG_BONUS
        if want_explain:
            reasons.append(f"strong + (url|money) combo (+{STRONG_BONUS:.2f})")

    score = min(score, 0.99)
    return score, reasons


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--subject", default="")
    p.add_argument("--content", default="")
    p.add_argument("--sender", default="")
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    p.add_argument("--explain", action="store_true")
    args = p.parse_args(argv)

    score, reasons = _score(args.subject, args.content, args.sender, want_explain=args.explain)
    is_spam = score >= args.threshold

    payload = {
        "subject": args.subject,
        "sender": args.sender,
        "score": round(score, 2),
        "is_spam": is_spam,
        "engine": "heuristic-v0",
    }
    if args.explain:
        payload["explain"] = reasons

    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
