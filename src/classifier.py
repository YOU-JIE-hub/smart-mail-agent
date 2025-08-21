from __future__ import annotations
from typing import Any, Optional
import os
import re

# 低信心門檻（可用環境變數覆寫）
FALLBACK_CONF = float(os.getenv("SMA_INTENT_LOWCONF", "0.5"))

# 嘗試載入正式實作（可能不存在）
try:
    from smart_mail_agent.inference_classifier import classify_intent as _base_classify  # type: ignore
except Exception:
    _base_classify = None  # type: ignore[assignment]

try:
    from smart_mail_agent.inference_classifier import IntentClassifier as _RealIC  # type: ignore
except Exception:
    _RealIC = None  # type: ignore[assignment]


def _normalize_result(res: Any) -> dict:
    """把各式輸出統一為 {predicted_label, label, confidence, score}。"""
    # dict 形狀
    if isinstance(res, dict):
        out = dict(res)
        label = (
            out.get("predicted_label")
            or out.get("label")
            or out.get("intent")
            or out.get("category")
        )
        conf = (
            out.get("confidence")
            or out.get("score")
            or out.get("prob")
            or out.get("probability")
        )
        try:
            conf = float(conf) if conf is not None else 1.0  # type: ignore[assignment]
        except Exception:
            conf = 1.0  # type: ignore[assignment]
        if label is None:
            label = "unknown"
        out["predicted_label"] = str(label)
        out["label"] = out["predicted_label"]
        out["confidence"] = conf
        out.setdefault("score", conf)
        return out

    # list/tuple: [(label, score)]、[label, score]、[{"label":..,"score":..}, ...]
    if isinstance(res, (list, tuple)):
        if not res:
            return {"predicted_label": "unknown", "label": "unknown", "confidence": 0.0, "score": 0.0}
        first = res[0]
        if isinstance(first, dict):
            return _normalize_result(first)
        if isinstance(first, (list, tuple)) and first:
            label = first[0]
            score = first[1] if len(first) > 1 else 1.0
        else:
            label = first
            score = res[1] if len(res) > 1 else 1.0
        try:
            conf = float(score)
        except Exception:
            conf = 1.0
        lab = str(label)
        return {"predicted_label": lab, "label": lab, "confidence": conf, "score": conf}

    # 純字串 → 當作 label，信心 1.0
    if isinstance(res, str):
        return {"predicted_label": res, "label": res, "confidence": 1.0, "score": 1.0}

    # 其他 → unknown
    return {"predicted_label": "unknown", "label": "unknown", "confidence": 0.0, "score": 0.0}


def _is_generic(subject: str, content: str) -> bool:
    txt = f"{subject or ''} {content or ''}".strip()
    if len(txt) < 8:
        return True
    # 全 ASCII 且詞數很少 → 泛用問候
    if all(ord(c) < 128 for c in txt) and len(txt.split()) <= 3:
        return True
    return False


def _apply_fallback(res: dict, subject: str, content: str) -> dict:
    """低信心且泛用文字時才回退 label→『其他』，並保留原 confidence/score。"""
    out = dict(res)
    try:
        conf = float(out.get("confidence", out.get("score", 0.0)) or 0.0)
    except Exception:
        conf = 0.0
    out["confidence"] = conf
    out.setdefault("score", conf)
    if conf < FALLBACK_CONF and _is_generic(subject, content):
        out["predicted_label"] = "其他"
        out["label"] = "其他"
    else:
        # 確保 alias 存在
        out.setdefault("label", out.get("predicted_label", "unknown"))
    return out


# 關鍵詞規則：命中即覆蓋為「業務接洽或報價」
RE_QUOTE = re.compile(
    r"(報價|合作|採購|方案|價格|詢價|比價|quotation|quote|pricing|price)",
    re.I,
)
def _apply_rules(res: dict, subject: str, content: str) -> dict:
    txt = f"{subject or ''} {content or ''}"
    if RE_QUOTE.search(txt):
        out = dict(res)
        out["predicted_label"] = "業務接洽或報價"
        out["label"] = "業務接洽或報價"
        return out
    # 仍確保 alias 存在
    if "label" not in res and "predicted_label" in res:
        res = dict(res)
        res["label"] = res["predicted_label"]
    return res


def _safe_call_base(subject: str, content: str, sender: Optional[str] = None) -> dict:
    """呼叫底層 classify_intent（若有），然後做正規化→回退→規則。"""
    if _base_classify is None:
        return _apply_rules(
            _apply_fallback(
                _normalize_result({"predicted_label": "unknown", "confidence": 0.0}),
                subject,
                content,
            ),
            subject,
            content,
        )
    # 相容多種簽名
    raw = None
    for caller in (
        lambda: _base_classify(subject, content, sender),
        lambda: _base_classify(subject, content),
        lambda: _base_classify(subject=subject, content=content, sender=sender),
        lambda: _base_classify(subject=subject, content=content),
    ):
        try:
            raw = caller()
            break
        except TypeError:
            continue
    res = _normalize_result(raw)
    res = _apply_fallback(res, subject, content)
    res = _apply_rules(res, subject, content)
    return res


def classify_intent(subject: str, content: str, sender: Optional[str] = None, **_: Any) -> dict:
    """模組層函式：吞掉未知 kwargs，走 base + 規則/回退流程。"""
    return _safe_call_base(subject, content, sender)


if _RealIC is None:
    class IntentClassifier:
        """兼容用分類器：
        - 接受任意 kwargs（如 model_path, pipeline_override）
        - 若提供 pipeline_override（callable），優先使用它
        - 回傳一律正規化→回退→規則
        """
        def __init__(self, **kwargs):
            self.kwargs = dict(kwargs)

        def classify(self, subject: str, content: str, sender: Optional[str] = None, **kwargs):
            merged = {**self.kwargs, **kwargs}
            override = merged.get("pipeline_override")
            if callable(override):
                # 相容多種簽名：(s,c,sen) → (s,c) → (s) → kwargs
                raw = None
                for caller in (
                    lambda: override(subject, content, sender),
                    lambda: override(subject, content),
                    lambda: override(subject),
                    lambda: override(subject=subject, content=content, sender=sender),
                    lambda: override(subject=subject, content=content),
                    lambda: override(subject=subject),
                ):
                    try:
                        raw = caller()
                        break
                    except TypeError:
                        continue
                res = _normalize_result(raw)
                res = _apply_fallback(res, subject, content)
                res = _apply_rules(res, subject, content)
                return res

            # 沒有 override → 走底層實作
            return _safe_call_base(subject, content, sender)

        # 別名
        def predict(self, *a, **k):
            return self.classify(*a, **k)

        def __call__(self, *a, **k):
            return self.classify(*a, **k)
else:
    # 若專案已有正式類別，就直接導出
    IntentClassifier = _RealIC  # type: ignore[misc]

__all__ = ["IntentClassifier", "classify_intent"]
