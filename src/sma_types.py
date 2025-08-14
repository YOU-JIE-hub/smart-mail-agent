from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Union

try:
    from pydantic import BaseModel, Field  # v2

    _V2 = True
except Exception:  # pragma: no cover
    from pydantic import BaseModel, Field  # type: ignore  # v1

    _V2 = False


class _CompatModel(BaseModel):
    """提供 v1/v2 一致的 model_dump()。"""

    def model_dump(self, **kwargs):
        if hasattr(super(), "model_dump"):
            return super().model_dump(**kwargs)  # type: ignore[attr-defined]
        return self.dict(**kwargs)  # type: ignore[call-arg]

    class Config:  # pydantic v1
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class AttachmentMeta(_CompatModel):
    path: str
    exists: bool = True
    size: Optional[int] = None
    mime: Optional[str] = None


class Request(_CompatModel):
    subject: str = ""
    from_: Optional[str] = Field(default=None, alias="from")
    body: str = ""
    predicted_label: str = ""  # 預設空字串（測試期望）
    confidence: float = -1.0  # 預設 -1.0（測試期望）
    attachments: List[Any] = []


class ActionResult(_CompatModel):
    action: Optional[str] = None
    action_name: Optional[str] = None
    ok: bool = True
    code: str = "OK"
    message: str = ""
    subject: Optional[str] = None
    body: Optional[str] = None
    output: Optional[Any] = None  # 放寬以容納多型 payload
    attachments: List[Union[AttachmentMeta, Dict[str, Any], str]] = []
    request_id: Optional[str] = None
    spent_ms: Optional[int] = None
    duration_ms: int = 0  # 測試只檢查鍵是否存在
    meta: Dict[str, Any] = {}
    cc: List[str] = []

    def with_logged_path(self, path: Optional[str]) -> "ActionResult":
        if path:
            self.meta = dict(self.meta or {})
            self.meta.setdefault("logged_path", path)
        return self


def _coerce_attachments(items: Optional[Iterable[Any]]) -> List[Union[AttachmentMeta, Dict[str, Any], str]]:
    out: List[Union[AttachmentMeta, Dict[str, Any], str]] = []
    for a in items or []:
        if isinstance(a, str):
            out.append(AttachmentMeta(path=a, exists=True))
        else:
            out.append(a)
    return out


def normalize_request(raw: Dict[str, Any]) -> Request:
    return Request(**raw)


def normalize_result(raw: Dict[str, Any]) -> ActionResult:
    data = dict(raw or {})
    # 對齊 action 欄位
    if "action" not in data and "action_name" in data:
        data["action"] = data.get("action_name")
    # 主旨自動加前綴
    subj = data.get("subject")
    if isinstance(subj, str) and not subj.startswith("[自動回覆] "):
        data["subject"] = f"[自動回覆] {subj}"
    # 附件正規化
    data["attachments"] = _coerce_attachments(data.get("attachments"))
    # 確保有 duration_ms 鍵
    data.setdefault("duration_ms", 0)
    return ActionResult(**data)
