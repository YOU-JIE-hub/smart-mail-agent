import importlib
mod = importlib.import_module("send_with_attachment")
assert hasattr(mod, "send_email_with_attachment")
