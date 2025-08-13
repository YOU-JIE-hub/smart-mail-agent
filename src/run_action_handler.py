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

    # 1) 先嘗試路由補丁（英文/別名 → 標準動作）
    applied = False
    try:
        from patches.handle_router_patch import handle as router_handle  # type: ignore

        ah.handle = router_handle
        applied = True
    except Exception:
        pass

    # 2) 失敗則退回安全補丁（附件/PDF 安全處理）
    if not applied:
        try:
            from patches.handle_safe_patch import handle as safe_handle  # type: ignore

            ah.handle = safe_handle
            applied = True
        except Exception:
            pass

    # 3) 仍未套用，提供最小內建 fallback，保證面試不會走錯路
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

    from action_handler import main as action_main  # type: ignore

    action_main()


if __name__ == "__main__":
    main()
