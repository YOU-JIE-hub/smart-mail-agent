# 檔案位置：tests/test_send_with_attachment.py
# 模組用途：測試 send_with_attachment CLI 是否能正常觸發主流程

import os
import tempfile
from unittest import mock

import send_with_attachment as swa


@mock.patch("send_with_attachment.send_email_with_attachment")
def test_send_with_attachment_cli_success(mock_send):
    """測試 CLI 呼叫能正確觸發寄信行為"""
    mock_send.return_value = True

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = "%PDF-1.4\n% 測試內容\n".encode()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        args = [
            "--to",
            "recipient@example.com",
            "--subject",
            "測試郵件",
            "--body",
            "<h1>測試 HTML</h1>",
            "--file",
            tmp_path,
        ]

        with mock.patch("sys.argv", ["send_with_attachment.py"] + args):
            swa.main()

        mock_send.assert_called_once()

    finally:
        os.remove(tmp_path)
