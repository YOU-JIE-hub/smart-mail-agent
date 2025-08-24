from __future__ import annotations

from collections.abc import Iterable
from typing import Any

try:
    from pydantic import BaseModel, Field  # v2

    _V2 = True
except Exception:
    # pragma: no cover
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
    data["attachments"] = _coerce_attachments_safe(data.get("attachments"))
    # 確保有 duration_ms 鍵
    data.setdefault("duration_ms", 0)
    return ActionResult(**data)


# ---- 安全附件正規化（允許 None/str/dict 混合） ----
def _coerce_attachments_safe(src):
    # 將各種輸入形狀轉為統一 dict 列表，過濾 None/空字串：
    #   - "a.txt" -> {"filename":"a.txt","mime":"application/octet-stream","size":0}
    #   - {"name":"b.pdf","size":123} -> 轉為 {"filename":"b.pdf","size":123,"mime":...}
    #   - 已是 dict 且有 filename/mime/size 保留並補預設；其餘型別忽略
    out = []
    for it in src or []:
        if not it:
            continue
        if isinstance(it, str):
            name = it.strip()
            if not name:
                continue
            out.append({"filename": name, "mime": "application/octet-stream", "size": 0})
            continue
        if isinstance(it, dict):
            d = dict(it)
            fname = d.get("filename") or d.get("name") or d.get("file") or d.get("path") or ""
            fname = str(fname).strip()
            if not fname:
                continue
            d["filename"] = fname
            if "size" not in d:
                d["size"] = d.get("length") or 0
            if "mime" not in d:
                d["mime"] = d.get("content_type") or "application/octet-stream"
            out.append(d)
            continue
        # 其它型別（例如自訂物件）為避免驗證錯，直接忽略
    return out
