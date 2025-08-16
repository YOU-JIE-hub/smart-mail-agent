#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

CONF_PATH: Optional[str] = None

__all__ = [
    "contains_keywords",
    "link_ratio",
    "label_email",
    "has_suspicious_attachment",
    "CONF_PATH",
    "_normalize_text",
]


def _normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = html.unescape(s)
    s = s.replace("\u3000", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# 內建關鍵字（含常見中文行銷詞）
DEFAULT_KEYWORDS: Tuple[str, ...] = (
    "中獎",
    "領獎",
    "投資",
    "虛擬幣",
    "比特幣",
    "色情",
    "發票中獎",
    "免費",
    "點此連結",
    "lottery",
    "winner",
    "click here",
    "viagra",
    "invest",
    "crypto",
    "free",
    "限時優惠",
    "優惠",
    "下單",
    "折扣",
    "領券",
)


def contains_keywords(
    text: str,
    keywords: Optional[Sequence[str]] = None,
    *,
    case_insensitive: bool = True,
    match_word_boundary: bool = False,
) -> bool:
    kws = list(keywords or DEFAULT_KEYWORDS)
    s = _normalize_text(text)
    if not s or not kws:
        return False
    flags = re.IGNORECASE if case_insensitive else 0
    for kw in kws:
        if not kw:
            continue
        pattern = (
            rf"(?:(?<=^)|(?<=[^\w])){re.escape(kw)}(?:(?=$)|(?=[^\w]))"
            if match_word_boundary
            else re.escape(kw)
        )
        if re.search(pattern, s, flags=flags):
            return True
    return False


_URL_RE = re.compile(r"https?://[^\s<>\")]+", re.IGNORECASE)


def link_ratio(html_or_text: str) -> float:
    if not isinstance(html_or_text, str) or not html_or_text.strip():
        return 0.0
    s = html_or_text

    # 1) <a>inner</a> 的 inner（可見）
    inners = re.findall(r"<\s*a\b[^>]*>(.*?)<\s*/\s*a\s*>", s, flags=re.IGNORECASE | re.DOTALL)
    link_text = " ".join(_normalize_text(re.sub(r"<[^>]+>", " ", inner)) for inner in inners)
    link_text_len = len(link_text.strip())

    # 2) 可見文字（去標籤）
    visible_text = _normalize_text(re.sub(r"<[^>]+>", " ", s))
    visible_text_len = max(len(visible_text), 1)

    # 3) 僅在可見文字中計算純文字 URL
    for u in _URL_RE.findall(visible_text):
        link_text_len += max(8, min(len(u), 64))

    ratio = link_text_len / float(visible_text_len)
    return 0.0 if ratio < 0 else (1.0 if ratio > 1 else ratio)


DANGEROUS_EXTS: Tuple[str, ...] = (
    ".exe",
    ".scr",
    ".pif",
    ".com",
    ".bat",
    ".cmd",
    ".vbs",
    ".js",
    ".jse",
    ".wsf",
    ".wsh",
    ".ps1",
    ".psm1",
    ".psd1",
    ".jar",
    ".apk",
    ".hta",
    ".cpl",
    ".msi",
    ".msp",
    ".dll",
    ".reg",
    ".sh",
)


def _ext_of(name: Any) -> str:
    m = re.search(r"(\.[A-Za-z0-9]{1,6})$", str(name or "").strip())
    return m.group(1).lower() if m else ""


def has_suspicious_attachment(attachments: Sequence[Any]) -> Tuple[bool, List[str]]:
    hits: List[str] = []
    for a in attachments or ():
        ext = _ext_of(a)
        if ext and ext in DANGEROUS_EXTS and ext not in hits:
            hits.append(ext)
    return (len(hits) > 0, hits)


def _load_conf() -> Dict[str, Any]:
    path = CONF_PATH
    if not path or not os.path.isfile(path):
        return {}
    try:
        import yaml  # type: ignore

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        pass
    txt = open(path, "r", encoding="utf-8").read()
    result: Dict[str, Any] = {}
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()

        def _quote_keys(s: str) -> str:
            return re.sub(r"({|,)\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1 "\2":', s)

        if v.startswith("{") and v.endswith("}"):
            vv = _quote_keys(v).replace("'", '"')
            try:
                result[k] = json.loads(vv)
            except Exception:
                result[k] = {}
        elif v.startswith("[") and v.endswith("]"):
            vv = v.replace("'", '"')
            try:
                result[k] = json.loads(vv)
            except Exception:
                result[k] = []
        else:
            result[k] = v.strip('"').strip("'")
    return result


def _domain_of(url: str) -> str:
    m = re.match(r"https?://([^/:?#]+)", url, flags=re.I)
    return (m.group(1).lower() if m else "").strip()


def _tld_of(domain: str) -> str:
    parts = (domain or "").split(".")
    return parts[-1].lower() if parts else ""


@dataclass
class LabelResult:
    label: str
    score: float
    scores: Dict[str, float]
    reasons: List[str]


def _label_email_internal(
    email: Mapping[str, Any], *, keywords: Optional[Sequence[str]], lr_drop: float
) -> Dict[str, Any]:
    subject = str(email.get("subject", "") or "")
    content = str(email.get("content", "") or "")
    attachments = email.get("attachments", [])
    if not isinstance(attachments, (list, tuple)):
        attachments = []

    merged = f"{subject}\n{content}"
    reasons: List[str] = []
    conf = _load_conf()

    if conf:
        pts = 0
        kw_map = conf.get("keywords") or {}
        if isinstance(kw_map, dict):
            for k, w in kw_map.items():
                if contains_keywords(merged, [str(k)]):
                    pts += int(w)
                    reasons.append(f"cfg:kw:{k}")
        urls = _URL_RE.findall(content)
        doms = [_domain_of(u) for u in urls]
        tlds = [_tld_of(d) for d in doms]
        sus_doms = set(map(str.lower, conf.get("suspicious_domains") or []))
        sus_tlds = set(map(str.lower, conf.get("suspicious_tlds") or []))
        if doms and any((d == _sd or d.endswith("." + _sd)) for d in doms for _sd in sus_doms):
            pts += int((conf.get("weights", {}) or {}).get("url_suspicious", 0))
            reasons.append("cfg:url_suspicious")
            for _d in doms:
                for _sus in sus_doms:
                    if _d == _sus or _d.endswith("." + _sus):
                        reasons.append(f"url:{_d}")
                        break
        if tlds and any(t in sus_tlds for t in tlds):
            pts += int((conf.get("weights", {}) or {}).get("tld_suspicious", 0))
            reasons.append("cfg:tld_suspicious")
            for _t in tlds:
                if _t in sus_tlds:
                    reasons.append(f"tld:{_t}")
        bad_exts = set(map(str.lower, conf.get("bad_extensions") or []))
        if attachments and any(_ext_of(a) in bad_exts for a in attachments):
            pts += int((conf.get("weights", {}) or {}).get("attachment_executable", 0))
            reasons.append("cfg:attachment_executable")
        sender = str(email.get("sender") or "")
        sender_dom = sender.split("@")[-1].lower() if "@" in sender else ""
        if sender_dom and sender_dom in set(map(str.lower, conf.get("whitelist_domains") or [])):
            pts = max(0, pts - 999)

        thr = conf.get("thresholds") or {}
        thr_sus = int(thr.get("suspect", 4))
        thr_spam = int(thr.get("spam", 8))
        label = "spam" if pts >= thr_spam else ("suspect" if pts >= thr_sus else "legit")
        score_norm = min(1.0, pts / float(max(thr_spam, 1)))
        scores = {
            "keyword": 1.0 if any(r.startswith("cfg:kw") for r in reasons) else 0.0,
            "link_ratio": link_ratio(content),
            "attachment": 1.0 if "cfg:attachment_executable" in reasons else 0.0,
        }
        return {
            "label": label,
            "score": float(score_norm),
            "score_points": int(pts),
            "scores": scores,
            "reasons": reasons,
        }

    # 無 conf：啟發式
    kw_hit = contains_keywords(merged, keywords)
    if kw_hit:
        reasons.append("rule:keyword")
    lr = float(link_ratio(content))
    if lr >= lr_drop:
        reasons.append(f"rule:link_ratio>={lr_drop:.2f}")
    att_hit = any(_ext_of(a) in DANGEROUS_EXTS for a in attachments)
    if att_hit:
        for a in attachments:
            ext = _ext_of(a)
            if ext in DANGEROUS_EXTS:
                reasons.append(f"rule:attachment:{ext}")
    score = max(lr, 0.6 if kw_hit else 0.0, 0.5 if att_hit else 0.0)
    label = "spam" if score >= 0.60 else ("suspect" if score >= 0.45 else "legit")
    scores = {
        "keyword": 1.0 if kw_hit else 0.0,
        "link_ratio": lr,
        "attachment": 1.0 if att_hit else 0.0,
    }
    return {"label": label, "score": float(score), "scores": scores, "reasons": reasons}


def label_email(
    email_or_sender: Mapping[str, Any] | str,
    subject: Optional[str] = None,
    content: Optional[str] = None,
    attachments: Optional[Sequence[Any]] = None,
    *,
    keywords: Optional[Sequence[str]] = None,
    lr_drop: float = 0.60,
):
    """
    兩種呼叫：
      1) label_email(mapping) -> dict（含 score=0~1 與 score_points（如有））
      2) label_email(sender, subject, content, attachments) -> (label, score, reasons)
         - 若載入 CONF（CONF_PATH 有效），score 為原始分數點數
         - 否則 score 為 0~1 正規化分數
    """
    if isinstance(email_or_sender, dict):
        res = _label_email_internal(email_or_sender, keywords=keywords, lr_drop=lr_drop)
        return res
    email = {
        "sender": email_or_sender,
        "subject": subject or "",
        "content": content or "",
        "attachments": list(attachments or []),
    }
    res = _label_email_internal(email, keywords=keywords, lr_drop=lr_drop)
    # 依是否有 CONF 決定四參數回傳的 score 定義
    from_path_conf = CONF_PATH
    if from_path_conf:
        return (res["label"], int(res.get("score_points", 0)), res["reasons"])  # raw points
    return (res["label"], float(res.get("score", 0.0)), res["reasons"])  # normalized
