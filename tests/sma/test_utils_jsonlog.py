import json
from pathlib import Path
import importlib
jl = importlib.import_module("smart_mail_agent.utils.jsonlog")

def test_log_event(tmp_path, monkeypatch):
    monkeypatch.setenv("SMA_LOG_DIR", str(tmp_path))
    res = {"ok":True}
    path = jl.log_event({"action_name":"x"},{"subject":"s","from":"u@x"}, res)
    assert path and Path(path).exists()
    # 檔案為 NDJSON，每行為 JSON
    lines = Path(path).read_text(encoding="utf-8").strip().splitlines()
    assert lines and lines[0].strip().startswith("{")
    assert "logged_path" in res
