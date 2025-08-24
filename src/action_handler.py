from __future__ import annotations

from typing import Dict

_MAPPING = {
    "請求技術支援": "reply_support",
    "申請修改資訊": "apply_info_change",
    "詢問流程或規則": "reply_faq",
    "投訴與抱怨": "reply_apology",
    "業務接洽或報價": "send_quote",
    "其他": "reply_general",
    "未定義標籤": "reply_general",
}


def run(intent_text: str) -> Dict[str, object]:
    return {"ok": True, "action_name": _MAPPING.get((intent_text or "").strip(), "reply_general")}
