#!/usr/bin/env python3
# 檔案位置：src/smart_mail_agent/smart_mail_agent/spam/__init__.py
# 模組用途：修正多餘巢狀命名空間，統一轉接至 smart_mail_agent.spam
from __future__ import annotations
from ...spam import *  # noqa: F401,F403
