#!/usr/bin/env bash
set -Eeuo pipefail

# 建立與啟用 venv
python -m venv .venv 2>/dev/null || true
. .venv/bin/activate

# 安裝依賴
python -m pip -q install -U pip
pip -q install -r requirements.txt

# 安裝 .pth：讓所有子進程自動看到 <repo>/src
PYLIB=$(python - <<'PY'
import sysconfig
print(sysconfig.get_paths()['purelib'])
PY
)
echo "$PWD/src" > "$PYLIB/smart_mail_agent_src.pth"

echo "環境完成。使用：. .venv/bin/activate"
