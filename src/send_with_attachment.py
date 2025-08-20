#!/usr/bin/env python3
# 檔案位置：src/send_with_attachment.py
# 作用：寄信 shim，對外提供 main()，內部委派到正式實作
from __future__ import annotations

from smart_mail_agent.ingestion.integrations.send_with_attachment import (
    send_email_with_attachment,
    main as _delegate_main,
)

__all__ = ["send_email_with_attachment", "main"]

def main() -> int | None:  # 給測試與 CLI 呼叫
    return _delegate_main()

if __name__ == "__main__":
    # 直接執行腳本時，走相同入口
    raise SystemExit(main() or 0)
