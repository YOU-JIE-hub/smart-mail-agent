from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

# 供測試 monkeypatch：規則檔路徑與簡易快取
CONF_PATH: str | None = None
_CACHE: dict[str, Any] = {"path": None, "mtime": None, "rules": None}

# 內建預設（若無外部 YAML）
_DEFAULT = {
    "blacklist_senders": ["scam@bad.com", "noreply@scam.biz"],
    "blacklist_domains": ["bad.com", "scam.biz"],
    "shorteners": ["bit.ly", "goo.gl", "is.gd", "t.co"],
    "suspicious_domains": [],
    "suspicious_tlds": ["tk", "gq", "ml", "cf", "ga", "top"],
    "bad_extensions": [".js", ".vbs", ".exe", ".bat", ".cmd", ".scr"],
    "whitelist_domains": ["yourcompany.com", "example.com"],
    "keywords": {},  # 例：{"FREE": 3}
    "weights": {
        "url_suspicious": 4,
        "tld_suspicious": 3,
        "attachment_executable": 5,
        "sender_black": 5,
        "domain_black": 4,
        "keyword": 1,  # 關鍵字 fallback 點數
    },
    "thresholds": {"suspect": 4, "spam": 8},
}

_URL_RE = re.compile(r"https?://[^\s)>\]]+", re.I)


def _load_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file() or yaml is None:
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else None
    except Exception:  # pragma: no cover
        return None


def load_rules(config_path: str | Path | None = None) -> dict[str, Any]:
    """讀取規則；優先順序：參數 -> CONF_PATH -> configs/spam_rules.yaml -> 內建"""
    path = Path(config_path or CONF_PATH or "configs/spam_rules.yaml")
    mtime = path.stat().st_mtime if path.exists() else None
    if (
        _CACHE.get("path") == str(path)
        and _CACHE.get("mtime") == mtime
        and isinstance(_CACHE.get("rules"), dict)
    ):
        return _CACHE["rules"]  # type: ignore[return-value]

    rules = dict(_DEFAULT)
    override = _load_yaml(path)
    if override:
        rules.update(override)

    _CACHE.update({"path": str(path), "mtime": mtime, "rules": rules})
    return rules


def _iter_urls(text: str) -> Iterable[str]:
    if not text:
        return []
    return _URL_RE.findall(text)


def _domain_of(url: str) -> str | None:
    m = re.match(r"https?://([^/:?#]+)", url, flags=re.I)
    return m.group(1).lower() if m else None


def _tld_of(domain: str) -> str | None:
    if not domain or "." not in domain:
        return None
    return domain.rsplit(".", 1)[-1].lower()


def _ext_of(path: str) -> str:
    return Path(path).suffix.lower()


def _domain_matches_list(domain: str, lst: list[str]) -> bool:
    """支援子網域：a.bit.ly 命中 bit.ly"""
    d = (domain or "").lower()
    for item in (x.lower() for x in lst or []):
        if d == item or d.endswith("." + item):
            return True
    return False


def has_suspicious_attachment(attachments) -> bool:
    """
    Heuristic：是否含高風險副檔名或雙重副檔名（.pdf.exe）。
    attachments: Iterable of dict/obj/str with 'filename'/'name' or str().
    """
    exts = {
        ".exe",
        ".scr",
        ".js",
        ".bat",
        ".cmd",
        ".com",
        ".vbs",
        ".jar",
        ".apk",
        ".ps1",
        ".lnk",
        ".cab",
        ".msi",
        ".dll",
        ".iso",
        ".img",
        ".7z",
        ".zip",
        ".rar",
    }

    def _name(a):
        if isinstance(a, dict):
            return (a.get("filename") or a.get("name") or "").lower()
        try:
            return str(getattr(a, "filename", getattr(a, "name", a))).lower()
        except Exception:
            return str(a).lower()

    for a in attachments or []:
        n = _name(a)
        if any(n.endswith(e) for e in exts):
            return True
        if ".pdf." in n or ".doc." in n or ".xls." in n:
            return True
    return False


def score_email(
    sender: str,
    subject: str,
    content: str,
    attachments: list[str],
) -> tuple[int, list[str]]:
    """回傳 (raw_points, reasons)。reasons 前綴符合測試：url:/tld:/attachment: ..."""
    cfg = load_rules()
    w = cfg.get("weights", {})
    reasons: list[str] = []
    score = 0

    text = f"{subject or ''}\n{content or ''}"

    # URL / 可疑網域 / 可疑 TLD
    sus_domains = list(cfg.get("suspicious_domains", [])) + list(
        cfg.get("shorteners", [])
    )
    for url in _iter_urls(text):
        domain = _domain_of(url) or ""
        if domain and _domain_matches_list(domain, sus_domains):
            score += int(w.get("url_suspicious", 0))
            reasons.append(f"url:{domain}")
        tld = _tld_of(domain)
        if tld and tld in [x.lower() for x in cfg.get("suspicious_tlds", [])]:
            score += int(w.get("tld_suspicious", 0))
            reasons.append(f"tld:.{tld}")

    # 附件
    for a in attachments or []:
        ext = _ext_of(a)
        if ext in [x.lower() for x in cfg.get("bad_extensions", [])]:
            score += int(w.get("attachment_executable", 0))
            reasons.append(f"attachment:{ext}")

    # 黑/白名單與關鍵字
    sender_lower = (sender or "").lower()
    sender_domain = sender_lower.split("@", 1)[-1] if "@" in sender_lower else ""
    if sender_lower in (x.lower() for x in cfg.get("blacklist_senders", [])):
        score += int(w.get("sender_black", 0))
        reasons.append("sender:blacklisted")
    if sender_domain and sender_domain in (
        d.lower() for d in cfg.get("blacklist_domains", [])
    ):
        score += int(w.get("domain_black", 0))
        reasons.append(f"domain:blacklisted:{sender_domain}")
    if sender_domain and sender_domain in (
        d.lower() for d in cfg.get("whitelist_domains", [])
    ):
        reasons.append(f"domain:whitelisted:{sender_domain}")

    kw_map: dict[str, int] = cfg.get("keywords", {}) or {}
    for kw, pts in kw_map.items():
        if kw and re.search(rf"\b{re.escape(kw)}\b", text, flags=re.I):
            score += int(pts if isinstance(pts, int) else w.get("keyword", 1))
            reasons.append(f"kw:{kw}")

    return int(score), reasons


def label_email(
    sender: str,
    subject: str,
    content: str,
    attachments: list[str],
) -> tuple[str, int, list[str]]:
    """依 thresholds 產出 label：'spam' / 'suspect' / 'ok'"""
    cfg = load_rules()
    thresholds = cfg.get("thresholds", {}) or {}
    score, reasons = score_email(sender, subject, content, attachments)
    spam_th = int(thresholds.get("spam", 8))
    suspect_th = int(thresholds.get("suspect", 4))
    if score >= spam_th:
        label = "spam"
    elif score >= suspect_th:
        label = "suspect"
    else:
        label = "ok"
    return label, score, reasons


__all__ = [
    "load_rules",
    "score_email",
    "label_email",
    "has_suspicious_attachment",
    "CONF_PATH",
    "_CACHE",
]
