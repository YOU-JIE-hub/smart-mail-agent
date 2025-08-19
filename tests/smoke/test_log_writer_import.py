import importlib
def test_log_writer_importable():
    importlib.import_module("smart_mail_agent.observability.log_writer")
