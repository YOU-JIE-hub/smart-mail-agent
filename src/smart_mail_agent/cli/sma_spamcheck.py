#!/usr/bin/env python3
# 檔案位置: src/smart_mail_agent/cli/sma_spamcheck.py
from __future__ import annotations

import argparse
import inspect
import os
import sys
from pathlib import Path
from typing import Any

CANDIDATE_METHODS = (
    "check",
    "run",
    "predict",
    "evaluate",
    "classify",
    "analyze",
    "infer",
    "decide",
    "filter",
    "process",
)
SPAM_KEYS = ("is_spam", "spam", "isSpam", "label", "tag", "prediction", "result")
SCORE_KEYS = ("score", "prob", "probability", "confidence", "spam_score", "spam_prob")
REASON_KEYS = ("reason", "why", "message", "explain", "explanation", "detail")


def _ensure_src_on_syspath() -> None:
    cwd_src = Path.cwd() / "src"
    if cwd_src.exists():
        sys.path.insert(0, str(cwd_src))
        return
    here = Path(__file__).resolve()
    for up in [here] + list(here.parents):
        cand = up if up.is_dir() else up.parent
        if (cand / "src").exists():
            sys.path.insert(0, str(cand / "src"))
            return


def _import_orch_module():
    _ensure_src_on_syspath()
    try:
        import importlib

        return importlib.import_module("spam.spam_filter_orchestrator")
    except Exception:
        try:
            return importlib.import_module("smart_mail_agent.spam.spam_filter_orchestrator")
        except Exception:
            return None


def _find_orch_class(mod) -> type | None:
    if mod is None:
        return None
    # 優先使用明確命名
    cls = getattr(mod, "SpamFilterOrchestrator", None)
    if inspect.isclass(cls):
        return cls
    # 次選：找看起來像 orchestrator 的類
    cand = [v for k, v in mod.__dict__.items() if inspect.isclass(v) and ("Orchestrator" in v.__name__ or "Spam" in v.__name__)]
    if len(cand) == 1:
        return cand[0]
    return None


def _instantiate(cls) -> Any | None:
    if cls is None:
        return None
    # 盡量無參數建構；失敗則放棄（避免互動）
    try:
        return cls()
    except Exception:
        try:
            # 嘗試以常見 kwargs（若類別可接受）
            sig = inspect.signature(cls)
            kwargs = {}
            for name, p in sig.parameters.items():
                if p.default is not inspect._empty:
                    continue
                # 不猜測外部資源，統一略過必填參數，改用空字典
            return cls(**kwargs)
        except Exception:
            return None


def _call_with_adaptation(target, subject: str, content: str, sender: str) -> tuple[bool, float, str]:
    """
    嘗試多種方法與參數組合；將返回值正規化為 (is_spam, score, reason)。
    score 預設 0.0；若返回值為機率或分數則採用；若僅布林則分數以 1.0/0.0 表示。
    """
    # 1) 可能的呼叫目標（物件方法、類別方法、模組函式）
    callables: dict[str, Any] = {}

    # 物件／類別方法
    for name in CANDIDATE_METHODS:
        fn = getattr(target, name, None)
        if callable(fn):
            callables[name] = fn

    # 若 target 是模組，加入模組層函式
    if inspect.ismodule(target):
        for name in CANDIDATE_METHODS:
            fn = getattr(target, name, None)
            if callable(fn):
                callables[name] = fn

        # 也許模組內有「最佳入口」函式名稱
        for name in ("main", "orchestrate", "detect_spam", "is_spam"):
            fn = getattr(target, name, None)
            if callable(fn) and name not in callables:
                callables[name] = fn

    # 若完全沒有可呼叫目標，直接失敗
    if not callables:
        raise AttributeError("找不到可用的方法（check/run/predict/...）")

    # 2) 嘗試多種參數映射
    payloads = [
        {"subject": subject, "content": content, "sender": sender},
        {"subject": subject, "body": content, "sender": sender},
        {"title": subject, "text": content, "sender": sender},
        {"text": f"{subject}\n{content}", "sender": sender},
        {"message": f"{subject}\n{content}", "sender": sender},
        (subject, content, sender),
        (subject, content),
        (f"{subject}\n{content}",),
    ]

    # 3) 逐一嘗試呼叫與解析
    last_err: Exception | None = None
    for name, fn in callables.items():
        for pay in payloads:
            try:
                # 按簽名過濾 kwargs
                if isinstance(pay, dict):
                    sig = inspect.signature(fn)
                    kwargs = {k: v for k, v in pay.items() if k in sig.parameters}
                    # 若全被過濾掉，且函式至少接受一個參數，改用合併文本
                    if not kwargs and len(sig.parameters) >= 1:
                        kwargs = {"text": f"{subject}\n{content}"}
                    res = fn(**kwargs)
                else:
                    # 序列參數呼叫
                    res = fn(*pay)
                is_spam, score, reason = _normalize(res)
                return is_spam, score, reason or f"via {name}"
            except Exception as e:
                last_err = e
                continue
    raise RuntimeError(f"無法成功呼叫 orchestrator：{last_err!r}")


