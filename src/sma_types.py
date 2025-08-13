# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class AttachmentMeta(BaseModel):
    filename: Optional[str] = None
    content_type: Optional[str] = None
    path: Optional[str] = None
    size: Optional[int] = None  # bytes


class ActionResult(BaseModel):
    ok: bool = True
    action_name: str = Field(..., min_length=1)
    subject: Optional[str] = None
    body: Optional[str] = None
    to: List[str] = Field(default_factory=list)
    cc: List[str] = Field(default_factory=list)
    bcc: List[str] = Field(default_factory=list)
    attachments: List[Union[str, AttachmentMeta]] = Field(default_factory=list)

    # flags
    dry_run: Optional[bool] = None  # <-- 加入這行，讓 pydantic 不會濾掉

    # observability
    request_id: Optional[str] = None
    duration_ms: Optional[int] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)

    # error channel
    error_code: Optional[str] = None
    error_msg: Optional[str] = None

    # extension meta
    meta: Dict[str, Any] = Field(default_factory=dict)

    @validator("confidence")
    def _clamp_conf(cls, v):
        if v is None:
            return v
        try:
            return max(0.0, min(1.0, float(v)))
        except Exception:
            return None

    def to_dict(self) -> dict:
        return self.dict(exclude_none=True)
