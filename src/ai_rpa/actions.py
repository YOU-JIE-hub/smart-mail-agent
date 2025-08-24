
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("ai_rpa.actions")

def _to_jsonable(obj: Any) -> Any:
    # 遞迴把不可序列化型別（Path、set 等）變成可序列化
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    return obj

def write_json(data: Dict[str, Any], output_path: str | Path) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    safe = _to_jsonable(dict(data or {}))
    # 若沒有 steps，依既有結果鍵自動補一份（讓 legacy 測試能檢查 'nlp'）
    if "steps" not in safe:
        ordered = [k for k in ("ocr", "scrape", "classify_files", "nlp", "actions") if k in safe]
        safe = {"steps": ordered, **safe}

    out.write_text(json.dumps(safe, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("已輸出結果：%s", out)
    return out
