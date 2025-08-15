#!/usr/bin/env bash
set -Eeuo pipefail
trap 'ec=$?; echo "❌ failed at line $LINENO (exit $ec)"; exit $ec' ERR

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# venv
if [[ ! -f .venv/bin/activate ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate
if [[ -f requirements.txt && ! -f .venv/.deps_installed ]]; then
  python -m pip -q install -U pip
  pip -q install -r requirements.txt || true
  touch .venv/.deps_installed
fi

mkdir -p logs data/output src/utils utils
: > src/utils/__init__.py
: > utils/__init__.py

# 覆寫：穩定 jsonlog（永不丟例外；成功時回填 result["logged_path"]）
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
        result["logged_path"] = str(p)
        if result.get("warnings"):
            result["warnings"] = [w for w in result["warnings"] if w != "log_write_failed"]
        return str(p)
    except Exception:
        result.setdefault("warnings", []).append("log_write_failed")
        return ""
PY

# 根目錄 utils 代理（明確 re-export）
cat > utils/jsonlog.py <<'PY'
"""Compatibility proxy to canonical implementation."""
from src.utils.jsonlog import log_event  # noqa: F401
PY

# 跑 sample（非互動）
if [[ -x bin/smarun ]]; then
  bin/smarun
else
  PYTHONPATH=src python -m src.run_action_handler --input data/output/in_sales.json --output data/output/out_sales.json --dry-run
  PYTHONPATH=src python -m src.run_action_handler --input data/output/in_complaint.json --output data/output/out_complaint.json --dry-run
fi

# 驗證 logged_path 與 JSONL
python - <<'PY'
import json, os, datetime as dt
for f in ("data/output/out_sales.json","data/output/out_complaint.json"):
    d=json.load(open(f,"r",encoding="utf-8"))
    print(f"{f}: logged_path={d.get('logged_path')} | warnings={d.get('warnings')}")
lp=f"logs/sma-{dt.datetime.now():%Y%m%d}.jsonl"
print("log file exists:", os.path.exists(lp), lp)
if os.path.exists(lp):
    print("---- tail ----")
    print("\n".join(open(lp,"r",encoding="utf-8").read().splitlines()[-5:]))
PY

# 可選自動提交
if [[ "${DO_COMMIT:-0}" == "1" ]]; then
  BRANCH="${BRANCH:-main}"
  git add bin/smarun tools/one_shot_patch_and_run.sh src/utils/jsonlog.py utils/jsonlog.py || true
  git commit -m "feat(scripts): add non-interactive runner and one-shot patch+verify" || true
  git add -u || true
  git commit -m "style: pre-commit fixes" || true
  git push origin "$BRANCH"
fi

echo "✅ done"
