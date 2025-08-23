import importlib
import sys

import pytest

sys.path.insert(0, "src")
mod = importlib.import_module("patches.handle_safe_patch")


def test_apply_safe_patch_minimal():
    fn = getattr(mod, "apply_safe_patch", None)
    if fn is None:
        pytest.skip("apply_safe_patch not implemented")
    out = fn({"priority": "low", "attachments": [], "content": "hello"})
    assert isinstance(out, dict)
    assert "priority" in out
