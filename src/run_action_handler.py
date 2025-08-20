#!/usr/bin/env python3
from __future__ import annotations
import sys, json, argparse, importlib, os
from typing import List, Dict, Any

DANGEROUS_EXTS = (".exe",".bat",".cmd",".scr",".js",".vbs",".msi",".com",".jar",".ps1")

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
        # 1) 雙副檔名且以可執行結尾
        if lname.count(".") >= 2 and lname.endswith(DANGEROUS_EXTS):
            risks.append("attach:double_ext")
        # 2) 檔名過長
        if len(name) >= 120:
            risks.append("attach:long_name")
        # 3) PDF 副檔名但 MIME 非 application/pdf
        if lname.endswith(".pdf") and not mime.startswith("application/pdf"):
            risks.append("attach:mime_mismatch")
    return risks

def _fallback(ns, argv: list[str]) -> int:
    # 最小處理：讀 input 寫 output，並補 meta/risks/require_review
    with open(ns.input, "r", encoding="utf-8") as f:
        payload = json.load(f)
    out = dict(payload)
    meta = dict(out.get("meta") or {})
    risks = _analyze_risks(payload)
    meta.setdefault("request_id", os.urandom(6).hex())
    meta.setdefault("duration_ms", 0)
    meta["dry_run"] = bool(ns.dry_run)
    meta["risks"] = sorted(set((meta.get("risks") or []) + risks))
    meta["require_review"] = bool(meta["risks"])
    out["meta"] = meta
    with open(ns.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    return 0

def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    ns = _parse_args(argv)
    # 先嘗試委派到底層套件入口
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

        # 補齊 meta 欄位與風險代碼（即便底層已輸出，也做 union）
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
        out["meta"] = meta
        with open(ns.output, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        return int(ret or 0)
    except Exception:
        # 委派失敗則走保底
        return _fallback(ns, argv)

if __name__ == "__main__":
    raise SystemExit(main())
