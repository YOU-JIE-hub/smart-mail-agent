from __future__ import annotations
import argparse, json, re, sys
from email.utils import parseaddr
from pathlib import Path
from typing import Any, Dict, List

DANGEROUS_EXTS = {".exe", ".js", ".bat", ".vbs", ".scr", ".cmd", ".ps1", ".jar"}
WHITELIST_DOMAINS = {"trusted.example"}

def _email_domain(addr: str) -> str:
    _, email = parseaddr(addr or "")
    if "@" in email:
        return email.split("@", 1)[1].lower()
    return ""

def _risks_for_attachment(a: dict) -> List[str]:
    risks: List[str] = []
    name = str(a.get("filename") or a.get("name") or "")
    mime = str(a.get("mime") or "")
    low = name.lower()
    if any(low.endswith(ext) for ext in DANGEROUS_EXTS):
        risks.append("attach:danger_ext")
    if ".pdf.exe" in low or ".xlsm.exe" in low:
        risks.append("attach:double_ext")
    if len(name) > 120:
        risks.append("attach:long_name")
    if low.endswith(".pdf") and mime and mime not in ("", "application/pdf"):
        risks.append("attach:mime_mismatch")
    if (a.get("size") or 0) > 5 * 1024 * 1024:
        risks.append("attach:oversize")
    return risks

def _decide_action_name_by_label(label: str) -> str:
    if label == "other":
        return "reply_general"
    return label

def _choose_action_runtime(label: str) -> str:
    mapping = {
        "send_quote": "reply_with_quote",
        "reply_faq": "reply_faq",
        "complaint": "escalate_case",
        "sales_inquiry": "reply_sales_summary",
        "other": "reply_general",
        "": "reply_general",
    }
    return mapping.get(label, "reply_general")

def _severity_priority(subject: str, body: str) -> str | None:
    txt = f"{subject} {body}"
    if re.search(r"(當機|無法使用|嚴重|down|故障)", txt, re.IGNORECASE):
        return "P1"
    if re.search(r"(錯誤|影響|延遲)", txt, re.IGNORECASE):
        return "P2"
    return None

def _sla_eta(priority: str | None) -> str | None:
    if priority == "P1":
        return "4h"
    if priority == "P2":
        return "8h"
    return None

def _safe_md_name(subject: str) -> str:
    base = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff_-]+", "_", subject or "note")
    return f"needs_summary_{base[:40]}.md"

def _action_for_payload(payload: Dict[str, Any], dry_run: bool, simulate: List[str] | None) -> Dict[str, Any]:
    label = str(payload.get("predicted_label") or payload.get("label") or "").lower()
    subject = str(payload.get("subject", ""))
    body = str(payload.get("body", ""))
    atts = payload.get("attachments") or []
    sender = str(payload.get("from") or payload.get("sender") or "")

    risks: List[str] = []
    for a in atts:
        if isinstance(a, dict):
            risks += _risks_for_attachment(a)
        else:
            risks += _risks_for_attachment({"filename": str(a)})

    warnings: List[str] = []
    meta: Dict[str, Any] = {"dry_run": bool(dry_run)}

    # --simulate-failure
    if simulate is not None:
        if len(simulate) == 0:
            risks.append("simulate:generic")
            warnings.append("simulated_generic_failure")
            meta["simulate_failure"] = "generic"
        else:
            for s in simulate:
                risks.append(f"simulate:{s}")
            if "pdf" in simulate:
                warnings.append("simulated_pdf_failure")
                meta["simulate_failure"] = "pdf"

    action_name = _decide_action_name_by_label(label)
    action_impl = _choose_action_runtime(label)

    # 主旨前綴：FAQ / sales_inquiry / complaint 皆需
    out_subject = subject
    if label in {"reply_faq", "sales_inquiry", "complaint"}:
        if not subject.startswith("[自動回覆] "):
            out_subject = "[自動回覆] " + subject

    # 白名單寄件者
    whitelisted = _email_domain(sender) in WHITELIST_DOMAINS

    # Priority（僅 complaint 評級）
    priority = _severity_priority(subject, body) if label == "complaint" else None
    if priority:
        meta["priority"] = priority
        eta = _sla_eta(priority)
        if eta:
            meta["SLA_eta"] = eta
        if priority == "P1":
            meta.setdefault("cc", []).extend(["qa@company.example", "ops@company.example"])
            # 高優先 P1 下一步：通知 oncall
            meta.setdefault("next_step", "page_oncall")

    # sales_inquiry 產出 .md 摘要附件 + 下一步提示
    out_attachments: List[Dict[str, Any]] = []
    if label == "sales_inquiry":
        out_attachments.append({"filename": _safe_md_name(subject)})
        meta["next_step"] = "review_summary_md"

    # simulate generic 產出 .txt 記錄檔
    if simulate is not None and not simulate:
        out_attachments.append({"filename": "simulated_error.txt"})

    # 有任何風險 -> 交人工審核；且若為附件風險，抄送安全小組
    action_final = "review" if risks else action_impl
    if any(r.startswith("attach:") for r in risks):
        meta.setdefault("cc", []).append("support@company.example")

    meta.update({
        "risks": sorted(set(risks)),
        "require_review": bool(risks),
        "whitelisted": bool(whitelisted),
    })

    out: Dict[str, Any] = {
        "dry_run": dry_run,
        "label": label,
        "action_name": action_name,
        "action": action_final,
        "subject": out_subject,
        "meta": meta,
    }
    if warnings:
        out["warnings"] = warnings
    if out_attachments:
        out["attachments"] = out_attachments
    return out

def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--simulate-failure", nargs="*", default=None)
    args = p.parse_args(argv)

    inp = Path(args.input)
    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)

    payload = json.loads(inp.read_text(encoding="utf-8"))
    res = _action_for_payload(payload, args.dry_run, args.simulate_failure)
    outp.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
