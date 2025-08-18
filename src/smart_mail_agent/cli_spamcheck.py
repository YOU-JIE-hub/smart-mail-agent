from __future__ import annotations
import argparse, json, os, sys
from .spam import rules

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--subject", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--sender", default="")
    p.add_argument("--threshold", type=float, default=float(os.getenv("SPAM_THRESHOLD", "0.5")))
    p.add_argument("--explain", action="store_true")
    args = p.parse_args(argv)

    subj, cont = args.subject or "", args.content or ""
    if not subj and not cont:
        out = {"is_spam": False, "score": 0.0, "explain": [] if args.explain else None}
        print(json.dumps(out, ensure_ascii=False))
        return 0

    res = rules.label_email({"subject": subj, "content": cont, "attachments": []})
    is_spam = bool(res["score"] >= args.threshold)
    out = {"is_spam": is_spam, "score": float(res["score"])}
    if args.explain:
        out["explain"] = res.get("reasons", [])
        out["reasons"] = res.get("reasons", [])
    else:
        out["reasons"] = res.get("reasons", [])
    print(json.dumps(out, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
