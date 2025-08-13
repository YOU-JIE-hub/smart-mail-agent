#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, root_validator, validator

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

    # 兼容 pydantic v2 介面
    def model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)


# 與舊測試相容
AttachmentMeta = Attachment


# 測試矩陣會期望 attachments 的元素擁有 .path 屬性（而不是 dict）
class AttachmentOut(BaseModel):
    path: str
    exists: Optional[bool] = None

    # 兼容 pydantic v2 介面
    def model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)


class EmailOptions(BaseModel):
    dry_run: Optional[bool] = None
    simulate_failure: Optional[str] = None  # pdf|smtp|db|template


class EmailRequest(BaseModel):
    subject: str
    body: str
    sender: Optional[str] = Field(None, alias="from")
    predicted_label: Optional[str] = ""
    confidence: Optional[float] = None
    attachments: List[Attachment] = []
    options: Optional[EmailOptions] = None

    class Config:
        allow_population_by_field_name = True
        extra = "allow"

    @validator("confidence", pre=True, always=True)
    def _conf_default(cls, v):
        return -1.0 if v is None else float(v)

    @validator("predicted_label", pre=True, always=True)
    def _label_norm(cls, v):
        if not v:
            return ""
        return str(v).strip().lower()


class ActionResult(BaseModel):
    # 允許用 'action' 餵入
    action_name: str = Field(..., alias="action")
    subject: Optional[str] = ""
    # 允許用 'output' 餵入
    body: str = Field("", alias="output")
    ok: bool = True
    to: List[str] = []
    cc: List[str] = []
    attachments: List[AttachmentOut] = []
    meta: Dict[str, Any] = {}
    request_id: Optional[str] = None
    intent: Optional[str] = None
    confidence: float = -1.0
    # 允許用 'spent_ms' 餵入；None -> 0
    duration_ms: Optional[int] = Field(0, alias="spent_ms")
    logged_path: Optional[str] = None
    # 測試直接讀取 ar.code / ar.message
    code: Optional[str] = "OK"
    message: Optional[str] = ""

    class Config:
        allow_population_by_field_name = True
        extra = "allow"

    @root_validator(pre=True)
    def _compat_old_names(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # 舊欄位映射到新欄位
        if "code" not in values and "error_code" in values:
            values["code"] = values.get("error_code")
        if "message" not in values and "error_msg" in values:
            values["message"] = values.get("error_msg")
        if "action_name" not in values and "action" in values:
            values["action_name"] = values.get("action")
        return values

    @validator("duration_ms", pre=True, always=True)
    def _dur_default(cls, v):
        if v is None:
            return 0
        try:
            return int(v)
        except Exception:
            return 0

    @validator("attachments", pre=True, always=True)
    def _attachments_coerce(cls, v):
        """
        接受：
          - ["path1", "path2"]  →  [{"path": "path1"}, {"path": "path2"}]
          - [{"path": "...", "exists": true}, {...}] → 保持
          - 舊格式 [{"filename": "...", ...}] → 以 filename 當 path
        """
        out = []
        for item in v or []:
            if isinstance(item, str):
                out.append({"path": item})
            elif isinstance(item, dict):
                if "path" in item:
                    out.append({"path": item.get("path"), "exists": item.get("exists")})
                elif "filename" in item:
                    out.append({"path": item.get("filename"), "exists": item.get("exists")})
                else:
                    # 最後嘗試：把整個 dict 轉字串當 path
                    out.append({"path": str(item)})
            else:
                out.append({"path": str(item)})
        return out


def normalize_request(raw: Dict[str, Any]) -> EmailRequest:
    return EmailRequest.parse_obj(raw)


def ensure_reply_prefix(subject: str) -> str:
    prefix = "[自動回覆] "
    return subject if subject.startswith(prefix) else f"{prefix}{subject}"


def normalize_result(result: Dict[str, Any]) -> ActionResult:
    intent = str(result.get("intent") or result.get("action_name") or "other")
    subject = str(result.get("subject") or "")
    if intent.startswith("reply_") or intent in {"sales_inquiry", "complaint", "reply_general"}:
        subject = ensure_reply_prefix(subject) if subject else "[自動回覆] "
    result["subject"] = subject
    if not result.get("action_name"):
        result["action_name"] = intent
    result.setdefault("ok", True)
    result.setdefault("to", [])
    result.setdefault("cc", [])
    result.setdefault("meta", {})
    result.setdefault("attachments", [])
    result.setdefault("confidence", -1.0)
    result.setdefault("duration_ms", 0)
    return ActionResult.parse_obj(result)


__all__ = [
    "Attachment",
    "AttachmentMeta",
    "AttachmentOut",
    "EmailOptions",
    "EmailRequest",
    "ActionResult",
    "normalize_request",
    "normalize_result",
    "ensure_reply_prefix",
    "ALLOWED_INTENTS",
]
