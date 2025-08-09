#!/usr/bin/env python3
# 檔案位置：src/spam/spam_filter_orchestrator.py
# 模組用途：依序整合 Rule → ML → LLM 三階段垃圾信判斷邏輯

from typing import Any, Dict

from spam.ml_spam_classifier import SpamBertClassifier
from spam.rule_filter import RuleBasedSpamFilter
from spam.spam_llm_filter import SpamLLMFilter
from utils.logger import logger

SPAM_THRESHOLD = 0.75
WHITELIST_DOMAINS = ["@example.com", "@trusted.org", ".gov", ".edu"]


class SpamFilterOrchestrator:
    """
    統一垃圾信檢測流程主控器，依序處理：
        1. Rule-Based 關鍵字與黑名單
        2. BERT ML 預測（具信心值）
        3. LLM 語意判斷（可選）
    回傳統一格式：
        { allow: bool, stage: str, reason: str }
    """

    def __init__(self, model_path: str = "model/bert_spam_classifier"):
        self.rule_filter = RuleBasedSpamFilter()
        self.ml_model = SpamBertClassifier(model_path)
        self.llm_filter = SpamLLMFilter()

    def is_legit(self, subject: str, content: str, sender: str = "") -> Dict[str, Any]:
        """
        主程序呼叫：進行垃圾信多階段判斷

        :param subject: 信件標題
        :param content: 信件內容
        :param sender: 寄件者 Email
        :return: Dict { allow, stage, reason }
        """
        full_text = f"{subject.strip()}\n{content.strip()}"

        # L0 - Rule Filter
        if self.rule_filter.is_spam(full_text):
            logger.info("[SpamFilter] L0 規則命中，判定為垃圾信")
            return {"allow": False, "stage": "rule", "reason": "關鍵字或黑名單"}

        # L1 - ML 預測
        ml_result = self.ml_model.predict(subject, content)
        if ml_result["label"] == "spam" and ml_result["confidence"] >= SPAM_THRESHOLD:
            logger.info("[SpamFilter] L1 ML 模型判定為垃圾信 (%.2f)", ml_result["confidence"])
            return {
                "allow": False,
                "stage": "ml",
                "reason": f"ML 模型信心值 {ml_result['confidence']}",
            }

        # L2 - LLM 判斷
        if self.llm_filter.is_suspicious(subject, content):
            logger.info("[SpamFilter] L2 LLM 判定為垃圾信")
            return {"allow": False, "stage": "llm", "reason": "LLM 語意判斷疑似詐騙"}

        # Whitelist Domain (optional record)
        if any(domain in sender.lower() for domain in WHITELIST_DOMAINS):
            logger.info("[SpamFilter] 寄件人來自白名單網域：%s", sender)

        # 正常信件
        return {"allow": True, "stage": "none", "reason": "通過所有檢查"}
