from importlib import import_module as _im
try:
    _mod = _im("smart_mail_agent.routing.action_handler")
    for _k in dir(_mod):
        if not _k.startswith("_"):
            globals()[_k] = getattr(_mod, _k)
    __all__ = getattr(_mod, "__all__", [k for k in globals() if not k.startswith("_")])
except Exception:  # 最小降級
    def route_action(*_a, **_k): return {"routed": False, "reason": "compat-fallback"}
    __all__ = ["route_action"]
del _im, _mod
