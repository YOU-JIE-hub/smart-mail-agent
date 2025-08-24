#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/nlp.py
# 模組用途: NLP/LLM 分析（預設離線關鍵詞；可切換 transformers）
from __future__ import annotations

from typing import Any, Dict, List

from ai_rpa.utils.logger import get_logger

log = get_logger("NLP")

KEYWORDS = {
    "refund": ["退款", "退貨", "發票"],
    "complaint": ["抱怨", "投訴", "不滿"],
    "sales": ["報價", "合作", "詢價"],
}


def analyze_text(texts: List[str], model: str = "offline-keyword") -> Dict[str, Any]:
    """
    對多段文字進行分析；預設採關鍵詞規則，以避免下載模型。
    回傳: {"labels":[...], "extracted":[...]}
    """
    if model == "offline-keyword":
        labels: List[str] = []
        for t in texts:
            lab = "other"
            for k, keys in KEYWORDS.items():
                if any(kw in t for kw in keys):
                    lab = k
                    break
            labels.append(lab)
        return {"labels": labels, "extracted": []}
    log.warning("未啟用 transformers，改用離線關鍵詞")
    return analyze_text(texts, model="offline-keyword")
