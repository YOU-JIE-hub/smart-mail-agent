#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/ocr.py
# 模組用途: OCR（與 PDF 設計相符）
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from PIL import Image
try:
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore

from ai_rpa.utils.logger import get_logger
log = get_logger("OCR")

def run_ocr(image_path: str) -> Dict[str, Any]:
    """
    對單一影像執行 OCR，失敗時回傳錯誤訊息。
    參數:
        image_path: 影像路徑
    回傳:
        {"ok": bool, "text": str, "error": str|None}
    """
    p = Path(image_path)
    if not p.exists():
        return {"ok": False, "text": "", "error": f"file not found: {image_path}"}
    if pytesseract is None:
        log.warning("pytesseract 未安裝，略過 OCR")
        return {"ok": True, "text": "", "error": None}
    try:
        text = pytesseract.image_to_string(Image.open(str(p)))
        log.info("OCR 完成: %s", p.name)
        return {"ok": True, "text": text, "error": None}
    except Exception as e:  # pragma: no cover
        return {"ok": False, "text": "", "error": str(e)}
