from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any, Dict

# 純 Python、無外部依賴的 orchestrator。以 DI 傳入規則與模型。
# 規範：
#   - rule_fn(text) -> bool | dict（若 dict 則須有 "is_spam": bool）
#   - model_fn(text) -> dict | tuple | list 允許多形：
#         dict: {"label": "SPAM"|"HAM", "score": float}
#         tuple/list: (label, score) 或 [{"label":..., "score":...}]
#   - 例外安全：model_fn 失敗時 fallback 至規則結果
#   - 決策：
#       1) 規則為 True → 直接 spam（reason="rule"）
#       2) 規則為 False → 看模型是否 label=SPAM 且 score>=model_threshold
#       3) 無法解析模型 → 規則結果
#       4) 邊界：score==threshold 視為命中（保守）
#
#   - 之後動作：choose_action
#       SPAM → "drop"
#       非 SPAM → "route_to_inbox"
#       若 is_borderline=True → "review"
#
@dataclass(frozen=True)
class OrchestrateResult:
    is_spam: bool
    is_borderline: bool
    source: str          # "rule" | "model" | "fallback"
    rule_value: bool
    model_label: str | None
    model_score: float | None
    action: str          # "drop" | "route_to_inbox" | "review"
    extra: Dict[str, Any]

def _as_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, dict) and "is_spam" in v:
        return bool(v.get("is_spam"))
    return bool(v)

def _parse_model_ret(ret: Any) -> tuple[str | None, float | None]:
    # 支援 dict / (label, score) / [{"label":..., "score":...}]
    if ret is None:
        return None, None
    if isinstance(ret, dict):
        return ret.get("label"), float(ret.get("score")) if ret.get("score") is not None else None
    if isinstance(ret, (list, tuple)) and ret:
        head = ret[0]
        tail = ret[1] if len(ret) > 1 else None
        if isinstance(head, dict):
            return head.get("label"), float(head.get("score")) if head.get("score") is not None else (float(tail) if isinstance(tail, (int, float)) else None)
        if isinstance(head, str):
            return head, float(tail) if isinstance(tail, (int, float)) else None
    return None, None

def choose_action(is_spam: bool, is_borderline: bool) -> str:
    if is_borderline:
        return "review"
    return "drop" if is_spam else "route_to_inbox"

def orchestrate(
    text: str,
    rule_fn: Callable[[str], Any],
    model_fn: Callable[[str], Any],
    *,
    model_threshold: float = 0.6,
) -> OrchestrateResult:
    rule_hit = _as_bool(rule_fn(text))
    if rule_hit:
        return OrchestrateResult(
            is_spam=True,
            is_borderline=False,
            source="rule",
            rule_value=True,
            model_label=None,
            model_score=None,
            action=choose_action(True, False),
            extra={},
        )
    # 規則未命中 → 交給模型；例外安全
    try:
        m_label, m_score = _parse_model_ret(model_fn(text))
    except Exception as e:  # pragma: no cover - 但我們在測試會覆蓋
        return OrchestrateResult(
            is_spam=rule_hit,
            is_borderline=False,
            source="fallback",
            rule_value=rule_hit,
            model_label=None,
            model_score=None,
            action=choose_action(rule_hit, False),
            extra={"model_error": repr(e)},
        )
    is_spam = (m_label or "").upper() == "SPAM" and (m_score or 0.0) >= model_threshold
    is_borderline = (m_label or "").upper() == "SPAM" and (m_score or 0.0) == model_threshold
    return OrchestrateResult(
        is_spam=is_spam,
        is_borderline=is_borderline,
        source="model",
        rule_value=False,
        model_label=m_label,
        model_score=m_score,
        action=choose_action(is_spam, is_borderline),
        extra={},
    )
