#!/usr/bin/env python3
# 檔案位置：src/policy_engine.py
# 模組用途：依據 config/policy.yaml 套用策略；支援多種 when/effect 條件

from __future__ import annotations

import os
from typing import Any, Dict, List

import yaml


def _sum_attachments_size(items: List[dict]) -> int:
    total = 0
    for it in items or []:
        try:
            total += int(it.get("size") or 0)
        except Exception:
            pass
    return total


def _from_domain(addr: str | None) -> str | None:
    if not addr or "@" not in addr:
        return None
    return addr.split("@", 1)[1].lower()


def _match_when(when: dict, bundle: dict) -> bool:
    # 支援：label, max_confidence, severity, attachments_total_size_gt, from_domain_in
    if "label" in when and when["label"] != bundle.get("label"):
        return False
    if "max_confidence" in when:
        try:
            if float(bundle.get("confidence") or 0) > float(when["max_confidence"]):
                return False
        except Exception:
            return False
    if "severity" in when and when["severity"] != bundle.get("severity"):
        return False
    if "attachments_total_size_gt" in when:
        try:
            if int(bundle.get("attachments_total_size") or 0) <= int(when["attachments_total_size_gt"]):
                return False
        except Exception:
            return False
    if "from_domain_in" in when:
        dom = (bundle.get("from_domain") or "").lower()
        wl = [str(x).lower() for x in (when.get("from_domain_in") or [])]
        if dom not in wl:
            return False
    return True


def _apply_effect(effect: dict, result: dict) -> None:
    meta = result.setdefault("meta", {})
    # require_review
    if "require_review" in effect:
        meta["require_review"] = bool(effect["require_review"])
    # cc
    if "cc" in effect:
        cc = set(meta.get("cc") or [])
        for r in effect["cc"] or []:
            cc.add(r)
        meta["cc"] = sorted(cc)
    # set_subject_prefix
    if "set_subject_prefix" in effect:
        prefix = str(effect["set_subject_prefix"])
        subj = result.get("subject") or ""
        if not subj.startswith(prefix):
            result["subject"] = f"{prefix}{subj}"
    # set_action
    if "set_action" in effect:
        result["action_name"] = str(effect["set_action"])
    # set_meta
    if "set_meta" in effect:
        for k, v in (effect.get("set_meta") or {}).items():
            meta[k] = v


def apply_policies(
    result: Dict[str, Any], request: Dict[str, Any], policy_path: str = "config/policy.yaml"
) -> Dict[str, Any]:
    """
    參數:
        result: 動作回傳的 ActionResult
        request: 原始輸入
        policy_path: YAML 規則路徑
    回傳:
        經策略套用後的 ActionResult
    """
    if not os.path.exists(policy_path):
        return result
    try:
        rules = yaml.safe_load(open(policy_path, "r", encoding="utf-8")) or {}
    except Exception:
        return result

    attachments = request.get("attachments") or []
    bundle = {
        "label": result.get("action_name"),
        "confidence": request.get("confidence"),
        "severity": (result.get("meta") or {}).get("severity"),
        "attachments_total_size": _sum_attachments_size(attachments),
        "from_domain": _from_domain(request.get("from")),
    }

    for rule in rules.get("rules") or []:
        when = rule.get("when") or {}
        effect = rule.get("effect") or {}
        try:
            if _match_when(when, bundle):
                _apply_effect(effect, result)
        except Exception:
            continue
    return result


# ---- compatibility shim for tests ----
def apply_policy(policy, message, context=None):
    """
    Wrap single policy into apply_policies to keep tests compatible.
    """
    try:
        res = apply_policies([policy], message, context)
        # 若原本 apply_policies 回傳列表
        return res[0] if isinstance(res, (list, tuple)) else res
    except NameError:
        # 若此檔無 apply_policies，直接回傳 policy(message)
        return policy(message)
