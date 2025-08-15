#!/usr/bin/env python3
# 檔案位置：spam/spam_filter_orchestrator.py
# 模組用途：相容層，轉發至 smart_mail_agent.spam

from importlib import import_module as _imp

_SF = _imp("smart_mail_agent.spam.spam_filter_orchestrator")
SpamFilterOrchestrator = _SF.SpamFilterOrchestrator
