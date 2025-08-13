#!/usr/bin/env bash
set -Eeuo pipefail
trap 'ec=$?; echo "❌ patch+run failed at line $LINENO (exit $ec)"; exit $ec' ERR
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT"
if [[ -f .venv/bin/activate ]]; then . .venv/bin/activate; else python3 -m venv .venv; . .venv/bin/activate; python -m pip -q install -U pip; [[ -f requirements.txt ]] && pip -q install -r requirements.txt || true; fi
mkdir -p src/utils utils logs data/output
: > src/utils/__init__.py; : > utils/__init__.py

# 永不丟例外 logger（若已存在仍覆寫成穩定版）
cat > src/utils/jsonlog.py <<'PY'
#!/usr/bin/env python3
from __future__ import annotations
import json, os, datetime as dt
from pathlib import Path
from typing import Any, Dict, Optional

def _log_dir() -> Path:
    d = Path(os.getenv("SMA_LOG_DIR", "logs"))
    d.mkdir(parents=True, exist_ok=True)
    return d

def _jsonable(x: Any):
    try:
        json.dumps(x)
        return x
    except Exception:
        return str(x)

def log_event(result: Dict[str, Any], request: Optional[Dict[str, Any]] = None) -> str:
    try:
        p = _log_dir() / f"sma-{dt.datetime.now():%Y%m%d}.jsonl"
        row = {
            "ts": dt.datetime.now().isoformat(timespec="seconds"),
            "level": "INFO",
            "action_name": result.get("action_name"),
            "ok": bool(result.get("ok", True)),
            "code": result.get("code", "OK"),
            "request_id": result.get("request_id"),
            "intent": result.get("intent"),
            "confidence": result.get("confidence"),
            "duration_ms": result.get("duration_ms") or result.get("spent_ms"),
            "dry_run": result.get("dry_run"),
            "warnings": result.get("warnings") or [],
        }
        if isinstance(request, dict):
            row["req_subject"] = request.get("subject")
            row["req_from"] = request.get("from")
        row = {k: _jsonable(v) for k, v in row.items()}
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return str(p)
    except Exception:
        try:
            (_log_dir() / "log_event_error.txt").write_text(
                f"[{dt.datetime.now().isoformat(timespec='seconds')}] log_event failed\n",
                encoding="utf-8"
            )
        except Exception:
            pass
        return ""
PY

# 根目錄 proxy（避免 flake8 F403）
cat > utils/jsonlog.py <<'PY'
"""Compatibility proxy to canonical logger."""
from src.utils.jsonlog import log_event  # noqa: F401
PY

# Smoke ＋ 雙案例
PYTHONPATH=src python - <<'PY'
from utils.jsonlog import log_event
p = log_event({"action_name":"_smoke_","ok":True,"code":"OK","request_id":"smoke"}, {"subject":"S","from":"T"})
print("logger_ok:", bool(p))
PY
cat > data/output/in_sales.json <<'JSON'
{"subject":"詢價與合作","from":"alice@partner.co","body":"想了解報價與合作方案。"}
JSON
cat > data/output/in_complaint.json <<'JSON'
{"subject":"嚴重投訴","from":"bob@example.com","body":"我的訂單延誤，請儘速協助。"}
JSON
PYTHONPATH=src python -X dev -m src.run_action_handler --input data/output/in_sales.json --output data/output/out_sales.json --dry-run
PYTHONPATH=src python -X dev -m src.run_action_handler --input data/output/in_complaint.json --output data/output/out_complaint.json --dry-run
python - <<'PY'
import json, os, datetime as dt, sys
ok=True
for f in ("data/output/out_sales.json","data/output/out_complaint.json"):
    d = json.load(open(f,"r",encoding="utf-8"))
    lp = d.get("logged_path"); warns = d.get("warnings") or []
    print(f"{f}: logged_path={lp} | warnings={warns}")
    if (not lp) or any("log_write_failed" in str(w) for w in warns): ok=False
log = os.path.join("logs", f"sma-{dt.datetime.now():%Y%m%d}.jsonl")
print("log file:", log, "(存在)" if os.path.exists(log) else "(不存在)")
if os.path.exists(log):
    print("---- tail ----")
    print("\n".join(open(log,"r",encoding="utf-8").read().splitlines()[-5:]))
sys.exit(0 if ok else 2)
PY
echo "🎉 patch+verify done."
