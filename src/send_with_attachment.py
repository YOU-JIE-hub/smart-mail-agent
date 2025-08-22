from __future__ import annotations
# 允許 tests 直接 import 本模組並檢查符號存在
from utils.mailer import send_email_with_attachment  # re-export
__all__ = ["send_email_with_attachment"]
