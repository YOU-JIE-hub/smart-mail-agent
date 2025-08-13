# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

LOG_PATH = os.environ.get("SMA_LOG_PATH", "logs/actions.log")


def jlog(event: str, **fields):
    rec = {"ts": datetime.utcnow().isoformat() + "Z", "event": event}
    rec.update(fields)
    line = json.dumps(rec, ensure_ascii=False)
    try:
        p = Path(LOG_PATH)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    print(line)
