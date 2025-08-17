import json
import pathlib
import tempfile

from smart_mail_agent.email_processor import extract_fields, write_classification_result


def test_extract_fields_various_keys():
    data = {"title": "t", "body": "b", "from": "f"}
    s, b, f = extract_fields(data)
    assert (s, b, f) == ("t", "b", "f")


def test_write_classification_result_writes_json(tmp_path):
    p = tmp_path / "x.json"
    write_classification_result({"a": 1}, str(p))
    assert json.loads(p.read_text(encoding="utf-8"))["a"] == 1
