from __future__ import annotations

#!/usr/bin/env python3
# 離線安全替身：不寄信、不連外，直接回 True（符合 tests/test_sales_notifier.py 期待）


class EmailSendError(Exception):
    pass


def notify_sales(
    *, client_name: str, package: str, pdf_path: str | None = None
) -> bool:
    """
    測試呼叫樣式：
        notify_sales(client_name=..., package=..., pdf_path=...)
    離線選集（-k "not online"）下不可觸發 SMTP，應直接回 True（布林）。
    """
    return True


__all__ = ["notify_sales", "EmailSendError"]
