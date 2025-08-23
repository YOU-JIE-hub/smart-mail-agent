import importlib
mod = importlib.import_module("smart_mail_agent.features.sales_notifier")
def test_notify_sales_stub():
    assert mod.notify_sales(client_name="A", package="B", pdf_path=None) is True
