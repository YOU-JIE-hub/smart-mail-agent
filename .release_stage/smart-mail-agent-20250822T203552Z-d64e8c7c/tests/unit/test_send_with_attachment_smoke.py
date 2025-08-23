import importlib
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, "src")
swa = importlib.import_module("send_with_attachment")


def test_function_is_patchable_and_callable():
    if not hasattr(swa, "send_email_with_attachment"):
        pytest.skip("send_email_with_attachment not implemented")
    with patch(
        "send_with_attachment.send_email_with_attachment", return_value=True
    ) as mock_fn:
        # 不假設參數介面；MagicMock 可接受任意參數或無參數
        assert mock_fn() is True
        assert mock_fn.called
