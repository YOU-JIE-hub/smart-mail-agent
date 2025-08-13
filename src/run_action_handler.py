# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import os
import sys


def main() -> None:
    base = os.path.abspath(os.path.dirname(__file__))
    if base not in sys.path:
        sys.path.insert(0, base)

    import action_handler as ah  # type: ignore

    os.environ.setdefault("OFFLINE", "1")  # 預設離線

    # 取得原始 handle，供非新增意圖時委派
    _orig = getattr(ah, "handle", None)

    # 輕量 router：只攔截「我們新增的」intent，其餘交回原始 handle
    _ALIASES = {
        "business_inquiry": "sales_inquiry",
        "sales": "sales_inquiry",
        "complain": "complaint",
    }

    def _router(req: dict):
        label = (req.get("predicted_label") or "").strip().lower()
        label = _ALIASES.get(label, label)
        req["predicted_label"] = label

        if label == "sales_inquiry":
            return importlib.import_module("actions.sales_inquiry").handle(req)
        if label == "complaint":
            return importlib.import_module("actions.complaint").handle(req)

        if callable(_orig):
            return _orig(req)
        return {"ok": True, "action": "reply_general", "subject": "[自動回覆] 一般諮詢"}

    # 最終包裝器：補 action_name、為 reply_* 加上主旨前綴
    def _normalize_and_prefix(req: dict):
        res = _router(req)
        try:
            if isinstance(res, dict):
                act = res.get("action_name") or res.get("action") or ""
                if act and ("action_name" not in res):
                    res["action_name"] = act
                if act.startswith("reply_"):
                    subj = res.get("subject") or ""
                    if not subj.startswith("[自動回覆] "):
                        res["subject"] = "[自動回覆] " + (subj or "一般諮詢")
        except Exception:
            pass
        return res

    ah.handle = _normalize_and_prefix

    from action_handler import main as action_main  # type: ignore

    action_main()


if __name__ == "__main__":
    main()
