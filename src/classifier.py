from __future__ import annotations

import ast
import json
import re
from collections.abc import Mapping as AbcMapping
from collections.abc import Sequence as AbcSequence
from numbers import Number
from typing import Any

try:
    from smart_mail_agent.core.classifier import (
        IntentClassifier as _NewIntentClassifier,  # type: ignore
    )
except Exception:  # pragma: no cover
    _NewIntentClassifier = None  # type: ignore

# ---- 規則 / 同義詞 ----
GENERIC_LABELS = {"其他", "其它", "general", "generic", "unknown"}
QUOTE_PATTERNS = re.compile(r"(報價|詢價|quote|quotation)", re.I)
ALIAS_TO_CANONICAL = {
    "詢價": "業務接洽或報價",
    "報價": "業務接洽或報價",
    "報價需求": "業務接洽或報價",
    "報價詢問": "業務接洽或報價",
    "quote": "業務接洽或報價",
    "quotation": "業務接洽或報價",
}


# ---- helpers ----
def _coerce_text(
    *args: Any,
    text: str | None = None,
    subject: str | None = None,
    content: str | None = None,
    **_: Any,
) -> str:
    # 支援三種呼叫型態
    if text is None and args:
        if len(args) == 1 and isinstance(args[0], str):
            text = args[0]
        elif len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], str):
            subject, content = args[0], args[1]
    if text is not None:
        return str(text)
    subject = subject or ""
    content = content or ""
    return (subject + " " + content).strip()


def _num(x: Any, default: float = 1.0) -> float:
    try:
        if isinstance(x, Number):
            return float(x)
        return float(str(x))
    except Exception:
        return default


def _normalize_result(obj: Any) -> dict:
    # 1) Mapping
    if isinstance(obj, AbcMapping):
        m = dict(obj)
        label = str(m.get("predicted_label", m.get("label", "")))
        score = m.get("score", m.get("confidence", 1.0))
        sc = _num(score, 1.0)
        return {
            "predicted_label": label,
            "label": label,
            "score": sc,
            "confidence": sc,
            "raw": obj,
        }

    # 2) bytes/str -> try parse JSON/python literal; else當作純字串標籤
    if isinstance(obj, bytes | str):
        s = obj.decode() if isinstance(obj, bytes) else obj
        parsed: Any | None = None
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(s)
                break
            except Exception:
                parsed = None
        if isinstance(parsed, AbcMapping):
            return _normalize_result(parsed)
        if isinstance(parsed, AbcSequence) and not isinstance(
            parsed, bytes | bytearray | str
        ):
            if parsed and isinstance(parsed[0], AbcMapping):
                return _normalize_result(parsed[0])
            return _normalize_result(list(parsed))
        return {
            "predicted_label": s,
            "label": s,
            "score": 1.0,
            "confidence": 1.0,
            "raw": obj,
        }

    # 3) Sequence (list/tuple)
    if isinstance(obj, AbcSequence) and not isinstance(obj, bytes | bytearray | str):
        if obj and isinstance(obj[0], AbcMapping):
            d0 = dict(obj[0])
            label = str(d0.get("predicted_label", d0.get("label", "")))
            score = d0.get("score", d0.get("confidence", 1.0))
            sc = _num(score, 1.0)
            return {
                "predicted_label": label,
                "label": label,
                "score": sc,
                "confidence": sc,
                "raw": obj,
            }
        # (label, score)
        label = str(obj[0]) if obj else ""
        sc = _num(obj[1], 1.0) if len(obj) > 1 else 1.0
        return {
            "predicted_label": label,
            "label": label,
            "score": sc,
            "confidence": sc,
            "raw": obj,
        }

    # 4) fallback
    s = str(obj)
    return {
        "predicted_label": s,
        "label": s,
        "score": 1.0,
        "confidence": 1.0,
        "raw": obj,
    }


def _alias_canonicalize(res: dict) -> dict:
    out = dict(res)
    lbl = str(out.get("predicted_label", out.get("label", ""))).strip()
    if not lbl:
        return out
    key = lbl.casefold() if isinstance(lbl, str) and lbl.isascii() else lbl
    canon = ALIAS_TO_CANONICAL.get(key) or ALIAS_TO_CANONICAL.get(lbl)
    if canon:
        out["predicted_label"] = canon
        out["label"] = canon
    else:
        out.setdefault("label", lbl)
        out.setdefault("predicted_label", lbl)
    return out


def _maybe_override(text: str, res: dict) -> dict:
    out = dict(res)
    if out.get("predicted_label") in GENERIC_LABELS and QUOTE_PATTERNS.search(
        text or ""
    ):
        out["predicted_label"] = "業務接洽或報價"
        out["label"] = "業務接洽或報價"
    else:
        lbl = out.get("predicted_label", out.get("label", ""))
        out.setdefault("label", lbl)
        out.setdefault("predicted_label", lbl)
    out.setdefault("confidence", _num(out.get("score", 1.0), 1.0))
    out.setdefault("score", _num(out.get("confidence", 1.0), 1.0))
    return out


class IntentClassifier:
    def __init__(
        self, model_path: str | None = None, *, pipeline_override=None, **kwargs: Any
    ):
        self._use_shim = pipeline_override is not None and (not model_path)
        if self._use_shim:
            self._pipe = pipeline_override
            self._impl = None
        else:
            if _NewIntentClassifier is None:
                raise RuntimeError("smart_mail_agent.core.classifier not available")
            self._impl = _NewIntentClassifier(model_path, **kwargs)

    def classify(
        self,
        *args: Any,
        text: str | None = None,
        subject: str | None = None,
        content: str | None = None,
        **kw: Any,
    ) -> dict:
        return self._run_and_normalize(
            _coerce_text(*args, text=text, subject=subject, content=content, **kw)
        )

    def predict(self, *args: Any, **kw: Any) -> dict:
        return self.classify(*args, **kw)

    __call__ = classify

    def _run_and_normalize(self, text: str) -> dict:
        runner = (
            self._pipe
            if self._use_shim
            else (
                getattr(self._impl, "classify", None)
                or getattr(self._impl, "predict", None)
                or self._impl
            )
        )
        # 寬鬆呼叫協定：text= / 位置參數 / subject+content
        try:
            raw = runner(text=text)  # type: ignore[misc]
        except TypeError:
            try:
                raw = runner(text)  # type: ignore[misc,call-arg]
            except TypeError:
                raw = runner(subject=text, content="")  # type: ignore[misc,call-arg]

        res = _normalize_result(raw)
        res = _alias_canonicalize(res)
        res = _maybe_override(text, res)
        return res
