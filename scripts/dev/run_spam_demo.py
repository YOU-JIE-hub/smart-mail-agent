from __future__ import annotations

import json
import time
from pathlib import Path

from src.spam.pipeline import analyze

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "output"
OUT.mkdir(parents=True, exist_ok=True)

SAMPLES = [
    {
        "name": "ham_simple",
        "email": {
            "sender": "client@company.com",
            "subject": "關於報價與合約",
            "content": "請提供新版報價與付款條款，謝謝",
            "attachments": [],
        },
    },
    {
        "name": "spam_giveaway",
        "email": {
            "sender": "admin@promo.top",
            "subject": "GET RICH QUICK!!!",
            "content": "Free crypto airdrop now: https://scam.click/win?token=abc",
            "attachments": [],
        },
    },
    {
        "name": "suspect_attach",
        "email": {
            "sender": "it@support.co",
            "subject": "Password reset",
            "content": "Please verify your login via the link",
            "attachments": ["reset.js"],
        },
    },
]


def main():
    rows = []
    for s in SAMPLES:
        r = analyze(s["email"])
        rows.append({"name": s["name"], **r})
    out = OUT / "spam_demo.json"
    out.write_text(
        json.dumps({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("[SPAM] demo ->", out)


if __name__ == "__main__":
    main()
