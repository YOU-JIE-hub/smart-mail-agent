#!/usr/bin/env python3
from __future__ import annotations
import sys, json, argparse, importlib, os

DANGEROUS_EXTS = (".exe",".bat",".cmd",".scr",".js",".vbs",".msi",".com",".jar",".ps1")

def _parse_args(argv: list[str]):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true", default=False)
    ns, _ = ap.parse_known_args(argv[1:])
    return ns

def _need_review(payload: dict) -> bool:
    atts = payload.get("attachments") or []
    for a in atts:
        name = str(a.get("filename") or "")
        mime = str(a.get("mime") or "")
        lname = name.lower()
        # 1) 雙副檔名且以可執行結尾
        if lname.count(".") >= 2 and lname.endswith(DANGEROUS_EXTS):
            return True
        # 2) 檔名過長
        if len(name) >= 120:
            return True
        # 3) PDF 副檔名但 MIME 非 application/pdf
        if lname.endswith(".pdf") and not mime.startswith("application/pdf"):
            return True
    return False

def _fallback(ns, argv: list[str]) -> int:
    # 最小處理：讀 input 寫 output，並補 meta 與 require_review
    with open(ns.input, "r", encoding="utf-8") as f:
        payload = json.load(f)
    out = dict(payload)
    meta = dict(out.get("meta") or {})
    meta.setdefault("request_id", os.urandom(6).hex())
    meta.setdefault("duration_ms", 0)
    meta["dry_run"] = bool(ns.dry_run)
    meta.setdefault("require_review", _need_review(payload))
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
        # 底層若有寫出結果，就在其基礎上補 meta.require_review
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
        if "require_review" not in meta:
            meta["require_review"] = _need_review(payload_in)
        meta.setdefault("dry_run", bool(ns.dry_run))
        out["meta"] = meta
        with open(ns.output, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        return int(ret or 0)
    except Exception:
        # 委派失敗則走保底
        return _fallback(ns, argv)

if __name__ == "__main__":
    raise SystemExit(main())
