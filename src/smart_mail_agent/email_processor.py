from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

__all__ = ["extract_fields", "write_classification_result"]

_SYNS_SUBJ = ("subject", "title", "subj")
_SYNS_BODY = ("body", "content", "text", "msg", "message")
_SYNS_FROM = ("from", "sender", "email")


def _pick(d: Dict[str, Any], keys: Iterable[str]) -> str:
    for k in keys:
        if k in d and d[k] is not None:
            return str(d[k])
    return ""


def extract_fields(data: Dict[str, Any] | Tuple[str, str, str]) -> Tuple[str, str, str]:
    """
    輸入 dict（多種鍵名同義詞）或三元 tuple，統一回傳 (subject, body, sender) 的 tuple。
    """
    if isinstance(data, tuple) and len(data) == 3:
        s, b, f = data
        return (str(s or ""), str(b or ""), str(f or ""))
    if isinstance(data, dict):
        s = _pick(data, _SYNS_SUBJ)
        b = _pick(data, _SYNS_BODY)
        f = _pick(data, _SYNS_FROM)
        return (s, b, f)
    # 其他型別容錯
    return ("", "", "")


def write_classification_result(a: Any, b: Any) -> str:
    """
    允許兩種呼叫：
      write_classification_result(data: dict, path: str|Path)
      write_classification_result(path: str|Path, data: dict)
    回傳檔案實際路徑字串。
    """
    if isinstance(a, (str, Path)) and isinstance(b, dict):
        path, data = Path(a), b
    elif isinstance(b, (str, Path)) and isinstance(a, dict):
        path, data = Path(b), a
    else:
        raise TypeError("usage: write_classification_result(data, path) or (path, data)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)
