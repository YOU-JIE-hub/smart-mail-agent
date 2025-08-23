from __future__ import annotations

import json
from pathlib import Path

from email_processor import write_classification_result


def test_write_classification_result_reversed_order(tmp_path):
    dest = tmp_path / "r.json"
    p = write_classification_result(str(dest), {"x": 1, "y": "ok"})
    assert Path(p).exists()
    data = json.loads(Path(p).read_text(encoding="utf-8"))
    assert data["x"] == 1 and data["y"] == "ok"
