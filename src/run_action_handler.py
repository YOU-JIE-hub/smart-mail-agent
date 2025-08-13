# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys


def main() -> None:
    base = os.path.abspath(os.path.dirname(__file__))
    if base not in sys.path:
        sys.path.insert(0, base)

    import action_handler as ah  # type: ignore

    os.environ.setdefault("OFFLINE", "1")

    applied = False
    # 1) 路由補丁
    try:
        from patches.handle_router_patch import handle as router_handle  # type: ignore

        ah.handle = router_handle
        applied = True
    except Exception:
        pass

    # 2) 安全補丁
    if not applied:
        try:
            from patches.handle_safe_patch import handle as safe_handle  # type: ignore

            ah.handle = safe_handle
            applied = True
        except Exception:
            pass

    # 3) fallback：把常見別名正規化
    if not applied:
        _alias = {
            "send_quote": "send_quote",
            "reply_faq": "reply_faq",
            "reply_support": "reply_support",
            "apply_info_change": "apply_info_change",
            "other": "reply_general",
        }
        _orig = getattr(ah, "handle", None)

        def _fallback_handle(req: dict):
            lbl = (req.get("predicted_label") or "").strip().lower()
            req["predicted_label"] = _alias.get(lbl, lbl)
            if callable(_orig):
                return _orig(req)
            return {"ok": True, "action": "reply_general", "subject": "[自動回覆] 一般諮詢"}

        ah.handle = _fallback_handle

    # 4) 最終包裝器：統一輸出欄位，補 subject 前綴
    _selected = getattr(ah, "handle")

    def _normalize_and_prefix(req: dict):
        res = _selected(req)
        try:
            if isinstance(res, dict):
                act = res.get("action_name") or res.get("action") or ""
                # 補 action_name
                if act and ("action_name" not in res):
                    res["action_name"] = act
                # 補 subject 前綴
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
