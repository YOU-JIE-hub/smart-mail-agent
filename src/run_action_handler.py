#!/usr/bin/env python3
from __future__ import annotations
import sys, json, argparse, importlib, os
from typing import List, Dict, Any

DANGEROUS_EXTS = (".exe",".bat",".cmd",".scr",".js",".vbs",".msi",".com",".jar",".ps1")
SUPPORT_CC = os.getenv("SMA_SUPPORT_CC", "support@company.example")

def _parse_args(argv: list[str]):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true", default=False)
    ns, _ = ap.parse_known_args(argv[1:])
    return ns

def _analyze_risks(payload: Dict[str, Any]) -> List[str]:
    risks: List[str] = []
    atts = payload.get("attachments") or []
    for a in atts:
        name = str(a.get("filename") or "")
        mime = str(a.get("mime") or "")
        lname = name.lower()
        if lname.count(".") >= 2 and lname.endswith(DANGEROUS_EXTS):
            risks.append("attach:double_ext")
        if len(name) >= 120:
            risks.append("attach:long_name")
        if lname.endswith(".pdf") and not mime.startswith("application/pdf"):
            risks.append("attach:mime_mismatch")
    return risks

def _fallback(ns, argv: list[str]) -> int:
    with open(ns.input, "r", encoding="utf-8") as f:
        payload = json.load(f)
    out = dict(payload)
    meta = dict(out.get("meta") or {})
    risks = _analyze_risks(payload)

    meta.setdefault("request_id", os.urandom(6).hex())
    meta.setdefault("duration_ms", 0)
    meta["dry_run"] = bool(ns.dry_run)
    meta["risks"] = sorted(set(list(meta.get("risks") or []) + risks))
    meta["require_review"] = bool(meta["risks"])

    cc = list(meta.get("cc") or [])
    if meta["require_review"] and SUPPORT_CC not in cc:
        cc.append(SUPPORT_CC)
    meta["cc"] = cc

    out["meta"] = meta
    with open(ns.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    return 0

def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    ns = _parse_args(argv)
    try:
        ra = importlib.import_module("smart_mail_agent.routing.run_action_handler")
        called = False
        ret = 0
        for name in ("main", "cli", "run"):
            fn = getattr(ra, name, None)
            if callable(fn):
                try:
                    ret = fn(argv)
                except TypeError:
                    ret = fn()
                called = True
                break
        if not called:
            return _fallback(ns, argv)

        # 讀回輸出做補強（union risks、設定 require_review、附帶 cc）
        try:
            with open(ns.input, "r", encoding="utf-8") as f:
                payload_in = json.load(f)
        except Exception:
            payload_in = {}
        try:
            with open(ns.output, "r", encoding="utf-8") as f:
                out = json.load(f)
        except FileNotFoundError:
            return _fallback(ns, argv)

        meta = dict(out.get("meta") or {})
        existing = list(meta.get("risks") or [])
        add = _analyze_risks(payload_in)
        meta["risks"] = sorted(set(existing + add))
        meta.setdefault("dry_run", bool(ns.dry_run))
        meta["require_review"] = bool(meta["risks"])

        cc = list(meta.get("cc") or [])
        if meta["require_review"] and SUPPORT_CC not in cc:
            cc.append(SUPPORT_CC)
        meta["cc"] = cc

        out["meta"] = meta
        with open(ns.output, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        return int(ret or 0)
    except Exception:
        return _fallback(ns, argv)

if __name__ == "__main__":
    raise SystemExit(main())
