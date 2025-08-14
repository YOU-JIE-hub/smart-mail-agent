#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

ALLOWED_INTENTS = {
    "send_quote",
    "reply_faq",
    "sales_inquiry",
    "complaint",
    "reply_general",
    "other",
}


class Attachment(BaseModel):
    filename: str
    content_type: Optional[str] = None
    path: Optional[str] = None
    size_bytes: Optional[int] = None

    def model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)


AttachmentMeta = Attachment  # 舊測試相容


class AttachmentOut(BaseModel):
    path: str
    exists: Optional[bool] = None

    def model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)


class EmailOptions(BaseModel):
    dry_run: Optional[bool] = None
    simulate_failure: Optional[str] = None  # pdf|smtp|db|template


class EmailRequest(BaseModel):
    subject: str
    body: str


class ActionResult(BaseModel):
    action_name: Optional[str] = Field(default=None, alias="action")
    subject: Optional[str] = None
    body: Optional[str] = None
    ok: bool = True
    to: List[str] = []
    cc: List[str] = []
    attachments: List[AttachmentOut] = []
    meta: Dict[str, Any] = {}
    request_id: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    duration_ms: Optional[int] = None
    logged_path: Optional[str] = None
    code: str = "OK"
    message: str = ""
    output: Optional[str] = None
    spent_ms: Optional[int] = None
    warnings: Optional[List[str]] = None
    dry_run: Optional[bool] = None

    @validator("spent_ms", pre=True, always=True)
    def _none_to_zero(cls, v):
        return 0 if v is None else int(v)

    class Config:
        allow_population_by_field_name = True

    @validator("attachments", pre=True)
    def _coerce_attachments(cls, v):
        out = []
        for a in v or []:
            if isinstance(a, str):
                out.append({"path": a, "exists": True})
            elif isinstance(a, dict):
                out.append(a)
            else:
                out.append(a)
        return out
