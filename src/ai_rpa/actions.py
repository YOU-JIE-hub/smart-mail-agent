#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/actions.py
# 模組用途: 輸出/動作（寫檔、預留 webhook/email）
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

from ai_rpa.utils.logger import get_logger
log = get_logger("ACTIONS")

def write_json(data: Dict[str, Any], outdir: str, basename: str = "report") -> str:
    """
    將資料寫入 JSON 檔；回傳路徑。
    """
    Path(outdir).mkdir(parents=True, exist_ok=True)
    fp = Path(outdir) / f"{Path(basename).stem}.json"
    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("已輸出: %s", fp)
    return str(fp)
