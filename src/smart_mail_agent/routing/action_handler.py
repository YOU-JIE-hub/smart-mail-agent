from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import argparse, json, os, tempfile, re
from smart_mail_agent.features.quotation import generate_pdf_quote, choose_package
from smart_mail_agent.utils.inference_classifier import IntentClassifier

# --- 風險判斷 ---
def _attachment_risks(att: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    fn = (att.get("filename") or "").lower()
    mime = (att.get("mime") or "").lower()
    size = int(att.get("size") or 0)
    # 雙重副檔名
    if re.search(r"\.(pdf|docx|xlsx|xlsm)\.[a-z0-9]{2,4}$", fn):
        reasons.append("double_ext")
    # 名稱過長
    if len(fn) > 120:
        reasons.append("name_too_long")
    # MIME 與副檔名常見不符
    if fn.endswith(".pdf") and mime not in ("application/pdf", ""):
        reasons.append("mime_mismatch")
    if size > 5 * 1024 * 1024:
        reasons.append("oversize")
    return reasons

def _ensure_attachment(title: str, lines: List[str]) -> str:
    # 產出一個最小 PDF
    with tempfile.NamedTemporaryFile(prefix="quote_", suffix=".pdf", delete=False) as tf:
        tf.write(b"%PDF-1.4\n%% Minimal\n%%EOF\n")
        return tf.name

def _send(to_addr: str, subject: str, body: str, attachments: List[str] | None = None) -> Dict[str, Any]:
    if os.getenv("OFFLINE") == "1":
        return {"ok": True, "offline": True, "sent": False, "attachments": attachments or []}
    # 測試環境不真正送信
    return {"ok": True, "offline": False, "sent": True, "attachments": attachments or []}

# --- 各動作 ---
def _action_send_quote(payload: Dict[str, Any]) -> Dict[str, Any]:
    client = payload.get("client_name") or payload.get("sender") or "客戶"
    pkg = choose_package(payload.get("subject",""), payload.get("body","")).get("package","基礎")
    pdf = generate_pdf_quote(pkg, str(client).replace("@", "_"))
    return {"action": "send_quote", "attachments": [pdf], "package": pkg}

def _action_reply_support(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": "reply_support"}

def _action_apply_info_change(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": "apply_info_change"}

def _action_reply_faq(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": "reply_faq"}

def _action_reply_apology(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": "reply_apology"}

def _action_reply_general(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": "reply_general"}

_LABEL_TO_ACTION = {
    # 中文
    "業務接洽或報價": _action_send_quote,
    "請求技術支援": _action_reply_support,
    "申請修改資訊": _action_apply_info_change,
    "詢問流程或規則": _action_reply_faq,
    "投訴與抱怨": _action_reply_apology,
    "其他": _action_reply_general,
    # 英文/內部
    "send_quote": _action_send_quote,
    "reply_support": _action_reply_support,
    "apply_info_change": _action_apply_info_change,
    "reply_faq": _action_reply_faq,
    "reply_apology": _action_reply_apology,
    "reply_general": _action_reply_general,
    "sales_inquiry": _action_send_quote,
    "complaint": _action_reply_apology,
    "other": _action_reply_general,
}

def _normalize_label(label: str) -> str:
    l = (label or "").strip()
    return l

def handle(payload: Dict[str, Any], *, dry_run: bool = False, simulate_failure: str = "") -> Dict[str, Any]:
    label = payload.get("predicted_label") or ""
    if not label:
        clf = IntentClassifier()
        c = clf.classify(payload.get("subject",""), payload.get("body",""))
        label = c.get("predicted_label") or c.get("label") or "其他"
    label = _normalize_label(label)
    action_fn = _LABEL_TO_ACTION.get(label) or _LABEL_TO_ACTION.get(label.lower()) or _action_reply_general
    out = action_fn(payload)

    # 風險與白名單
    attachments = payload.get("attachments") or []
    risky = any(_attachment_risks(a) for a in attachments if isinstance(a, dict))
    require_review = risky or bool(simulate_failure)

    # 投訴嚴重度（P1）
    if label in ("complaint", "投訴與抱怨"):
        text = f"{payload.get('subject','')} {payload.get('body','')}"
        if any(k in text for k in ["down","無法使用","嚴重","影響"]):
            out["priority"] = "P1"
            out["cc"] = ["oncall@example.com"]

    # send 行為（僅示意）
    if out["action"] == "send_quote":
        # 附件確保存在
        if not out.get("attachments"):
            out["attachments"] = [_ensure_attachment("報價單", ["感謝詢價"])]

    meta = {
        "dry_run": bool(dry_run),
        "require_review": bool(require_review),
    }
    out["meta"] = meta
    return out

# --- CLI ---
def _load_payload(ns) -> Dict[str, Any]:
    if getattr(ns, "input", None):
        if ns.input in ("-", ""):
            import sys
            return json.loads(sys.stdin.read())
        p = Path(ns.input)
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", default=None)
    p.add_argument("--output", "--out", dest="output", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--simulate-failure", nargs="?", const="any", default="")
    p.add_argument("--whitelist", action="store_true")
    ns, _ = p.parse_known_args(argv)

    payload = _load_payload(ns)
    res = handle(payload, dry_run=ns.dry_run, simulate_failure=ns.simulate_failure)

    # 回傳總結（舊測試期望頂層一些鍵）
    out_obj = {
        "action": res.get("action"),
        "attachments": res.get("attachments", []),
        "requires_review": res.get("meta", {}).get("require_review", False),
        "dry_run": res.get("meta", {}).get("dry_run", False),
        "input": payload,
        "meta": res.get("meta", {}),
    }

    if ns.output:
        Path(ns.output).parent.mkdir(parents=True, exist_ok=True)
        Path(ns.output).write_text(json.dumps(out_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(out_obj, ensure_ascii=False))

    return 0
