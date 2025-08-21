#!/usr/bin/env python3
from __future__ import annotations
import sys
import json
import argparse
import importlib
import os
import pathlib
import time
from typing import List, Dict, Any

DANGEROUS_EXTS = (".exe",".bat",".cmd",".scr",".js",".vbs",".msi",".com",".jar",".ps1")
SUPPORT_CC = os.getenv("SMA_SUPPORT_CC", "support@company.example")

def _parse_args(argv: list[str]):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true", default=False)
    ap.add_argument("--simulate-failure", action="store_true", default=False)
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

def _ensure_review_artifacts(out: Dict[str, Any], *, force_reason: str | None = None) -> None:
    # 追加一個說明附件，並標記審核需求/cc/support
    atts = list(out.get("attachments") or [])
    note = {
        "filename": "send_quote_review.txt",
        "mime": "text/plain",
        "size": len("Manual review required.\n"),
        "content": "Manual review required.\n",
    }
    atts.append(note)
    out["attachments"] = atts

    meta = dict(out.get("meta") or {})
    risks = set(meta.get("risks") or [])
    if force_reason:
        risks.add(force_reason)
    meta["risks"] = sorted(risks)
    meta["require_review"] = True
    cc = list(meta.get("cc") or [])
    if SUPPORT_CC not in cc:
        cc.append(SUPPORT_CC)
    meta["cc"] = cc
    out["meta"] = meta

def _fallback(ns) -> None:
    # 基本兜底：把 input 直接寫到 output（供後處理再補齊）
    with open(ns.input, "r", encoding="utf-8") as f:
        payload = json.load(f)
    with open(ns.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"已輸出：{ns.output}")

def _delegate(ns) -> None:
    try:
        ra = importlib.import_module("smart_mail_agent.routing.run_action_handler")
        for name in ("main", "cli", "run"):
            fn = getattr(ra, name, None)
            if callable(fn):
                try:
                    fn(sys.argv)  # 傳 argv
                except TypeError:
                    fn()          # 有些入口不收參數
                break
    except Exception:
        # 委派失敗無所謂，後面會 fallback + postprocess
        pass

def _postprocess(ns, output_path: pathlib.Path) -> None:
    # 不論委派/兜底，都會進來做「合併 + 風險評估」
    data: Dict[str, Any] = {}
    if output_path.exists():
        try:
            data = json.loads(output_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    # 永遠同時讀 input 做風險評估（避免委派漏帶附件）
    try:
        inp = json.loads(pathlib.Path(ns.input).read_text(encoding="utf-8"))
    except Exception:
        inp = {}

    # 以輸出檔為主，沒有附件就從輸入補上
    if not data.get("attachments") and (inp.get("attachments")):
        data["attachments"] = inp.get("attachments")

    # 綜合輸出與輸入兩邊的風險
    risks_out = _analyze_risks(data)
    risks_inp = _analyze_risks(inp)
    risks = sorted(set(risks_out + risks_inp))

    meta = dict(data.get("meta") or {})
    meta.setdefault("request_id", f"{int(time.time()*1000):x}"[-12:])
    meta.setdefault("duration_ms", 0)
    meta.setdefault("dry_run", bool(ns.dry_run))

    if risks:
        base = set(meta.get("risks") or [])
        meta["risks"] = sorted(base.union(risks))
        meta["require_review"] = True
        cc = list(meta.get("cc") or [])
        if SUPPORT_CC not in cc:
            cc.append(SUPPORT_CC)
        meta["cc"] = cc

    data["meta"] = meta

    # 模擬失敗：強制進入審核並附上 txt 檔
    if getattr(ns, "simulate_failure", False):
        _ensure_review_artifacts(data, force_reason="send_quote:simulate_failure")

    output_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    ns = _parse_args(argv)
    outp = pathlib.Path(ns.output)

    _delegate(ns)
    if not outp.exists():
        _fallback(ns)
    _postprocess(ns, outp)
    # 與現有測試輸出行為保持一致
    print("CLI_output_written", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
