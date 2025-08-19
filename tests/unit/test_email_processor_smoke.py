import importlib
from typing import Any, Dict

def test_extract_fields_minimal():
    mod = importlib.import_module("smart_mail_agent.email_processor")
    assert hasattr(mod, "extract_fields"), "extract_fields 不存在"
    sample = {
        "subject": "Hi",
        "from": "alice@example.com",
        "body": "hello",
        "attachments": [],
    }
    out: Dict[str, Any] = mod.extract_fields(sample)  # type: ignore[attr-defined]
    # 必要鍵存在且型別合理（鬆綁判斷，避免耦合具體格式）
    for k in ("subject", "from", "body", "attachments"):
        assert k in out
    assert isinstance(out.get("attachments"), list)

def test_extract_fields_with_attachments():
    mod = importlib.import_module("smart_mail_agent.email_processor")
    attach = [{"filename": "a.txt", "content_type": "text/plain"}]
    sample = {
        "subject": "Files",
        "from": "bob@example.com",
        "body": "see files",
        "attachments": attach,
    }
    out = mod.extract_fields(sample)  # type: ignore[attr-defined]
    assert out["attachments"]  # 至少非空
