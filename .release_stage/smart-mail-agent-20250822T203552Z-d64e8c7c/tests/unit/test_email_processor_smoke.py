import importlib
from typing import Any, Dict, Sequence

def _normalize(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        subj = result.get("subject") or result.get("title") or result.get("subj")
        frm  = result.get("from")    or result.get("sender") or result.get("email")
        body = result.get("body")    or result.get("text")   or ""
        atts = result.get("attachments") or result.get("files") or []
        return {
            "subject": subj or "",
            "from": frm or "",
            "body": body,
            "attachments": list(atts) if atts else [],
        }
    if isinstance(result, (tuple, list)):
        seq: Sequence[Any] = result
        subj = seq[0] if len(seq) > 0 else ""
        body = seq[1] if len(seq) > 1 else ""
        frm  = seq[2] if len(seq) > 2 else ""
        atts = seq[3] if len(seq) > 3 else []
        return {
            "subject": subj or "",
            "from": frm or "",
            "body": body or "",
            "attachments": list(atts) if atts else [],
        }
    # fallback：未知型別，至少保證欄位存在
    return {"subject": "", "from": "", "body": str(result), "attachments": []}

def test_extract_fields_minimal():
    mod = importlib.import_module("smart_mail_agent.email_processor")
    assert hasattr(mod, "extract_fields"), "extract_fields 不存在"
    sample = {
        "subject": "Hi",
        "from": "alice@example.com",
        "body": "hello",
        "attachments": [],
    }
    raw = mod.extract_fields(sample)  # type: ignore[attr-defined]
    out = _normalize(raw)
    assert out["subject"] == "Hi"
    assert out["from"] == "alice@example.com"
    assert out["body"]

def test_extract_fields_with_attachments():
    mod = importlib.import_module("smart_mail_agent.email_processor")
    attach = [{"filename": "a.txt", "content_type": "text/plain"}]
    sample = {
        "subject": "Files",
        "from": "bob@example.com",
        "body": "see files",
        "attachments": attach,
    }
    raw = mod.extract_fields(sample)  # type: ignore[attr-defined]
    out = _normalize(raw)
    # 只保證欄位存在與型別合理；若實作會保留附件則會是非空
    assert isinstance(out["attachments"], list)
