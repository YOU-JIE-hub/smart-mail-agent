from __future__ import annotations

from collections.abc import Iterable
from typing import Any

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
    size: int | None = None
    mime: str | None = None


class Request(_CompatModel):
    subject: str = ""
    from_: str | None = Field(default=None, alias="from")
    body: str = ""
    predicted_label: str = ""  # 預設空字串（測試期望）
    confidence: float = -1.0  # 預設 -1.0（測試期望）
    attachments: list[Any] = []


class ActionResult(_CompatModel):
    action: str | None = None
    action_name: str | None = None
    ok: bool = True
    code: str = "OK"
    message: str = ""
    subject: str | None = None
    body: str | None = None
    output: Any | None = None  # 放寬以容納多型 payload
    attachments: list[AttachmentMeta | dict[str, Any] | str] = []
    request_id: str | None = None
    spent_ms: int | None = None
    duration_ms: int = 0  # 測試只檢查鍵是否存在
    meta: dict[str, Any] = {}
    cc: list[str] = []

    def with_logged_path(self, path: str | None) -> ActionResult:
        if path:
            self.meta = dict(self.meta or {})
            self.meta.setdefault("logged_path", path)
        return self


def _coerce_attachments(
    items: Iterable[Any] | None,
) -> list[AttachmentMeta | dict[str, Any] | str]:
    out: list[AttachmentMeta | dict[str, Any] | str] = []
    for a in items or []:
        if isinstance(a, str):
            out.append(AttachmentMeta(path=a, exists=True))
        else:
            out.append(a)
    return out


def normalize_request(raw: dict[str, Any]) -> Request:
    return Request(**raw)


def normalize_result(raw: dict[str, Any]) -> ActionResult:
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
