from __future__ import annotations

import argparse
import json


def _heuristic_spam_score(text: str) -> float:
    """極簡啟發式打分：命中常見垃圾字詞與可疑連結加分，分數上限 0.99。"""
    if not text:
        return 0.0

    lowers = text.lower()
    kws = [
        "free",
        "winner",
        "bitcoin",
        "viagra",
        "casino",
        "loan",
        "credit",
        "limited time",
        "act now",
        "click here",
        "獎",
        "中獎",
        "免費",
        "限時",
        "點擊",
        "投資",
        "加密",
        "博彩",
    ]

    score = 0.0
    for k in kws:
        if k in lowers:
            score += 0.08

    # 帶連結再加權
    if ("http://" in lowers) or ("https://" in lowers):
        score += 0.10

    return min(score, 0.99)


def check_spam(subject: str, content: str, sender: str | None) -> dict[str, object]:
    text = f"{subject or ''}\n{content or ''}\n{sender or ''}"
    score = _heuristic_spam_score(text)
    return {
        "subject": subject,
        "sender": sender,
        "score": round(score, 2),
        "is_spam": score >= 0.5,
        "engine": "heuristic-v1",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Simple spam score checker")
    p.add_argument("--subject", required=True, help="mail subject")
    p.add_argument("--content", required=True, help="mail content")
    p.add_argument("--sender", default=None, help="mail from (optional)")
    args = p.parse_args(argv)

    res = check_spam(args.subject, args.content, args.sender)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
