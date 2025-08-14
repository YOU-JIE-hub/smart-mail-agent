from __future__ import annotations

from typing import Any, Dict, Tuple

REQUIRED_TOP: Tuple[str, ...] = ("action",)


def normalize_request(d: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(d or {})
    d.setdefault("meta", {})
    d.setdefault("dry_run", False)
    for k in REQUIRED_TOP:
        d.setdefault(k, None)
    # 兼容：若 meta 有 dry_run，同步到頂層
    if isinstance(d.get("meta"), dict) and "dry_run" in d["meta"]:
        d["dry_run"] = bool(d["meta"]["dry_run"])
    return d


def normalize_result(r: Dict[str, Any]) -> Dict[str, Any]:
    r = dict(r or {})
    r.setdefault("meta", {})
    r.setdefault("dry_run", False)
    if isinstance(r.get("meta"), dict) and "dry_run" in r["meta"]:
        r["dry_run"] = bool(r["meta"]["dry_run"])
    # 測試常用欄位兼容
    r.setdefault("action", r.get("action"))
    r.setdefault("predicted_label", r.get("label"))
    return r


__all__ = ["normalize_request", "normalize_result", "REQUIRED_TOP"]
