import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


@pytest.fixture(autouse=True, scope="session")
def _setup_env():
    os.environ.setdefault("OFFLINE", "1")
    sp = str(SRC)
    if sp not in sys.path:
        sys.path.insert(0, sp)
    yield


HAVE_TRANSFORMERS = importlib.util.find_spec("transformers") is not None
HAVE_REPORTLAB = importlib.util.find_spec("reportlab") is not None


def pytest_ignore_collect(path, config):
    p = str(path)
    if p.endswith("tests/test_classifier.py") and not HAVE_TRANSFORMERS:
        return True
    if p.endswith("tests/test_send_with_attachment.py") and not HAVE_REPORTLAB:
        return True
    return False


def pytest_collection_modifyitems(config, items):
    skip_online = pytest.mark.skip(reason="online tests disabled")
    for item in items:
        if "online" in item.keywords:
            item.add_marker(skip_online)
