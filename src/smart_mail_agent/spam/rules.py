from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pyyaml 不一定存在
    yaml = None  # type: ignore


# 預設規則（若專案的 configs/spam_rules.yaml 存在會覆蓋）
_DEFAULT = {
    "blacklist_senders": [
        "scam@bad.com",
        "noreply@scam.biz",
    ],
    "blacklist_domains": [
        "bad.com",
        "scam.biz",
    ],
    "shorteners": ["bit.ly", "goo.gl", "is.gd", "t.co"],
    "suspicious_tlds": ["tk", "gq", "ml", "cf", "ga", "top"],
    "bad_extensions": [".js", ".vbs", ".exe", ".bat", ".cmd", ".scr"],
    "whitelist_domains": ["yourcompany.com", "example.com"],
    "weights": {
        "url_suspicious": 4,
        "tld_suspicious": 3,
        "attachment_executable": 5,
        "sender_black": 5,
        "domain_black": 4,
    },
    "thresholds": {"suspect": 4, "spam": 8},
}

_CACHE: dict[str, Any] = {}


def _load_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    if yaml is None:
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            return data  # 型別由呼叫端做寬鬆處理
    except Exception:
        pass
    return None


def load_rules(config_path: str | Path | None = None) -> dict[str, Any]:
    """
    讀取規則檔；若未提供或檔案缺失，回傳內建預設。
    優先順序：參數指定 -> configs/spam_rules.yaml -> 內建預設
    """
    key = str(config_path or "default")
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]

    base = dict(_DEFAULT)
    path = Path(config_path) if config_path else Path("configs/spam_rules.yaml")
    override = _load_yaml(path)
    if override:
        # 淺合併即可（此處不做深層合併，保持簡單可預期）
        base.update(override)

    _CACHE[key] = base
    return base


_URL_RE = re.compile(r"https?://[^\s)>\]]+", re.I)


def _iter_urls(text: str) -> Iterable[str]:
    if not text:
        return []
    return _URL_RE.findall(text)


def _domain_of(url: str) -> str | None:
    # 極簡擷取 domain（不引入 urllib 以減少依賴）
    m = re.match(r"https?://([^/:?#]+)", url, flags=re.I)
    return m.group(1).lower() if m else None


def _tld_of(domain: str) -> str | None:
    if not domain or "." not in domain:
        return None
    return domain.rsplit(".", 1)[-1].lower()


def _ext_of(path: str) -> str:
    p = Path(path)
    return p.suffix.lower()


def score_email(
    sender: str,
    subject: str,
    content: str,
    attachments: list[str],
) -> tuple[int, list[str]]:
    """
    回傳 (分數, 命中的原因列表)。
    """
    cfg = load_rules()
    w = cfg["weights"]
    reasons: list[str] = []
    score = 0

    text = f"{subject or ''}\n{content or ''}"

    # URL 與短網址／可疑 TLD
    for url in _iter_urls(text):
        domain = _domain_of(url) or ""
        if any(s in domain for s in cfg["shorteners"]):
            score += w["url_suspicious"]
            reasons.append(f"url_shortener:{domain}")
        tld = _tld_of(domain)
        if tld and tld in cfg["suspicious_tlds"]:
            score += w["tld_suspicious"]
            reasons.append(f"suspicious_tld:.{tld}")

    # 附件副檔名
    for a in attachments or []:
        ext = _ext_of(a)
        if ext in cfg["bad_extensions"]:
            score += w["attachment_executable"]
            reasons.append(f"bad_attachment:{ext}")

    # 寄件者與網域
    sender_lower = (sender or "").lower()
    sender_domain = sender_lower.split("@", 1)[-1] if "@" in sender_lower else ""
    if sender_lower in (x.lower() for x in cfg["blacklist_senders"]):
        score += w["sender_black"]
        reasons.append("sender_blacklisted")
    if sender_domain and sender_domain in (d.lower() for d in cfg["blacklist_domains"]):
        score += w["domain_black"]
        reasons.append(f"domain_blacklisted:{sender_domain}")

    # 白名單網域可作為降權（此處僅保留，是否要減分看你策略）
    if sender_domain and sender_domain in (d.lower() for d in cfg["whitelist_domains"]):
        # 視情境可做小幅減分；先不改動分數，只記錄原因
        reasons.append(f"domain_whitelisted:{sender_domain}")

    return int(score), reasons


__all__ = ["load_rules", "score_email"]
