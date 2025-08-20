#!/usr/bin/env python3
# 檔案位置：src/smart_mail_agent/features/spam/__init__.py
# 模組用途：相容舊路徑之垃圾信功能匯入，統一轉接至 smart_mail_agent.spam
from __future__ import annotations
from ...spam import *  # noqa: F401,F403
