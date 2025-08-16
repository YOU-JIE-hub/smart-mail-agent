from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def extract_fields(payload: dict[str, Any]) -> tuple[str, str, str]:
    """從各種鍵名中擷取 subject/body/sender，缺少時回空字串。"""
    subject = payload.get("subject") or payload.get("title") or ""
    body = payload.get("body") or payload.get("text") or payload.get("content") or ""
    sender = payload.get("sender") or payload.get("from") or payload.get("email") or ""
    return subject, body, sender


def write_classification_result(arg1: Any, arg2: Any) -> Path:
    """
    將分類結果寫成 JSON 檔。
    支援兩種呼叫方式：
      - write_classification_result(data: dict, path: str|Path)
      - write_classification_result(path: str|Path, data: dict)
    回傳實際寫出的檔案 Path。
    """
    # 判斷哪個是 path 哪個是 data
    if isinstance(arg1, str | Path) and not isinstance(arg2, str | Path):
        path, data = arg1, arg2
    else:
        data, path = arg1, arg2

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
