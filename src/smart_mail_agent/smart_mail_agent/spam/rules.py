from importlib import import_module as _import_module
_mod = _import_module("smart_mail_agent.spam.rules")
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
