#!/usr/bin/env python3
# 檔案: src/smart_mail_agent/spam/pipeline.py
from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from typing import Any

from .orchestrator_offline import SpamFilterOrchestratorOffline, Thresholds
from .rules import has_suspicious_attachment, label_email


def analyze(
    email_or_subject: Mapping[str, Any] | str, content: str | None = None
) -> dict[str, Any]:
    if isinstance(email_or_subject, dict):
        email = dict(email_or_subject)
        subject = str(email.get("subject", "") or "")
        body = str(email.get("content", "") or "")
        attachments = email.get("attachments", [])
        if not isinstance(attachments, (list | tuple)):
            attachments = []
            email["attachments"] = attachments
    else:
        subject = str(email_or_subject or "")
        body = str(content or "")
        email = {"subject": subject, "content": body, "attachments": []}
        attachments = []

    rule_res = label_email(email, lr_drop=Thresholds().link_ratio_drop)
    orch = SpamFilterOrchestratorOffline()
    decision = orch.decide(subject, body)
    action = str(decision["action"])

    # 若僅附件可疑（但 orchestrator 未升級），最少 review
    att_flag, _ = has_suspicious_attachment(attachments)
    if att_flag and action == "route":
        action = "review"

    return {
        "label": rule_res["label"],
        "action": action,
        "score": float(rule_res.get("score", 0.0)),
        "scores": rule_res.get("scores", {}),
        "decision": decision,
    }


def _build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Spam analyze pipeline (offline)")
    p.add_argument("--subject", default="")
    p.add_argument("--content", default="")
    p.add_argument("--json", action="store_true")
    return p


def _main() -> int:
    args = _build_cli().parse_args()
    out = analyze(args.subject, args.content)
    print(json.dumps(out, ensure_ascii=False, indent=2) if args.json else out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
