from importlib import import_module as _import_module
_mod = _import_module("smart_mail_agent.routing.action_handler")
for _k in dir(_mod):
    if not _k.startswith("_"):
        globals()[_k] = getattr(_mod, _k)
__all__ = getattr(_mod, "__all__", [k for k in globals() if not k.startswith("_")])
del _import_module, _mod
