import importlib
def test_send_with_attachment_has_entry():
    m = importlib.import_module("send_with_attachment")
    assert hasattr(m, "send_email_with_attachment")
