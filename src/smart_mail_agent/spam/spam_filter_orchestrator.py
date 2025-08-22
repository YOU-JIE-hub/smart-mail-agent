from __future__ import annotations
import re
from typing import Any, Dict

_SUS_LINK = re.compile(r"(https?://|t\\.co/|tinyurl\\.com/)", re.I)
_SUS_WORD = re.compile(r"(免費|中獎|限時|贈品|優惠|viagra|lottery|prize)", re.I)

class SpamFilterOrchestrator:
    """離線可用的簡化版 API（提供測試需要的方法）。"""
    def __init__(self, *_: Any, **__: Any) -> None: ...

    def is_legit(self, *, subject: str = "", content: str = "", sender: str = "") -> bool:
        s = f"{subject} {content}"
        if _SUS_LINK.search(s) and _SUS_WORD.search(s):
            return False  # 有可疑連結 + 關鍵字 → spam
        return True

    def run(self, payload: Dict[str, Any] | None = None, **kw: Any) -> Dict[str, Any]:
        subject = (payload or {}).get("subject") or kw.get("subject","")
        content = (payload or {}).get("body") or (payload or {}).get("content") or kw.get("content","")
        sender = (payload or {}).get("from") or kw.get("sender","")
        legit = self.is_legit(subject=subject, content=content, sender=sender)
        return {"is_spam": (not legit), "subject": subject, "sender": sender}

    # 別名
    def filter_email(self, *a: Any, **kw: Any) -> Dict[str, Any]:
        return self.run(*a, **kw)

    def evaluate(self, *a: Any, **kw: Any) -> Dict[str, Any]:
        return self.run(*a, **kw)

    def orchestrate(self, rule: str | None = None, *a: Any, **kw: Any) -> Dict[str, Any]:
        return self.run(*a, **kw)
