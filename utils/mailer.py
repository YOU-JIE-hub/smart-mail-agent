import importlib
import smtplib as smtplib  # 供測試 patch 的目標

_impl = importlib.import_module("src.utils.mailer")
_impl.smtplib = smtplib
send_email_with_attachment = _impl.send_email_with_attachment
validate_smtp_config = _impl.validate_smtp_config
__all__ = ["send_email_with_attachment", "validate_smtp_config", "smtplib"]
