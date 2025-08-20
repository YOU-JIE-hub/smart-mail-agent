#!/usr/bin/env python3
# 檔案位置：src/send_with_attachment.py
# 模組用途：寄信 shim，委派到 smart_mail_agent/ingestion/integrations/send_with_attachment.py
from __future__ import annotations
from smart_mail_agent.ingestion.integrations.send_with_attachment import (
    send_email_with_attachment,
    main as _main,
)
if __name__ == "__main__":
    _main()
