# Smart Mail Agent

[![Release](https://img.shields.io/github/v/release/YOU-JIE-hub/smart-mail-agent?include_prereleases&label=release)](https://github.com/YOU-JIE-hub/smart-mail-agent/releases)
[![Downloads](https://img.shields.io/github/downloads/YOU-JIE-hub/smart-mail-agent/total.svg?label=downloads)](https://github.com/YOU-JIE-hub/smart-mail-agent/releases)

單一命名空間 `smart_mail_agent`，並保留 `utils/*`、`src/actions/__init__.py`、`src/utils/*` 作為舊匯入相容層。

## 開發
```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
pytest -q

# 一鍵清理/標準化/測試/打包/commit+tag/推分支/開PR（直接整段貼上執行）
bash <<'ONE'
set -Eeuo pipefail
trap 'rc=$?; echo "❌ FAIL (exit $rc) @ line ${BASH_LINENO[0]}: ${BASH_COMMAND}" >&2; exit $rc' ERR

REPO_URL="${REPO_URL:-https://github.com/YOU-JIE-hub/smart-mail-agent.git}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/smart-mail-agent}"
PKG="smart_mail_agent"
BRANCH="oneclick-$(date +%Y%m%d-%H%M%S)"

echo "▶ repo: $REPO_URL"
echo "▶ dir : $PROJECT_DIR"
echo "▶ br  : $BRANCH"

# 0) 取得專案 / 切分支
[ -d "$PROJECT_DIR/.git" ] || { mkdir -p "$(dirname "$PROJECT_DIR")"; git clone "$REPO_URL" "$PROJECT_DIR"; }
cd "$PROJECT_DIR"
if ! git diff --quiet || ! git diff --cached --quiet; then git add -A; git commit -m "snapshot: before one-click polish" || true; fi
git fetch -q origin || true
git checkout -B "$BRANCH"

# 1) 命名空間與相容層
mkdir -p "src/$PKG/actions" "src/$PKG/utils" utils src/actions src/utils

cat > utils/__init__.py <<'PY'
from smart_mail_agent.utils import *  # noqa: F401,F403
PY
cat > utils/logger.py <<'PY'
from smart_mail_agent.utils.logger import *  # noqa: F401,F403
PY
cat > utils/mailer.py <<'PY'
from smart_mail_agent.utils.mailer import *  # noqa: F401,F403
PY

cat > src/actions/__init__.py <<'PY'
from smart_mail_agent.actions import *  # noqa: F401,F403
PY
cat > src/utils/__init__.py <<'PY'
from smart_mail_agent.utils import *  # noqa: F401,F403
PY
cat > src/utils/logger.py <<'PY'
from smart_mail_agent.utils.logger import *  # noqa: F401,F403
PY
cat > src/utils/mailer.py <<'PY'
from smart_mail_agent.utils.mailer import *  # noqa: F401,F403
PY

# 2) pytest 設定
cat > pytest.ini <<'INI'
[pytest]
testpaths = tests
pythonpath = src
INI

# 3) 單一 README
mkdir -p docs/README-archive
for f in $(ls README* 2>/dev/null | grep -vx 'README.md' || true); do
  mv -f "$f" "docs/README-archive/" || true
done
cat > README.md <<'MD'
# Smart Mail Agent

[![Release](https://img.shields.io/github/v/release/YOU-JIE-hub/smart-mail-agent?include_prereleases&label=release)](https://github.com/YOU-JIE-hub/smart-mail-agent/releases)
[![Downloads](https://img.shields.io/github/downloads/YOU-JIE-hub/smart-mail-agent/total.svg?label=downloads)](https://github.com/YOU-JIE-hub/smart-mail-agent/releases)

單一命名空間 `smart_mail_agent`，保留 `utils/*`、`src/actions/__init__.py`、`src/utils/*` 為舊匯入相容層。

## 開發
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
pytest -q

## 打包
python -m pip install -U build
python -m build
