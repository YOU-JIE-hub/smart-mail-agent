from __future__ import annotations

from collections.abc import Mapping
from importlib import import_module as _import_module
from typing import Any, Iterable

# 盡量代理到核心模組；如果核心沒有 normalize_result，改用本地實作
try:
    _core = _import_module("smart_mail_agent.core.sma_types")
except Exception:  # 核心不存在也能工作
    _core = None  # type: ignore[assignment]


def _as_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        v = default
    # clamp to [0, 1] — 多數測試/用例期望機率範圍
    if v != v:  # NaN
        return default
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def _as_str(x: Any) -> str:
    return "" if x is None else str(x)


def _to_mapping(obj: Any) -> Mapping[str, Any] | None:
    # 支援 pydantic v1/v2、dataclass 或一般物件
    if isinstance(obj, Mapping):
        return obj
    for attr in ("model_dump", "dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                d = fn()  # type: ignore[misc]
                if isinstance(d, Mapping):
                    return d
            except Exception:
                pass
    if hasattr(obj, "__dict__") and not isinstance(obj, (str, bytes)):
        return vars(obj)
    return None


def _pick(d: Mapping[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for k in keys:
        if k in d:
            return d[k]
    return default


# --- 本地通用實作：把常見輸入格式標準化成 {label, score, extra} ---
def _normalize_result_fallback(obj: Any) -> dict[str, Any]:
    label_keys = ("label", "predicted_label", "prediction", "class", "category")
    score_keys = ("score", "confidence", "prob", "probability")
    extra_keys = ("extra", "extras", "meta", "details", "info", "data")

    label: str = ""
    score: float = 0.0
    extra: Mapping[str, Any] | None = None

    if isinstance(obj, (list, tuple)):
        label = _as_str(obj[0] if len(obj) >= 1 else "")
        score = _as_float(obj[1] if len(obj) >= 2 else 0.0)
        maybe_extra = obj[2] if len(obj) >= 3 else None
        extra = maybe_extra if isinstance(maybe_extra, Mapping) else None
    else:
        d = _to_mapping(obj) or {}
        label = _as_str(_pick(d, label_keys, ""))
        score = _as_float(_pick(d, score_keys, 0.0))
        maybe_extra = _pick(d, extra_keys, None)
        extra = maybe_extra if isinstance(maybe_extra, Mapping) else None

    return {"label": label, "score": score, "extra": dict(extra or {})}


# 嘗試從核心拿到 normalize_result；拿不到就用 fallback
if _core is not None:
    for name in ("normalize_result", "normalize", "normalize_extra_result"):
        fn = getattr(_core, name, None)
        if callable(fn):
            normalize_result = fn  # type: ignore[assignment]
            break
    else:
        normalize_result = _normalize_result_fallback  # type: ignore[assignment]
else:
    normalize_result = _normalize_result_fallback  # type: ignore[assignment]


# 其餘名稱盡量代理到核心（若存在）
def __getattr__(name: str):
    if _core is None:
        raise AttributeError(name)
    return getattr(_core, name)


def __dir__():
    base = list(globals().keys())
    if _core is not None:
        base += [n for n in dir(_core) if not n.startswith("_")]
    return sorted(set(base))


__all__ = ["normalize_result"]
