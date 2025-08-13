# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
from typing import Any, Dict

import action_handler as ah  # capture original before CLI patches

_ORIG = getattr(ah, "handle", None)

_ALIASES = {
    "business_inquiry": "sales_inquiry",
    "sales": "sales_inquiry",
    "complain": "complaint",
}


def _normalize(label: str) -> str:
    return _ALIASES.get(label, label)


def handle(req: Dict[str, Any]) -> Dict[str, Any]:
    label = (req.get("predicted_label") or "").strip().lower()
    label = _normalize(label)
    req["predicted_label"] = label

    if label == "sales_inquiry":
        return importlib.import_module("actions.sales_inquiry").handle(req)
    if label == "complaint":
        return importlib.import_module("actions.complaint").handle(req)

    if callable(_ORIG):
        return _ORIG(req)
    return {"ok": True, "action": "reply_general", "subject": "[自動回覆] 一般諮詢"}
