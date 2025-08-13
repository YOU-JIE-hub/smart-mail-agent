#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Dict, List

import yaml


def _load_policy(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def apply_policy(
    result: Dict[str, Any], request: Dict[str, Any], policy_file: str
) -> Dict[str, Any]:
    policy = _load_policy(policy_file)
    meta = result.setdefault("meta", {})
    cc: List[str] = result.setdefault("cc", [])

    # 低信心覆核（reply_faq）
    low_conf = policy.get("low_confidence_review", {})
    if (request.get("predicted_label") or "") == "reply_faq":
        th = float(low_conf.get("threshold", 0.6))
        conf = float(request.get("confidence", -1.0))
        if conf >= 0 and conf < th:
            meta["require_review"] = True
            for addr in low_conf.get("cc", []):
                if addr not in cc:
                    cc.append(addr)

    # 投訴升級（high）
    esc = policy.get("complaint_escalation", {})
    if result.get("action_name") == "complaint" and meta.get("severity") == "high":
        meta.setdefault("priority", "P1")
        meta.setdefault("sla_eta", esc.get("sla_eta_high", "24h"))
        for addr in esc.get("cc", []):
            if addr not in cc:
                cc.append(addr)
        meta["require_review"] = True

    # 附件大小限制 → 人工覆核
    att = policy.get("attachments_limit", {})
    if att:
        limit = int(att.get("max_total_bytes", 5 * 1024 * 1024))
        total = sum(int(a.get("size_bytes") or 0) for a in request.get("attachments", []))
        if total > limit:
            meta["attachments_policy"] = "over_limit"
            meta["require_review"] = True
            for addr in att.get("cc", []):
                if addr not in cc:
                    cc.append(addr)

    # 白名單紀錄
    wl = policy.get("allow_domains", {})
    sender = (request.get("sender") or "").lower()
    if "@" in sender and wl:
        domain = sender.split("@", 1)[1]
        if domain in (wl.get("domains") or []):
            meta["whitelisted_sender"] = True

    result["cc"] = cc
    result["meta"] = meta
    return result


# 舊名相容
def apply_policies(
    result: Dict[str, Any], request: Dict[str, Any], policy_file: str
) -> Dict[str, Any]:
    return apply_policy(result, request, policy_file)


__all__ = ["apply_policy", "apply_policies"]


def apply_policies(*args, **kwargs):  # noqa: F811
    import os

    if len(args) == 2 and isinstance(args[0], dict) and isinstance(args[1], dict):
        req, res = args
        policy_file = os.getenv("SMA_POLICY_FILE", os.getenv("POLICY_FILE", "configs/policy.yaml"))
        return apply_policy(res, req, policy_file)
    elif len(args) == 3:
        return apply_policy(*args)
    else:
        res = kwargs.get("result") or {}
        req = kwargs.get("request") or {}
        policy_file = kwargs.get("policy_file") or os.getenv(
            "SMA_POLICY_FILE", os.getenv("POLICY_FILE", "configs/policy.yaml")
        )
        return apply_policy(res, req, policy_file)
