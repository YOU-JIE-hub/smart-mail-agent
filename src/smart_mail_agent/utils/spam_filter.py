from __future__ import annotations
from typing import Dict, List

class SpamFilterOrchestrator:
    def is_legit(self, subject: str = "", content: str = "", sender: str = "") -> Dict:
        reasons: List[str] = []
        text = f"{subject} {content}".lower()
        kw = ["免費", "贈品", "中獎", "點此", "下載附件登入"]
        if any(k in text for k in kw):
            reasons.append("zh_keywords")
        if sender and sender.split("@")[-1].endswith(("unknown-domain.com", "example.netx")):
            reasons.append("suspicious_domain")
        is_spam = len(reasons) > 0
        return {"is_spam": is_spam, "allow": not is_spam, "reasons": reasons}
