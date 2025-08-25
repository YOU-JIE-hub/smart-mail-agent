from smart_mail_agent.core.policy_engine import *  # re-export by AP-15
"""
Compatibility wrapper for `smart_mail_agent.policy_engine`.

- Re-exports everything from `smart_mail_agent.core.policy_engine`
- Ensures `apply_policies` is available for legacy imports:
    from smart_mail_agent.policy_engine import apply_policies
"""
from importlib import import_module
from types import SimpleNamespace as _NS

_core = import_module("smart_mail_agent.core.policy_engine")

# Re-export everything public from core
for _k, _v in _core.__dict__.items():
    if not _k.startswith("_"):
        globals()[_k] = _v

# Provide a compat entrypoint if missing
if "apply_policies" not in globals():
    def apply_policies(*args, **kwargs):
        """
        Compat shim: try common entrypoints in core.policy_engine.
        Preference:
          1) core.apply_policies
          2) core.PolicyEngine().apply_policies / .apply / .run / .evaluate
          3) core.apply / core.run / core.evaluate
        """
        # 1) direct function
        for fn in ("apply_policies",):
            if hasattr(_core, fn):
                return getattr(_core, fn)(*args, **kwargs)
        # 2) class instance methods (common names)
        if hasattr(_core, "PolicyEngine"):
            _pe = getattr(_core, "PolicyEngine")()
            for m in ("apply_policies", "apply", "run", "evaluate"):
                if hasattr(_pe, m):
                    return getattr(_pe, m)(*args, **kwargs)
        # 3) module-level fallbacks
        for fn in ("apply", "run", "evaluate"):
            if hasattr(_core, fn):
                return getattr(_core, fn)(*args, **kwargs)
        raise AttributeError(
            "smart_mail_agent.core.policy_engine 未提供可用的 apply 入口（apply_policies/apply/run/evaluate）。"
        )

# keep a clean __all__
__all__ = [k for k in globals().keys() if not k.startswith("_")]


# AP15_ALIAS_BLOCK: begin (auto-added by AP-15)
# 目標：兼容 from policy_engine import apply_policy / apply_policies
try:
    apply_policies  # type: ignore[name-defined]
except Exception:
    def apply_policies(*args, **kwargs):  # type: ignore
        from smart_mail_agent.core import policy_engine as _pe
        return _pe.apply_policies(*args, **kwargs)

try:
    apply_policy  # type: ignore[name-defined]
except Exception:
    apply_policy = apply_policies  # type: ignore

# 對齊 __all__
try:
    __all__  # type: ignore[name-defined]
    for _n in ("apply_policies","apply_policy"):
        if _n not in __all__:
            __all__.append(_n)
except Exception:
    __all__ = ["apply_policies","apply_policy"]
# AP15_ALIAS_BLOCK: end

