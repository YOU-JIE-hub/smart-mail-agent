from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from smart_mail_agent.utils.logger import get_logger

logger = get_logger("ai_rpa.actions")


def write_json(data: Dict[str, Any], output_path: str | Path) -> Path:
    """
    將結果寫入完整檔名（統一介面）。
    若父目錄不存在會自動建立。
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("已輸出結果：%s", out)
    return out
