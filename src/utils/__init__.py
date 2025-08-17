"""Compatibility shim for legacy imports like:

from utils.logger import logger
from utils.jsonlog import log_event
"""

from __future__ import annotations

import sys as _sys
from importlib import import_module as _imp


def _alias(src: str, dst: str) -> None:
    try:
        _sys.modules[src] = _imp(dst)
    except Exception:
        # 不讓相容層成為阻斷點
        pass


_MAP = {
    "utils.logger": "smart_mail_agent.utils.logger",
    "utils.jsonlog": "smart_mail_agent.utils.jsonlog",
    "utils.mailer": "smart_mail_agent.utils.mailer",
    "utils.db_tools": "smart_mail_agent.utils.db_tools",
    "utils.env": "smart_mail_agent.utils.env",
    "utils.errors": "smart_mail_agent.utils.errors",
    "utils.config": "smart_mail_agent.utils.config",
    "utils.validators": "smart_mail_agent.utils.validators",
    "utils.fonts": "smart_mail_agent.utils.fonts",
    "utils.font_check": "smart_mail_agent.utils.font_check",
    "utils.pdf_safe": "smart_mail_agent.utils.pdf_safe",
    "utils.pdf_generator": "smart_mail_agent.utils.pdf_generator",
    "utils.logging_setup": "smart_mail_agent.utils.logging_setup",
    "utils.log_writer": "smart_mail_agent.utils.log_writer",
    "utils.imap_login": "smart_mail_agent.utils.imap_login",
    "utils.imap_folder_detector": "smart_mail_agent.utils.imap_folder_detector",
    "utils.priority_evaluator": "smart_mail_agent.utils.priority_evaluator",
    "utils.tracing": "smart_mail_agent.utils.tracing",
    "utils.templater": "smart_mail_agent.utils.templater",
}
for _s, _d in _MAP.items():
    _alias(_s, _d)
