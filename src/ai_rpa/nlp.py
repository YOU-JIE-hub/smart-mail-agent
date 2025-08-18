#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/nlp.py
# 模組用途: NLP/LLM 分析（離線關鍵詞為預設；可選 transformers）
from __future__ import annotations
from typing import Dict, Any, List

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
    參數:
        texts: 文本列表
        model: "offline-keyword" 或 transformers pipeline 名稱
    回傳:
        {"labels":[...], "extracted":[...]}
    """
    if model == "offline-keyword":
        labels = []
        for t in texts:
            lab = "other"
            for k, keys in KEYWORDS.items():
                if any(kw in t for kw in keys):
                    lab = k
                    break
            labels.append(lab)
        return {"labels": labels, "extracted": []}

    # 可擴充: 若使用 transformers，於此載入 pipeline（略）
    log.warning("未啟用 transformers，改用離線關鍵詞")
    return analyze_text(texts, model="offline-keyword")
