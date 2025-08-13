# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import re
import time
from pathlib import Path
from typing import Any, Dict

from utils.templater import render

DATA_DIR = Path("data")
LOG = DATA_DIR / "complaints" / "log.csv"


def _grade(body: str, subject: str) -> str:
    text = f"{subject}\n{body}".lower()
    high_kw = ("投訴", "檢舉", "法律", "惡劣", "退款", "退貨", "詐騙")
    med_kw = ("不滿", "抱怨", "不便", "失望")
    if (
        any(k in text for k in high_kw)
        or text.count("!") >= 3
        or re.search(r"(very bad|terrible)", text)
    ):
        return "high"
    if any(k in text for k in med_kw):
        return "med"
    return "low"


def _log(req: Dict[str, Any], severity: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new_file = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["ts", "from", "subject", "severity"])
        w.writerow(
            [
                time.strftime("%Y-%m-%d %H:%M:%S"),
                req.get("from", ""),
                req.get("subject", ""),
                severity,
            ]
        )


def handle(req: Dict[str, Any]) -> Dict[str, Any]:
    sev = _grade(req.get("body", ""), req.get("subject", ""))
    _log(req, sev)
    tmpl = f"complaint_{sev}.j2"
    body = render(tmpl, severity=sev, sender=req.get("from", ""), subject=req.get("subject", ""))
    subj = (
        "我們已收到您的反饋"
        if sev == "low"
        else ("我們已升級處理您的投訴" if sev == "med" else "高優先權處理：您的投訴已升級")
    )
    return {
        "ok": True,
        "action_name": "complaint",
        "subject": "[自動回覆] " + subj,
        "body": body,
        "attachments": [],
        "meta": {"severity": sev},
    }
