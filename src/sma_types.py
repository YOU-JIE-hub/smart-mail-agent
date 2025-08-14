from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ---- Contracts for tests/contracts/test_action_result_contracts.py ----
@dataclass
class AttachmentMeta:
    filename: str
    content_type: Optional[str] = None
    path: Optional[str] = None  # 本地路徑（若有）
    size: Optional[int] = None  # bytes
    sha256: Optional[str] = None
    inline: Optional[bool] = None


@dataclass
class ActionResult:
    action: Optional[str] = None
    label: Optional[str] = None
    predicted_label: Optional[str] = None
    confidence: Optional[float] = None
    dry_run: bool = False
    meta: Dict[str, Any] = field(default_factory=dict)
    attachments: List[AttachmentMeta] = field(default_factory=list)
    logged_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # 兼容：若只有 label，複製到 predicted_label；反之亦然
        if d.get("predicted_label") is None and d.get("label") is not None:
            d["predicted_label"] = d["label"]
        if d.get("label") is None and d.get("predicted_label") is not None:
            d["label"] = d["predicted_label"]
        # 同步 meta.dry_run -> 頂層
        if isinstance(d.get("meta"), dict) and "dry_run" in d["meta"]:
            d["dry_run"] = bool(d["meta"]["dry_run"])
        return d


REQUIRED_TOP: Tuple[str, ...] = ("action",)


def _coerce_attachments(v: Optional[Iterable[Any]]) -> List[AttachmentMeta]:
    out: List[AttachmentMeta] = []
    if not v:
        return out
    for x in v:
        if isinstance(x, AttachmentMeta):
            out.append(x)
        elif isinstance(x, dict) and "filename" in x:
            out.append(AttachmentMeta(**x))
    return out


def normalize_request(d: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(d or {})
    d.setdefault("meta", {})
    d.setdefault("dry_run", False)
    for k in REQUIRED_TOP:
        d.setdefault(k, None)
    if isinstance(d.get("meta"), dict) and "dry_run" in d["meta"]:
        d["dry_run"] = bool(d["meta"]["dry_run"])
    return d


def normalize_result(r: Dict[str, Any]) -> Dict[str, Any]:
    # 支援 dict 或 ActionResult
    if isinstance(r, ActionResult):
        return r.to_dict()
    r = dict(r or {})
    r.setdefault("meta", {})
    r.setdefault("dry_run", False)
    # 兼容欄位
    if r.get("predicted_label") is None and r.get("label") is not None:
        r["predicted_label"] = r["label"]
    if r.get("label") is None and r.get("predicted_label") is not None:
        r["label"] = r["predicted_label"]
    # 同步 dry_run
    if isinstance(r.get("meta"), dict) and "dry_run" in r["meta"]:
        r["dry_run"] = bool(r["meta"]["dry_run"])
    # attachments 正規化
    r["attachments"] = _coerce_attachments(r.get("attachments"))
    return r


__all__ = [
    "AttachmentMeta",
    "ActionResult",
    "normalize_request",
    "normalize_result",
    "REQUIRED_TOP",
]
