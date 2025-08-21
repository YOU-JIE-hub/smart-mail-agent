from importlib import import_module as _import_module

# 來源：smart_mail_agent.routing.action_handler
_mod = _import_module("smart_mail_agent.routing.action_handler")

# 將所有非底線成員直接 re-export，確保舊用法 `from action_handler import route_action` 可用
for _k in dir(_mod):
    if not _k.startswith("_"):
        globals()[_k] = getattr(_mod, _k)

# 若上游有 __all__ 就用；否則導出所有非底線
__all__ = getattr(_mod, "__all__", [k for k in globals() if not k.startswith("_")])

del _import_module, _mod
