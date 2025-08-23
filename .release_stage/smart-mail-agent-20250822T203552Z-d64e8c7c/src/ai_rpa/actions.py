#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/actions.py
# 模組用途: 輸出與動作（示範：寫 JSON；未直接產 PDF，但預留 PDF 路徑與字型）
from __future__ import annotations
from typing import Any, Dict
from pathlib import Path
import json
from ai_rpa.utils.logger import get_logger

log = get_logger("ACTIONS")

def write_json(data: Dict[str, Any], output_path: str) -> str:
    """
    將結果寫入 JSON 檔案。回傳輸出路徑。
    """
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info("已輸出: %s", str(p))
    return str(p)
