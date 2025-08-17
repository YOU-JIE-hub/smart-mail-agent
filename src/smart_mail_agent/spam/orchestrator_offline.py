#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable, Mapping, Optional, Union

# 規則模組（名稱不穩，這裡只用到 link ratio 規則 & keyword 概念，實作在本檔完成）
from smart_mail_agent.spam import rules as _rules  # noqa: F401  (保留相容引用)

LOG = logging.getLogger("smart_mail_agent.spam.orchestrator_offline")
if not LOG.handlers:
    logging.basicConfig(level=logging.INFO, format="[SPAM] %(asctime)s %(levelname)s %(message)s")

Email = Mapping[str, Any]
RuleFn = Callable[[Email], Union[bool, Mapping[str, Any]]]
ModelFn = Optional[Callable[..., Any]]  # 允許 0/1/2 參數


@dataclass
class Thresholds:
    model: float = 0.60
    link_ratio_drop: float = 0.60
    link_ratio_review: float = 0.45


def _normalize_email(subject_or_email: Union[str, Email]) -> Email:
    if isinstance(subject_or_email, str):
        return {"subject": subject_or_email, "content": ""}
    return subject_or_email


def _apply_rule_shortcut(rule: RuleFn, email: Email) -> Optional[SimpleNamespace]:
    r = rule(email)
    if isinstance(r, bool):
        if r:
            return SimpleNamespace(is_spam=True, is_borderline=False, source="rule", action="drop")
        return None
    if isinstance(r, Mapping):
        if r.get("is_spam") is True:
            action = r.get("action") or "drop"
            return SimpleNamespace(
                is_spam=True,
                is_borderline=bool(r.get("is_borderline")),
                source="rule",
                action=action,
            )
        return None
    return None


def _normalize_model_output(out: Any, threshold: float) -> tuple[str, float]:
    # None
    if out is None:
        return ("ham", 0.0)
    # 純分數
    if isinstance(out, (int, float)):
        sc = float(out)
        return ("spam" if sc >= threshold else "ham", max(0.0, min(1.0, sc)))
    # 純字串
    if isinstance(out, str):
        lbl = out.strip().lower()
        if lbl in ("spam", "ham"):
            return (lbl, 1.0 if lbl == "spam" else 0.0)
        return ("ham", 0.0)
    # (label, score) 或 (score, label)
    if isinstance(out, (list, tuple)) and len(out) == 2:
        a, b = out
        if isinstance(a, (int, float)) and isinstance(b, str):
            sc = float(a)
            lbl = b.strip().lower()
            if lbl not in ("spam", "ham"):
                lbl = "spam" if sc >= threshold else "ham"
            return (lbl, max(0, min(1, sc)))
        if isinstance(a, str) and isinstance(b, (int, float)):
            lbl = a.strip().lower()
            sc = float(b)
            if lbl not in ("spam", "ham"):
                lbl = "spam" if sc >= threshold else "ham"
            return (lbl, max(0, min(1, sc)))
    # dict
    if isinstance(out, Mapping):
        lbl = str(out.get("label", "ham")).lower()
        sc = out.get("score", out.get("prob"))
        if sc is None:
            sc = 1.0 if lbl == "spam" else 0.0
        sc = float(sc)
        if lbl not in ("spam", "ham"):
            lbl = "spam" if sc >= threshold else "ham"
        return (lbl, sc)
    # list[dict]
    if isinstance(out, list) and out and isinstance(out[0], Mapping):
        best = None
        for x in out:
            sc = x.get("score", x.get("prob"))
            if sc is not None:
                sc = float(sc)
                if best is None or sc > best[1]:
                    best = (str(x.get("label", "ham")).lower(), sc)
        if best is not None:
            lbl = (
                best[0]
                if best[0] in ("spam", "ham")
                else ("spam" if best[1] >= threshold else "ham")
            )
            return (lbl, best[1])
        # 沒分數，用第一個 label
        lbl = str(out[0].get("label", "ham")).lower()
        return (lbl if lbl in ("spam", "ham") else "ham", 1.0 if lbl == "spam" else 0.0)
    # fallback
    return ("ham", 0.0)


