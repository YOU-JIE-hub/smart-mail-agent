"""Compatibility wrapper for `smart_mail_agent.policy_engine` via core module."""

from importlib import import_module

_core = import_module("smart_mail_agent.core.policy_engine")
apply_policies = getattr(_core, "apply_policies")
apply_policy = getattr(_core, "apply_policy", apply_policies)

__all__ = ["apply_policies", "apply_policy"]
