#!/usr/bin/env bash
set -euo pipefail
root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root"

echo "=== 未逐行展開（Ruff: E701/E702/E703/E704）的檔案 ==="
ruff check --select E701,E702,E703,E704 --output-format=json src tests 2>/dev/null \
| python3 - <<'PY'
import json,sys;
try:
    data=json.load(sys.stdin)
except Exception:
    data=[]
seen=set(d.get("filename","") for d in data if d.get("filename"))
for f in sorted(seen):
    print(f)
PY

echo
echo "=== 自最近一次 'chore: checkpoint' 以來未被改動的 .py（可能未處理） ==="
last_cp=$(git log --grep='chore: checkpoint' -n 1 --pretty=%H || true)
if [ -n "${last_cp:-}" ]; then
  git diff --name-only "$last_cp"..HEAD | sort -u > /tmp/touched.lst
else
  # 找不到就用最初始提交當基準
  git diff --name-only $(git rev-list --max-parents=0 HEAD)..HEAD | sort -u > /tmp/touched.lst
fi
git ls-files 'src/**/*.py' 'tests/**/*.py' | sort -u > /tmp/all_py.lst
comm -23 /tmp/all_py.lst /tmp/touched.lst