def _call_model_robust(
    model: ModelFn, email: Email, threshold: float
) -> tuple[str, float, str, Optional[str]]:
    if model is None:
        return ("ham", 0.0, "rule", None)
    subj = email.get("subject", "")
    cont = email.get("content", "")
    try:
        try:
            out = model(subj, cont)  # 優先 2 參數
        except TypeError:
            try:
                out = model(cont)  # 次選 1 參數
            except TypeError:
                out = model()  # 最後 0 參數
        label, score = _normalize_model_output(out, threshold)
        return (label, float(score), "model", None)
    except Exception as e:
        LOG.warning("model raised, fallback ham: %s", e)
        return ("ham", 0.0, "fallback", str(e))


class SpamFilterOrchestratorOffline:
    def __init__(
        self,
        rule: Optional[RuleFn] = None,
        model: ModelFn = None,
        thresholds: Optional[Thresholds] = None,
    ) -> None:
        self.rule: RuleFn = rule or (lambda _e: False)
        self.model: ModelFn = model
        self.thresholds = thresholds or Thresholds()

    # NFKC 關鍵字 / link ratio
    def decide(self, subject: str, content: str) -> Mapping[str, Any]:
        def _nfkc_upper(x: str) -> str:
            try:
                x = unicodedata.normalize("NFKC", x or "")
            except Exception:
                x = x or ""
            return x.upper()

        text_norm = _nfkc_upper((subject or "") + " " + (content or ""))
        for k in ("FREE", "免費", "贈品", "中獎", "中奖"):
            if k in text_norm:
                return {
                    "action": "drop",
                    "is_spam": True,
                    "is_borderline": False,
                    "source": "keyword",
                    "reasons": ["rule:keyword"],
                    "scores": {},
                }

        a_pat = re.compile(r"<a\b[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)
        text_no_a = re.sub(
            r"<a\b[^>]*>.*?</a>", " ", content or "", flags=re.IGNORECASE | re.DOTALL
        )
        nonlink = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text_no_a)).strip()
        nonlink_len = len(nonlink)

        link_texts = a_pat.findall(content or "")
        link_weight = 0
        for t in link_texts:
            l = len(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip())
            link_weight += max(l, 15)

        den = link_weight + nonlink_len or 1
        ratio = link_weight / den

        scores = {"link_ratio": round(ratio, 4)}
        reasons = []
        d, r = self.thresholds.link_ratio_drop, self.thresholds.link_ratio_review
        if ratio >= d:
            reasons.append(f"rule:link_ratio>={d}")
            return {
                "action": "drop",
                "is_spam": True,
                "is_borderline": False,
                "source": "link_ratio",
                "reasons": reasons,
                "scores": scores,
            }
        if ratio >= r:
            reasons.append(f"rule:link_ratio>={r}")
            return {
                "action": "review",
                "is_spam": True,
                "is_borderline": True,
                "source": "link_ratio",
                "reasons": reasons,
                "scores": scores,
            }

        # 交給 orchestrate
        res = orchestrate(
            {"subject": subject, "content": content}, self.rule, self.model, self.thresholds.model
        )
        act = res.action
        return {
            "action": ("route" if act == "route_to_inbox" else act),
            "is_spam": bool(res.is_spam),
            "is_borderline": bool(res.is_borderline),
            "source": res.source,
            "reasons": reasons,
            "scores": scores,
        }

    def decide(self, subject: str, content: str) -> dict:
        import re as _re
        import unicodedata as _ud

        def _nfkc_upper(x: str) -> str:
            try:
                x = _ud.normalize("NFKC", x or "")
            except Exception:
                x = x or ""
            return x.upper()

        subject = str(subject or "")
        content = str(content or "")

        a_pat = _re.compile(r"<a\b[^>]*>(.*?)</a>", _re.IGNORECASE | _re.DOTALL)

        def _clean(t: str) -> str:
            return _re.sub(r"\s+", " ", _re.sub(r"<[^>]+>", " ", t)).strip()

        # 連結權重（每個連結至少 15 字元）
        link_texts = [m.group(1) for m in a_pat.finditer(content)]
        link_weight = sum(max(len(_clean(t)), 15) for t in link_texts)

        # 非連結文字長度
        nonlink_html_removed = _re.sub(
            r"<a\b[^>]*>.*?</a>", " ", content, flags=_re.IGNORECASE | _re.DOTALL
        )
        nonlink_text = _clean(nonlink_html_removed)
        nonlink_len = len(nonlink_text)

        den = link_weight + nonlink_len or 1
        ratio = link_weight / den

        scores = {"link_ratio": round(ratio, 4)}
        reasons = []
        d = getattr(self.thresholds, "link_ratio_drop", 0.6)
        r = getattr(self.thresholds, "link_ratio_review", 0.45)

        if ratio >= d:
            reasons.append(f"rule:link_ratio>={d}")
            return {
                "action": "drop",
                "is_spam": True,
                "is_borderline": False,
                "source": "link_ratio",
                "reasons": reasons,
                "scores": scores,
            }
        if ratio >= r:
            reasons.append(f"rule:link_ratio>={r}")
            return {
                "action": "review",
                "is_spam": True,
                "is_borderline": True,
                "source": "link_ratio",
                "reasons": reasons,
                "scores": scores,
            }

        # 關鍵字（放後面，避免覆蓋 link_ratio 的 reasons）
        text_norm = _nfkc_upper(subject + " " + content)
        if any(k in text_norm for k in ("FREE", "免費", "贈品", "中獎", "中奖")):
            return {
                "action": "drop",
                "is_spam": True,
                "is_borderline": False,
                "source": "keyword",
                "reasons": ["rule:keyword"],
                "scores": scores,
            }

        # fallback：交給 orchestrate（rule+model）
        email = {"subject": subject, "content": content, "attachments": []}
        res = orchestrate(email, self.rule, self.model, model_threshold=self.thresholds.model)
        act = getattr(res, "action", "route_to_inbox")
        return {
            "action": ("route" if act == "route_to_inbox" else act),
            "is_spam": bool(getattr(res, "is_spam", False)),
            "is_borderline": bool(getattr(res, "is_borderline", False)),
            "source": getattr(res, "source", "model"),
            "reasons": reasons,
            "scores": scores,
        }


