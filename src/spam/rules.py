from __future__ import annotations

import re
from typing import Dict, List, Tuple

SUSPICIOUS_TLDS = {
    "top",
    "xyz",
    "click",
    "work",
    "link",
    "fit",
    "kim",
    "win",
    "men",
    "loan",
    "mom",
    "party",
    "review",
    "country",
    "gq",
    "tk",
    "ml",
    "cf",
    "ru",
}
EXECUTABLE_EXTS = {
    ".js",
    ".exe",
    ".bat",
    ".cmd",
    ".vbs",
    ".scr",
    ".ps1",
    ".apk",
    ".msi",
    ".com",
    ".jar",
}

_SUBJECT_KWS = [
    (re.compile(r"\bget\s+rich\s+quick\b", re.I), 4, "kw: get rich quick"),
    (re.compile(r"\bcrypto\b", re.I), 2, "kw: crypto"),
    (re.compile(r"\bgive\s*away\b", re.I), 2, "kw: giveaway"),
    (re.compile(r"\bfree\b", re.I), 1, "kw: free"),
    (re.compile(r"!{3,}"), 1, "punct: !!!"),
]
_CONTENT_SPAM_URL_KWS = [
    re.compile(r"\bwin\b", re.I),
    re.compile(r"\btoken\b", re.I),
    re.compile(r"\bclaim\b", re.I),
    re.compile(r"\bbonus\b", re.I),
    re.compile(r"\bairdrop\b", re.I),
]
_URL_RE = re.compile(r"https?://(?P<host>[A-Za-z0-9.-]+)[^\s]*")


def _host_tld(host: str) -> str:
    parts = host.lower().split(".")
    return parts[-1] if parts else ""


def check_sender(sender: str) -> Tuple[int, List[str]]:
    score, reasons = 0, []
    if not sender:
        return score, reasons
    # 取 domain（簡化）
    m = re.search(r"@([A-Za-z0-9.-]+)$", sender)
    if m:
        host = m.group(1).lower()
        tld = _host_tld(host)
        if tld in SUSPICIOUS_TLDS:
            score += 2
            reasons.append(f"sender-tld:{tld}")
    return score, reasons


def check_subject(subject: str) -> Tuple[int, List[str]]:
    score, reasons = 0, []
    s = subject or ""
    for rx, pts, tag in _SUBJECT_KWS:
        if rx.search(s):
            score += pts
            reasons.append(f"subject:{tag}")
    return score, reasons


def check_content(content: str) -> Tuple[int, List[str]]:
    score, reasons = 0, []
    c = content or ""
    # URL + 關鍵詞
    hits_kw = any(rx.search(c) for rx in _CONTENT_SPAM_URL_KWS)
    m = _URL_RE.search(c)
    if m:
        host = m.group("host").lower()
        tld = _host_tld(host)
        score += 1
        reasons.append("url:present")
        if hits_kw:
            score += 2
            reasons.append("url:spam-kw")
        if tld in SUSPICIOUS_TLDS:
            score += 2
            reasons.append(f"url-tld:{tld}")
    else:
        # 沒 URL 也可有關鍵字，但分數較低
        if hits_kw:
            score += 1
            reasons.append("content:spam-kw")
    return score, reasons


def check_attachments(attachments: list) -> Tuple[int, List[str]]:
    score, reasons = 0, []
    for a in attachments or []:
        fn = str(a).lower()
        for ext in EXECUTABLE_EXTS:
            if fn.endswith(ext):
                score += 5
                reasons.append(f"attachment:exec({ext})")
                break
    return score, reasons


def score_email(sender: str, subject: str, content: str, attachments: list) -> Dict[str, object]:
    total = 0
    reasons: List[str] = []
    for s, r in [
        check_sender(sender),
        check_subject(subject),
        check_content(content),
        check_attachments(attachments),
    ]:
        total += s
        reasons.extend(r)
    return {"score": total, "reasons": reasons}
