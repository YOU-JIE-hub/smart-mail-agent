#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys, pathlib

def _decide_action(label: str) -> str:
    m = {
        "sales": "sales_inquiry",
        "send_quote": "send_quote",
        "quotation": "send_quote",
        "complaint": "complaint",
    }
    key = (label or "").strip().lower()
    return m.get(key, key or "unknown")

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--simulate-failure", action="store_true")
    args = p.parse_args(argv)

    inp = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
    label = inp.get("predicted_label") or inp.get("label") or "unknown"
    action = _decide_action(label)

    meta = {"dry_run": bool(args.dry_run)}
    out = {
        "action_name": action,
        "meta": meta,
        "attachments": [],
    }

    # 情境：大附件 -> 需要人工
    def _has_big_attachment(msg: dict, threshold: int = 5 * 1024 * 1024) -> bool:
        for a in msg.get("attachments", []) or []:
            try:
                if int(a.get("size", 0)) >= threshold:
                    return True
            except Exception:
                pass
        return False

    # simulate-failure -> 必須人工 + 加 cc + 產出 .txt 說明
    if args.simulate_failure:
        meta["simulate_failure"] = True
        meta["require_review"] = True
        meta["needs_manual"] = True
        meta["cc"] = ["support@company.example"]
        out["attachments"].append(
            {"filename": "analysis.txt", "content": "simulate-failure: capture for review"}
        )

    # label 影響：complaint -> P1 + SLA
    if action == "complaint":
        meta["priority"] = "P1"
        meta.setdefault("SLA_eta", "4h")

    # send_quote + 大附件 -> 需要人工（並補一份 .txt）
    if action == "send_quote" and _has_big_attachment(inp):
        meta["needs_manual"] = True
        if not any((a.get("filename","").endswith(".txt")) for a in out["attachments"]):
            out["attachments"].append(
                {"filename": "note.txt", "content": "large attachment detected"}
            )

    pathlib.Path(args.output).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
