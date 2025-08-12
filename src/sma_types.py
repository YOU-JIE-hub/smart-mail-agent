from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AttachmentMeta(BaseModel):
    path: str
    exists: bool = True
    size: Optional[int] = None
    mime: Optional[str] = None


class ActionResult(BaseModel):
    # 統一回傳契約；向外仍可 dict 輸出
    action: Literal[
        "send_quote",
        "reply_faq",
        "reply_support",
        "reply_general",
        "reply_apology",
        "sales",
        "apply_info_change",
    ]
    ok: bool = True
    code: str = "OK"  # OK / INPUT_INVALID / EXTERNAL_FAIL / INTERNAL_ERROR
    message: str = ""
    output: Optional[str] = None
    attachments: List[AttachmentMeta] = Field(default_factory=list)
    request_id: Optional[str] = None
    spent_ms: Optional[int] = None
    version: str = "1.0"
