# 檔案位置：tests/test_mailer.py
# 測試模組：utils.mailer.py - 寄送帶附件的郵件功能

from unittest.mock import patch

import pytest

from utils.mailer import send_email_with_attachment, validate_smtp_config


# 建立假的附件檔案供測試用
@pytest.fixture(scope="module")
def fake_attachment(tmp_path_factory):
    fpath = tmp_path_factory.mktemp("data") / "testfile.txt"
    with open(fpath, "w") as f:
        f.write("這是測試附件內容")
    return str(fpath)


# 測試 SMTP 設定缺失時會 raise
def test_validate_smtp_config_missing_env(monkeypatch):
    for var in ["SMTP_USER", "SMTP_PASS", "SMTP_HOST", "SMTP_PORT"]:
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(ValueError, match="SMTP 設定錯誤"):
        validate_smtp_config()


# 測試正常寄信行為（mock smtplib 不實際寄出）
@patch("utils.mailer.smtplib.SMTP_SSL")
def test_send_email_with_attachment_success(mock_smtp, fake_attachment, monkeypatch):
    monkeypatch.setenv("SMTP_USER", "test@example.com")
    monkeypatch.setenv("SMTP_PASS", "password")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_FROM", "Smart-Mail-Agent <test@example.com>")

    result = send_email_with_attachment(
        recipient="receiver@example.com",
        subject="測試郵件",
        body_html="<p>這是測試</p>",
        attachment_path=fake_attachment,
    )
    assert result is True
    assert mock_smtp.called


# 測試當附件不存在時拋出例外
def test_send_email_attachment_not_found(monkeypatch):
    monkeypatch.setenv("SMTP_USER", "test@example.com")
    monkeypatch.setenv("SMTP_PASS", "password")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_FROM", "Smart-Mail-Agent <test@example.com>")

    with pytest.raises(FileNotFoundError):
        send_email_with_attachment(
            recipient="a@b.com",
            subject="x",
            body_html="",
            attachment_path="/tmp/non_exist_file.pdf",
        )
