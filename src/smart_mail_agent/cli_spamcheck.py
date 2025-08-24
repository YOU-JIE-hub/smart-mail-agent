from __future__ import annotations

import argparse
import json
import os

from smart_mail_agent.spam_filter import SpamFilterOrchestrator


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="cli_spamcheck.py")
    p.add_argument("--subject", default="", help="Subject")
    p.add_argument("--content", default="", help="Body/content")
    p.add_argument("--sender", default="", help="From email")
    p.add_argument("--threshold", type=float, default=None)
    p.add_argument("--explain", action="store_true")
    ns = p.parse_args(argv)

    thr = ns.threshold if ns.threshold is not None else float(os.getenv("SMA_SPAM_THRESHOLD", "0.5"))
    sf = SpamFilterOrchestrator(default_threshold=thr)
    result = sf.is_legit(ns.subject, ns.content, ns.sender)
    # 補上分數/門檻輸出
    score, reasons = sf._score(ns.subject, ns.content, ns.sender)
    out = {"score": score, "threshold": thr, "is_spam": result["is_spam"], "reasons": reasons}
    if ns.explain:
        out["explain"] = reasons[:] or ["no_rule_matched"]
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
