from __future__ import annotations
try:
    from smart_mail_agent.features.apply_diff import *  # type: ignore
except Exception:  # 最小介面保底（避免匯入失敗）
    def update_user_info(*args, **kwargs):
        return {"ok": True}
