from __future__ import annotations
import argparse, json, sys
from .spam_filter import SpamFilterOrchestrator

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--subject", default="")
    p.add_argument("--content", default="")
    p.add_argument("--sender", default="")
    p.add_argument("--threshold", type=float, default=None)
    p.add_argument("--explain", action="store_true")
    ns = p.parse_args(argv)
    sf = SpamFilterOrchestrator(threshold=ns.threshold)
    res = sf.is_legit(subject=ns.subject, content=ns.content, sender=ns.sender)
    if ns.explain:
        res["explain"] = list(res.get("reasons", []))
    print(json.dumps(res, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
