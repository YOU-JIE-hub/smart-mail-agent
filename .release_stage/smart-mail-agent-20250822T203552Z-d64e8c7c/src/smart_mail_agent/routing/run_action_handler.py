#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
from typing import Any, Dict, List
from datetime import datetime

# --- constants ---------------------------------------------------------------
DEFAULT_CC_P1 = ["qa@company.example", "ops@company.example"]
PASS_THROUGH = {"reply_faq", "send_quote", "complaint", "sales_inquiry"}

# --- helpers: attachment risks ----------------------------------------------
def _attachment_risks(att: Dict[str, Any]) -> List[str]:
    risks: List[str] = []
    fn = (att.get("filename") or "")
    mime = (att.get("mime") or "").lower()
    size = int(att.get("size") or 0)
    if fn.count(".") >= 2:
        risks.append("attach:double_ext")
    if len(fn) > 120:
        risks.append("attach:long_name")
    if fn.lower().endswith(".pdf") and not mime.startswith("application/pdf"):
        risks.append("attach:mime_mismatch")
    # 可保留：過大附件（目前測試未檢查）
    if size > 5 * 1024 * 1024:
        risks.append("attach:too_large")
    return risks

def _gather_risks(atts: List[Dict[str, Any]] | None) -> List[str]:
    out: List[str] = []
    for a in (atts or []):
        out.extend(_attachment_risks(a))
    return sorted(set(out))

# --- helpers: policy & whitelist --------------------------------------------
def _complaint_policy(label: str, subject: str, body: str) -> Dict[str, Any]:
    text = f"{subject} {body}".lower()
    tokens = ["down", "當機", "無法使用", "影響交易", "critical", "重大", "緊急"]
    if label == "complaint" and any(t in text for t in tokens):
        return {"priority": "P1", "SLA_eta": "4h", "cc": list(DEFAULT_CC_P1), "next_step": "escalate_p1"}
    return {"priority": "P3", "SLA_eta": "24h", "cc": [], "next_step": "route_to_normal_queue"}

def _domain_in_allowlist(sender: str) -> bool:
    doms = os.getenv("WHITELIST_DOMAINS", "trusted.example")
    allow = {d.strip().lower() for d in doms.split(",") if d.strip()}
    try:
        domain = sender.split("@", 1)[1].lower()
    except Exception:
        domain = ""
    return domain in allow

# --- io ---------------------------------------------------------------------
def _read_payload(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- cli/main ---------------------------------------------------------------
def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", "--input", dest="input", required=True)
    p.add_argument("--out", dest="output")
    p.add_argument("--output", dest="output")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--simulate-failure", nargs="?", const="true")
    p.add_argument("--policy", choices=["whitelist", "default"], default=None)
    p.add_argument("--whitelist", action="store_true")
    args = p.parse_args(argv)

    payload = _read_payload(args.input)
    label = payload.get("predicted_label") or "other"
    subject_in = payload.get("subject") or ""
    body_in = payload.get("body") or ""
    sender = payload.get("from") or ""
    attachments = payload.get("attachments") or []

    # 1) 附件風險與審核
    risks = _gather_risks(attachments)
    require_review = bool(risks)
    extra_cc: List[str] = []
    if any(r in {"attach:double_ext","attach:long_name","attach:mime_mismatch"} for r in risks):
        extra_cc.append("support@company.example")

    # 2) 投訴策略
    pol = _complaint_policy(label, subject_in, body_in)
    cc_merged = sorted(set((pol.get("cc") or []) + extra_cc))

    # 3) 主旨前綴
    if label in ("reply_faq", "sales_inquiry", "complaint"):
        base_map = {"reply_faq": "常見問題", "sales_inquiry": "銷售洽談", "complaint": "投訴"}
        base = base_map[label]
        subject_out = f"[自動回覆] {subject_in}" if subject_in else f"[自動回覆] {base}"
    else:
        subject_out = subject_in

    # 4) 白名單策略啟用（旗標／環境／位置參數 + 寄件網域）
    argv_list = argv if argv is not None else sys.argv[1:]
    positional_flag = "whitelist" in argv_list
    policy = "whitelist" if (
        args.whitelist or args.policy == "whitelist" or
        os.getenv("POLICY") == "whitelist" or positional_flag
    ) else (args.policy or "default")
    whitelisted = (_domain_in_allowlist(sender) or policy == "whitelist")

    # 5) sales_inquiry：產 MD 並設定 next_step
    sales_extra_attachments: List[Dict[str, Any]] = []
    if label == "sales_inquiry":
        fname = f"needs_summary_{datetime.utcnow().strftime('%Y%m%d')}.md"
        md = f"# 銷售需求摘要\\n\\n**Subject:** {subject_in}\\n\\n**Body:** {body_in}\\n"
        sales_extra_attachments.append({
            "filename": fname, "mime": "text/markdown", "size": len(md)
        })
        pol["next_step"] = "prepare_sales_summary"

    # 6) 模擬失敗
    warnings: List[str] = []
    simulate_type: str | None = None
    if args.simulate_failure:
        val = args.simulate_failure.lower() if isinstance(args.simulate_failure, str) else "true"
        if val in ("pdf", "true", "1", "yes"):
            simulate_type = "pdf" if val == "pdf" else "generic"
            warnings.append("simulated_pdf_failure" if simulate_type == "pdf" else "simulated_failure")

    # 7) 組輸出
    meta = {
        "risks": risks,
        "require_review": require_review,
        "dry_run": bool(args.dry_run),
        "simulate_failure": ("pdf" if simulate_type == "pdf" else False) if simulate_type else False,
        "priority": pol["priority"],
        "SLA_eta": pol["SLA_eta"],
        "cc": cc_merged,
        "next_step": pol["next_step"],
        "whitelisted": whitelisted,
    }
    action_name = label if label in PASS_THROUGH else ("reply_general" if label == "other" else label)
    out = {
        "action_name": action_name,
        "status": "ok",
        "meta": meta,
        "attachments": (attachments + sales_extra_attachments),
        "warnings": warnings,
        "cc": cc_merged,
        "subject": subject_out,
        # 頂層鏡射
        "dry_run": bool(args.dry_run),
        "simulate_failure": bool(simulate_type),
        "simulate_type": simulate_type or "",
    }

    out_path = args.output or payload.get("output")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
    else:
        print(json.dumps(out, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

