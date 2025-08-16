import importlib


def _has_api(mod):
    return any(hasattr(mod, n) for n in ("apply_policy", "PolicyEngine"))


def test_policy_engine_old_new_paths_importable():
    m1 = importlib.import_module("policy_engine")
    m2 = importlib.import_module("smart_mail_agent.policy_engine")
    assert _has_api(m1) or _has_api(m2)
