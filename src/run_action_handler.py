#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

# logger（容錯）
try:
    from src.utils.logger import logger  # type: ignore
except Exception:  # pragma: no cover
    import logging

    logger = logging.getLogger("SMA")  # type: ignore
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

SUBJECTS = {
    "send_quote": "[自動回覆] 報價說明",
    "reply_faq": "[自動回覆] FAQ 回覆",
    "sales_inquiry": "[自動回覆] 商務詢問回覆",
    "complaint": "[自動回覆] 投訴回覆",
    "reply_general": "[自動回覆] 一般回覆",
}


def _read_json(p: str | Path) -> Dict[str, Any]:
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(p: str | Path, obj: Dict[str, Any]) -> None:
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _now_ms(start: float) -> int:
    return int((time.time() - start) * 1000)


def _safe_text(x: Any) -> str:
    return x if isinstance(x, str) else ("" if x is None else str(x))


def _extract_need_fields(text: str) -> Dict[str, str]:
    txt = _safe_text(text)
    m_company = re.search(r"([\w\u4e00-\u9fa5]+(?:股份有限公司|公司))", txt)
    m_qty = re.search(r"(\d+)\s*(?:台|件|個|份)", txt)
    m_budget = re.search(r"(?:預算|NTD|NT\$|新台幣)\s*([0-9,]+)", txt, re.IGNORECASE)
    m_deadline = re.search(r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})", txt)
    return {
        "公司": m_company.group(1) if m_company else "未提供",
        "數量": m_qty.group(1) if m_qty else "未提供",
        "預算": m_budget.group(1) if m_budget else "未提供",
        "截止": m_deadline.group(1) if m_deadline else "未提供",
    }


def _mk_needs_summary(body: str, rid: str) -> Dict[str, Any]:
    fields = _extract_need_fields(body)
    content = (
        "# 需求彙整\n\n"
        f"- 公司：{fields['公司']}\n"
        f"- 數量：{fields['數量']}\n"
        f"- 預算：{fields['預算']}\n"
        f"- 截止：{fields['截止']}\n"
        "\n> 本彙整由離線規則抽詞產生，供業務快速確認需求。"
    )
    out_dir = Path("data/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"needs_summary_{rid}.md"
    p = out_dir / name
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return {"filename": name, "size": len(content)}


def _apply_policies(result: Dict[str, Any], req: Dict[str, Any]) -> None:
    meta = result.setdefault("meta", {})
    # 附件總尺寸 > 5MB -> 需審核 + CC
    total = 0
    for a in req.get("attachments", []) or []:
        try:
            total += int(a.get("size", 0))
        except Exception:
            pass
    if total > 5 * 1024 * 1024:
        meta["require_review"] = True
        cc = set(meta.get("cc", []) or [])
        cc.add("support@company.example")
        meta["cc"] = sorted(cc)
    # 白名單寄件者
    sender = _safe_text(req.get("from"))
    if sender.endswith("@trusted.example"):
        meta["whitelisted"] = True
    # 投訴高嚴重度 → 升級 CC（若前面已決定 cc，與之合併）
    if result.get("action_name") == "complaint" and meta.get("severity") == "high":
        cc = set(meta.get("cc", []) or [])
        cc.update({"ops@company.example", "qa@company.example"})
        meta["cc"] = sorted(cc)
        meta["require_review"] = True


def _route(predicted: str) -> str:
    mapping = {
        "send_quote": "send_quote",
        "reply_faq": "reply_faq",
        "sales_inquiry": "sales_inquiry",
        "complaint": "complaint",
    }
    return mapping.get(_safe_text(predicted), "reply_general")


def _handle_send_quote(req: Dict[str, Any], rid: str, simulate: str | None) -> Dict[str, Any]:
    body = "您好，這是報價附件與說明。"
    attachments: List[Dict[str, Any]] = []
    warnings: List[str] = []
    meta: Dict[str, Any] = {}
    if simulate == "pdf":
        txt = "PDF 生成失敗回退：請見文字版報價。"
        fname = "quote_fallback.txt"
        p = Path("data/output") / fname
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
        attachments.append({"filename": fname, "size": len(txt)})
        warnings.append("simulated_pdf_failure")
        meta["simulate_failure"] = "pdf"
    else:
        txt = "這是報價說明與明細（離線示例）。"
        fname = "quote_fallback.txt"
        p = Path("data/output") / fname
        p.write_text(txt, encoding="utf-8")
        attachments.append({"filename": fname, "size": len(txt)})
    return {"body": body, "attachments": attachments, "warnings": warnings, "meta": meta}


def _handle_reply_faq(req: Dict[str, Any]) -> Dict[str, Any]:
    return {"body": "以下為常見問題回覆與說明。", "attachments": []}


def _handle_sales_inquiry(req: Dict[str, Any], rid: str) -> Dict[str, Any]:
    body = "已收到您的商務詢問，內文下附需求彙整附件。"
    att = _mk_needs_summary(_safe_text(req.get("body")), rid)
    return {
        "body": body,
        "attachments": [att],
        "meta": {"next_step": "安排需求澄清會議並由業務跟進", "confidence": req.get("confidence")},
    }


def _handle_complaint(req: Dict[str, Any]) -> Dict[str, Any]:
    txt = _safe_text(req.get("body"))
    sev = "low"
    if re.search(r"(嚴重|無法使用|down|重大|主管機關|退款)", txt):
        sev = "high"
    elif re.search(r"(抱怨|投訴|不滿|延遲)", txt):
        sev = "med"
    meta = {
        "severity": sev,
        "priority": "P1" if sev == "high" else ("P2" if sev == "med" else "P3"),
        "SLA_eta": "4h" if sev == "high" else ("1d" if sev == "med" else "3d"),
        "next_step": "建立工單並通知負責窗口",
    }
    # 高嚴重度立即 CC（與政策合併邏輯一致）
    if sev == "high":
        meta["cc"] = sorted({"ops@company.example", "qa@company.example"})
        meta["require_review"] = True
    return {"body": "我們已接收您的反饋並立即處理。", "attachments": [], "meta": meta}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dry-run", action="store_true", help="不進行外部副作用")
    parser.add_argument(
        "--simulate-failure", dest="simulate_failure", choices=["pdf"], help="模擬特定失敗"
    )
    args = parser.parse_args()

    start = time.time()
    req = _read_json(args.input)
    rid = uuid.uuid4().hex[:12]
    action_name = _route(req.get("predicted_label"))
    subject = SUBJECTS.get(action_name, "[自動回覆] 系統回覆")

    result: Dict[str, Any] = {"action_name": action_name, "subject": subject, "attachments": []}
    if action_name == "send_quote":
        part = _handle_send_quote(req, rid, args.simulate_failure)
    elif action_name == "reply_faq":
        part = _handle_reply_faq(req)
    elif action_name == "sales_inquiry":
        part = _handle_sales_inquiry(req, rid)
    elif action_name == "complaint":
        part = _handle_complaint(req)
    else:
        part = {"body": "已收到您的訊息，我們會儘速回覆。", "attachments": []}

    for k in ("body", "attachments", "warnings"):
        if k in part:
            result[k] = part[k]
    meta = result.setdefault("meta", {})
    meta.update(part.get("meta", {}))
    meta["request_id"] = rid
    meta["duration_ms"] = _now_ms(start)
    meta["dry_run"] = bool(args.dry_run)
    result["dry_run"] = bool(args.dry_run)

    _apply_policies(result, req)

    _write_json(args.output, result)
    try:
        logger.info("CLI_output_written")
    except Exception:
        pass
    print(f"已輸出：{args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
