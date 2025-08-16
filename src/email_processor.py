from __future__ import annotations
import json
from pathlib import Path
from typing import Tuple, Dict, Any

def extract_fields(payload: Dict[str, Any]) -> Tuple[str, str, str]:
    subject = payload.get("subject") or payload.get("title") or ""
    body = payload.get("body") or payload.get("text") or ""
    sender = payload.get("from") or payload.get("sender") or ""
    return subject, body, sender

def write_classification_result(*args, **kwargs) -> str:
    # 支援兩種呼叫法：
    # 1) write_classification_result(result_dict, path)
    # 2) write_classification_result(path, label, score, extra={...}, confidence=...)
    if args and isinstance(args[0], dict):
        result, path = args[0], Path(args[1])
    else:
        path, label, score = Path(args[0]), str(args[1]), float(args[2])
        result = {"label": label, "score": score}
        if "confidence" in kwargs:
            result["confidence"] = float(kwargs["confidence"])
        extra = kwargs.get("extra") or {}
        if isinstance(extra, dict):
            result.update(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
