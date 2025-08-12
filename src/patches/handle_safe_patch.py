# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

BASE = Path(__file__).resolve().parents[1]
for p in (BASE, BASE.parent):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

try:
    from action_handler import handle as _orig_handle  # type: ignore
except Exception:
    from src.action_handler import handle as _orig_handle  # type: ignore

try:
    from src.utils.pdf_safe import write_pdf_or_txt
except Exception:
    from utils.pdf_safe import write_pdf_or_txt  # type: ignore


def _attachments_ok(att_list: List[str] | None) -> bool:
    if not att_list:
        return False
    for a in att_list:
        p = Path(a)
        if not (p.exists() and p.stat().st_size > 0):
            return False
    return True


def handle(payload: Dict[str, Any]) -> Dict[str, Any]:
    os.environ.setdefault("OFFLINE", "1")
    res = _orig_handle(payload)
    if (res or {}).get("action") == "send_quote":
        atts = res.get("attachments") or []
        if not _attachments_ok(atts):
            subject = res.get("subject") or payload.get("subject", "報價")
            content = payload.get("content", "")
            lines = [f"主旨: {subject}", f"內容: {content}"]
            p = write_pdf_or_txt(lines, basename="attachment")
            res["attachments"] = [str(p)]
            if isinstance(res.get("mailer"), dict):
                res["mailer"]["attachments"] = res["attachments"]
    return res
