import importlib
import smtplib as smtplib  # 供 tests patch 的目標

_impl = importlib.import_module("src.utils.mailer")
_impl.smtplib = smtplib  # 讓 src 實作使用到同一個 smtplib 物件（patch 才會生效）

send_email_with_attachment = _impl.send_email_with_attachment
validate_smtp_config = _impl.validate_smtp_config

__all__ = ["send_email_with_attachment", "validate_smtp_config", "smtplib"]
