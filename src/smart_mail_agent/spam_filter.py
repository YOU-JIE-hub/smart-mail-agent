from __future__ import annotations
import os, re
from typing import Dict, List

ZH_SPAM_WORDS = ["免費","中獎","贈品","點此","立即領取","優惠碼"]
EN_SPAM_WORDS = ["FREE","WIN","BONUS","CLICK","DISCOUNT"]

def _score_rules(subject: str, content: str, sender: str) -> (float, List[str]):
    text = f"{subject} {content}".lower()
    reasons: List[str] = []

    if any(w.lower() in text for w in ZH_SPAM_WORDS+EN_SPAM_WORDS):
        reasons.append("zh_keywords")

    # 簡單短連結/可疑網址偵測
    if re.search(r"(tinyurl\.com|bit\.ly|t\.co|http[s]?://)", text):
        reasons.append("shortlink")

    # 多收件人/群發跡象（由呼叫端決定，這裡用 sender 網域啟發式）
    if sender and sender.endswith("@unknown-domain.com"):
        reasons.append("unknown_domain")

    # 單一規則 0.4 分、最高 1.0
    score = min(1.0, 0.4 * len(reasons))
    return score, reasons

class SpamFilterOrchestrator:
    def __init__(self, threshold: float | None = None):
        self.threshold = threshold if threshold is not None else float(os.getenv("SPAM_THRESHOLD", "0.5"))

    def is_legit(self, *, subject: str = "", content: str = "", sender: str = "") -> Dict[str, object]:
        score, reasons = _score_rules(subject or "", content or "", sender or "")
        is_spam = score >= self.threshold
        return {"is_spam": is_spam, "allow": (not is_spam), "reasons": reasons, "score": score}
