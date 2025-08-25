from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("ai_rpa.actions")


def _to_jsonable(obj: Any) -> Any:
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(x) for x in obj]
    return obj


def write_json(data: Dict[str, Any], output_path: str | Path) -> Path:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # auto steps if sections present
    steps = list(
        dict.fromkeys(
            [k for k in ("ocr", "scrape", "classify_files", "nlp", "actions") if k in data]
        )
    )
    envelope = {"ok": True, "artifacts": {"output_path": str(p)}}
    if "steps" not in data and steps:
        data = {**data, "steps": steps}
    out = {**envelope, **_to_jsonable(data)}
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("已輸出結果：%s", p)
    return p