def orchestrate(
    subject_or_email: Union[str, Email], rule: RuleFn, model: ModelFn, model_threshold: float = 0.6
) -> SimpleNamespace:
    email = _normalize_email(subject_or_email)
    # 規則捷徑
    try:
        rs = _apply_rule_shortcut(rule, email)
        if rs is not None:
            return rs
    except Exception:
        pass

    label, score, source, err = _call_model_robust(model, email, model_threshold)

    # ham 標籤一律視為非垃圾：覆寫 score 為 0.0

    if label == "ham":

        score = 0.0

    is_spam = score >= model_threshold
    is_borderline = bool(model is not None and score == model_threshold)
    action = "review" if (is_spam and is_borderline) else ("drop" if is_spam else "route_to_inbox")

    ns = SimpleNamespace(is_spam=is_spam, is_borderline=is_borderline, source=source, action=action)
    if source == "fallback" and err:
        ns.extra = {"model_error": err}
    return ns


# ---------- CLI ----------
def _parse_args(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--subject")
    p.add_argument("--content")
    p.add_argument("--threshold", type=float, default=0.60)
    p.add_argument("--json", action="store_true")  # 單元測試需要
    return p.parse_args(argv)


def _main() -> int:
    args = _parse_args()
    orch = SpamFilterOrchestratorOffline(thresholds=Thresholds(model=args.threshold))
    out = orch.decide(args.subject or "", args.content or "")
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
