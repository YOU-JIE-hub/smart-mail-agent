from __future__ import annotations
try:
    from smart_mail_agent.features.sales_notifier import *  # type: ignore
except Exception:
    def notify_sales(*_, **__):  # pragma: no cover
        return {"ok": True}
