#!/usr/bin/env python3
# 檔案位置: src/inference_classifier.py
# 模組用途: 離線安全的意圖分類入口（無 torch 依賴），供 ingestion/email_processor 等模組呼叫。
# 介面: classify_intent(subject: str, content: str) -> dict
#
# 設計重點
# 1) 「可被匯入」是第一優先：不得在 import 階段觸發沉重依賴或網路下載。
# 2) 以關鍵字啟發式實作，讓單元/合約測試在 OFFLINE=1 下穩定通過。
# 3) 回傳結構與早期約定相容：{'label': str, 'confidence': float, 'reason': str}
from __future__ import annotations

from dataclasses import dataclass

__all__ = ["classify_intent"]


@dataclass(frozen=True)
class IntentResult:
    label: str
    confidence: float
    reason: str


# 六大類別關鍵字（可依實際語料擴充）
_BUCKETS: dict[str, tuple[str, ...]] = {
    "technical_support": (
        "退款",
        "退貨",
        "瑕疵",
        "故障",
        "維修",
        "錯誤",
        "重設",
        "帳號",
        "登入",
        "密碼",
        "bug",
        "error",
        "無法",
        "崩潰",
        "當機",
        "掛掉",
    ),
    "information_modification": (
        "修改",
        "變更",
        "更換",
        "資料更新",
        "更正",
        "更新資料",
        "更改",
        "地址變更",
        "電話變更",
    ),
    "process_inquiry": (
        "流程",
        "規則",
        "辦理",
        "申請",
        "步驟",
        "方法",
        "怎麼",
        "如何",
        "多久",
        "期限",
        "辦法",
        "SLA",
        "SOP",
    ),
    "complaint": (
        "客訴",
        "抱怨",
        "不滿",
        "無法接受",
        "投訴",
        "申訴",
        "太慢",
        "差勁",
        "惡劣",
        "拖延",
    ),
    "business_inquiry": (
        "報價",
        "詢問",
        "合作",
        "採購",
        "報價單",
        "試用",
        "po",
        "下單",
        "商務",
        "合作邀約",
    ),
    "others": tuple(),
}


def _normalize_text(s: str) -> str:
    return (s or "").strip().lower()


def _score(subject: str, content: str) -> IntentResult:
    text = f"{_normalize_text(subject)}\n{_normalize_text(content)}"
    best_label = "others"
    best_hits = 0
    hit_reasons: list[str] = []

    for label, kws in _BUCKETS.items():
        if not kws:
            continue
        hits = [kw for kw in kws if kw.lower() in text]
        if len(hits) > best_hits:
            best_label = label
            best_hits = len(hits)
            hit_reasons = hits

    if best_label == "others":
        return IntentResult(
            label="others", confidence=0.34, reason="no strong keyword match"
        )

    if best_hits >= 3:
        conf = 0.92
    elif best_hits == 2:
        conf = 0.82
    else:
        conf = 0.70
    return IntentResult(
        label=best_label, confidence=conf, reason=f"keywords={','.join(hit_reasons)}"
    )


def classify_intent(subject: str, content: str) -> dict:
    """
    依主旨與內文回傳分類結果（離線安全）。
    回傳:
        dict:
            - label: technical_support / information_modification / process_inquiry / complaint / business_inquiry / others
            - confidence: 0~1
            - reason: 字串，命中關鍵字或無命中
    """
    if not (subject or content):
        raise ValueError("empty subject and content")

    res = _score(subject, content)
    return {
        "label": res.label,
        "confidence": float(res.confidence),
        "reason": res.reason,
    }


if __name__ == "__main__":
    examples = [
        ("請問退款流程", "商品有瑕疵，想辦理退貨與退款"),
        ("變更聯絡地址", "需要更新我的電話與地址"),
        ("合作詢問", "想索取報價單並討論合作"),
        ("沒有任何關鍵字", "這是一封一般測試郵件"),
    ]
    for s, c in examples:
        print(s, "=>", classify_intent(s, c))