def _normalize(res: Any) -> tuple[bool, float, str]:
    thr = float(os.getenv("SPAM_THRESHOLD", "0.5"))
    # dict
    if isinstance(res, dict):
        is_spam = _pick_bool(res, SPAM_KEYS, default=None)
        score = _pick_float(res, SCORE_KEYS, default=None)
        reason = _pick_str(res, REASON_KEYS, default="")
        # 若 label 型態
        if is_spam is None:
            label = str(res.get("label", res.get("prediction", ""))).lower()
            if label in ("spam", "junk", "垃圾", "惡意", "scam"):
                is_spam = True
            elif label in ("ham", "clean", "正常", "非垃圾"):
                is_spam = False
        if is_spam is None and score is not None:
            is_spam = bool(score >= thr)
        if is_spam is None:
            # 無法判定時，保守視為非垃圾
            is_spam = False
        if score is None:
            score = 1.0 if is_spam else 0.0
        return bool(is_spam), float(score), str(reason)
    # bool
    if isinstance(res, bool):
        return res, 1.0 if res else 0.0, ""
    # (bool, score[, reason]) 或 (score, reason) 等
    if isinstance(res, tuple | list):
        if len(res) >= 2:
            a, b = res[0], res[1]
            c = res[2] if len(res) >= 3 else ""
            if isinstance(a, bool):
                return a, float(b) if _is_number(b) else (1.0 if a else 0.0), str(c)
            if _is_number(a):
                score = float(a)
                is_spam = score >= thr
                reason = str(b) if not _is_number(b) else ""
                return is_spam, score, reason
    # 單一數值（視為分數）
    if _is_number(res):
        score = float(res)
        return score >= thr, score, ""
    # 文字標籤
    if isinstance(res, str):
        lbl = res.strip().lower()
        if lbl in ("spam", "junk", "垃圾", "惡意", "scam"):
            return True, 1.0, ""
        if lbl in ("ham", "clean", "正常", "非垃圾"):
            return False, 0.0, ""
    # 無法解析
    return False, 0.0, ""


def _is_number(x: Any) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def _pick_bool(d: dict[str, Any], keys, default=None):
    for k in keys:
        if k in d:
            v = d[k]
            if isinstance(v, bool):
                return v
            if isinstance(v, int | float):
                return bool(v)
            if isinstance(v, str):
                return v.strip().lower() in ("1", "true", "yes", "y", "spam", "junk", "垃圾")
    return default


def _pick_float(d: dict[str, Any], keys, default=None):
    for k in keys:
        if k in d:
            v = d[k]
            try:
                return float(v)
            except Exception:
                continue
    return default


def _pick_str(d: dict[str, Any], keys, default=""):
    for k in keys:
        if k in d:
            v = d[k]
            if v is None:
                continue
            return str(v)
    return default


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(description="垃圾信偵測（自動適配 orchestrator 介面）")
    p.add_argument("--subject", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--sender", default="")
    args = p.parse_args(argv)

    mod = _import_orch_module()
    if mod is None:
        sys.stderr.write("找不到 orchestrator 模組：請確認位於 src/spam/ 或 smart_mail_agent/spam/\n")
        return 2

    cls = _find_orch_class(mod)
    target: Any = _instantiate(cls) if cls else mod  # 沒有類別就用模組函式
    if target is None:
        sys.stderr.write("無法建立 orchestrator 實例，且無可用模組函式\n")
        return 2

    try:
        is_spam, score, reason = _call_with_adaptation(target, args.subject, args.content, args.sender)
    except Exception as e:
        sys.stderr.write(f"呼叫 orchestrator 失敗：{e}\n")
        return 3

    print(f"is_spam={int(is_spam)}\tscore={score:.3f}\treason={reason}")
    return 0 if not is_spam else 1


if __name__ == "__main__":
    raise SystemExit(main())
