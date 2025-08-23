from importlib import import_module as _im
try:
    _m = _im("smart_mail_agent.policy_engine")
    apply_policies = getattr(_m, "apply_policies")
except Exception:
    def apply_policies(email: dict, policies: dict | None = None) -> dict:
        return email
__all__ = ["apply_policies"]
