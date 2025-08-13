# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_DEFAULT = Path("config/policy.yaml")


def _get(d: dict, path: str, default=None):
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def _match(rule_when: dict, req: dict, res: dict) -> bool:
    intent = rule_when.get("intent")
    if intent and (req.get("predicted_label") != intent and res.get("action_name") != intent):
        return False
    cb = rule_when.get("confidence_below")
    if cb is not None and not (float(req.get("confidence") or -1) < float(cb)):
        return False
    meta = rule_when.get("meta") or {}
    for k, v in meta.items():
        if _get(res.get("meta", {}), k) != v:
            return False
    return True


def _apply(rule_then: dict, res: dict) -> dict:
    out = dict(res)  # shallow copy
    meta = dict(out.get("meta") or {})
    cc = list(out.get("cc") or [])

    if rule_then.get("require_review"):
        meta["require_review"] = True
    if "priority" in rule_then:
        meta["priority"] = rule_then["priority"]

    for x in rule_then.get("add_cc") or []:
        if x not in cc:
            cc.append(x)

    if cc:
        out["cc"] = cc
    if meta:
        out["meta"] = meta
    return out


def apply_policies(req: dict, res: dict, path: str | os.PathLike = _DEFAULT) -> dict:
    try:
        p = Path(path)
        if not p.exists():
            return res
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        rules = data.get("policies") or []
        out = dict(res)
        for r in rules:
            if _match(r.get("when") or {}, req, out):
                out = _apply(r.get("then") or {}, out)
        return out
    except Exception:
        # 避免 policy 問題影響主流程
        return res
