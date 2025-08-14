#!/usr/bin/env bash
set -Eeuo pipefail
trap 'ec=$?; echo "❌ failed at line $LINENO (exit $ec)"; exit $ec' ERR

# 0) 專案與環境
ROOT="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$ROOT"

if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
else
  python3 -m venv .venv
  . .venv/bin/activate
  python -m pip -q install -U pip
  [ -f requirements.txt ] && pip -q install -r requirements.txt || true
fi
mkdir -p logs data/output src/utils utils
: > src/utils/__init__.py
: > utils/__init__.py

# 1) 偵測 jsonlog 是否可用，否則修補成穩定版（never-throw）
python - <<'PY' || {
  import importlib, json, os, sys, datetime as dt
  try:
    sys.path.insert(0, "src")
    jl = importlib.import_module("utils.jsonlog") if os.path.exists("utils/jsonlog.py") \
         else importlib.import_module("src.utils.jsonlog")
  except Exception as e:
    raise SystemExit("jsonlog import failed: %s" % e)
  # smoke test
  result = {"action_name":"_smoke_","ok":True,"code":"OK","request_id":"smoke-1"}
  req = {"subject":"S","from":"T"}
  p = jl.log_event(result, req)
  assert isinstance(p, str) and p, "no path returned"
  assert os.path.isfile(p), "path not exists"
  assert result.get("logged_path"), "logged_path not set"
  print("jsonlog OK:", p)
PY

if [ "$?" -ne 0 ]; then
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
    """Never raise; write a JSONL row and set result['logged_path'] on success."""
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
        # success → 回填 logged_path 並移除舊的 log_write_failed
        result["logged_path"] = str(p)
        if result.get("warnings"):
            result["warnings"] = [w for w in result["warnings"] if w != "log_write_failed"]
        return str(p)
    except Exception:
        result.setdefault("warnings", []).append("log_write_failed")
        return ""
PY
  echo "✓ patched src/utils/jsonlog.py"
fi

# 2) 跑 sample 並驗證（非互動）
bin/smarun

python - <<'PY'
import json, sys, os, datetime as dt
def check(p):
    d = json.load(open(p, "r", encoding="utf-8"))
    lp = d.get("logged_path"); warns = d.get("warnings") or []
    print(f"{p}: logged_path={lp} | warnings={warns}")
    assert lp and "log_write_failed" not in warns
for f in ("data/output/out_sales.json","data/output/out_complaint.json"):
    check(f)
logp = f"logs/sma-{dt.datetime.now():%Y%m%d}.jsonl"
print("log file:", logp, "(存在)" if os.path.exists(logp) else "(不存在)")
if os.path.exists(logp):
    print("---- tail ----")
    print("\n".join(open(logp,"r",encoding="utf-8").read().splitlines()[-5:]))
PY

# 3) 可選：自動提交
if [ "${DO_COMMIT:-0}" = "1" ]; then
  BRANCH="${BRANCH:-main}"
  git add bin/smarun tools/one_shot_patch_and_run.sh || true
  [ -f src/utils/jsonlog.py ] && git add src/utils/jsonlog.py || true
  git commit -m "feat(scripts): add non-interactive runner and one-shot patch+verify" || true
  git add -u || true
  git commit -m "style: pre-commit fixes" || true
  git push origin "$BRANCH"
fi

echo "🎉 完成"
