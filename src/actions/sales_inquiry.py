# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any, Dict

from utils.templater import render

DATA_DIR = Path("data")
LEADS = DATA_DIR / "leads" / "leads.csv"


def _append_lead(req: Dict[str, Any], score: float = 0.5, owner: str = "sales@company.com") -> None:
    LEADS.parent.mkdir(parents=True, exist_ok=True)
    new_file = not LEADS.exists()
    with LEADS.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["ts", "from", "subject", "score", "owner"])
        w.writerow(
            [
                time.strftime("%Y-%m-%d %H:%M:%S"),
                req.get("from", ""),
                req.get("subject", ""),
                score,
                owner,
            ]
        )


def handle(req: Dict[str, Any]) -> Dict[str, Any]:
    _append_lead(req)
    body = render(
        "sales_inquiry_reply.j2", sender=req.get("from", ""), subject=req.get("subject", "")
    )
    return {
        "ok": True,
        "action_name": "sales_inquiry",
        "subject": "[自動回覆] 商務洽談需求確認",
        "body": body,
        "attachments": [],
    }
