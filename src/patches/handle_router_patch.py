# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
from typing import Any, Dict

BASE = __import__("pathlib").Path(__file__).resolve().parents[1]
for p in (BASE, BASE.parent):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

# 以「安全附件補丁」為 base，再前置路由/校驗
from patches.handle_safe_patch import handle as _base_handle  # type: ignore

_CANON = {
    "業務接洽或報價": "send_quote",
    "請求技術支援": "reply_support",
    "申請修改資訊": "apply_info_change",
    "詢問流程或規則": "reply_faq",
    "投訴與抱怨": "reply_apology",
    "其他": "reply_general",
}
# 關鍵字同義對應（英/中）
_RULES = [
    (
        ("業務接洽或報價", "報價", "詢價", "價格", "quote", "pricing", "price", "sales"),
        "業務接洽或報價",
    ),
    (
        ("請求技術支援", "技術支援", "技術", "支援", "錯誤", "bug", "error", "support", "issue"),
        "請求技術支援",
    ),
    (
        (
            "申請修改資訊",
            "修改資料",
            "更改資料",
            "更新資料",
            "變更",
            "info-change",
            "apply",
            "update info",
        ),
        "申請修改資訊",
    ),
    (("詢問流程或規則", "流程", "規則", "退貨", "faq", "policy", "how to"), "詢問流程或規則"),
    (("投訴與抱怨", "投訴", "抱怨", "客訴", "complaint", "bad", "angry", "refund"), "投訴與抱怨"),
    (("其他", "general", "other", "misc"), "其他"),
]


def _norm_label(s: Any) -> str:
    if not isinstance(s, str) or not s.strip():
        return "其他"
    raw = s.strip().lower()
    # 先比對中文完整命名
    for k in _CANON.keys():
        if k in s:
            return k
    # 再用關鍵字
    for keys, target in _RULES:
        for kw in keys:
            if kw in raw or kw in s:
                return target
    return "其他"


def _norm_payload(p: Dict[str, Any]) -> Dict[str, Any]:
    p = dict(p or {})
    p.setdefault("subject", "未提供主旨")
    p.setdefault("content", "未提供內容")
    p["sender"] = p.get("sender") or "noreply@example.com"
    p["predicted_label"] = _norm_label(p.get("predicted_label"))
    return p


def _fallback_action(res: Dict[str, Any]) -> Dict[str, Any]:
    # 若原流程未給 action，依標準映射兜底
    act = res.get("action")
    if not act:
        label = res.get("predicted_label") or "其他"
        res["action"] = _CANON.get(label, "reply_general")
    return res


def handle(payload: Dict[str, Any]) -> Dict[str, Any]:
    os.environ.setdefault("OFFLINE", "1")
    pl = _norm_payload(payload)
    res = _base_handle(pl)
    return _fallback_action(res or {})
