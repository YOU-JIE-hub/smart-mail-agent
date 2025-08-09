#!/usr/bin/env bash
set -euo pipefail

# 0) 安裝 gh（Ubuntu/WSL）
if ! command -v gh >/dev/null 2>&1; then
  echo "[info] installing GitHub CLI..."
  sudo apt update
  if ! sudo apt -y install gh; then
    # 官方套件庫（若發行版沒有 gh）
    type -p curl >/dev/null || sudo apt -y install curl
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
    sudo apt update && sudo apt -y install gh
  fi
fi
gh --version

# 1) gh 登入（會在 Windows 開瀏覽器授權）
echo "[info] gh auth login ..."
gh auth status || gh auth login --hostname github.com --web

# 2) 確保目前專案具備 GitHub 遠端
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "[info] no origin remote, creating repo on GitHub and pushing..."
  # 直接用資料夾名當 repo 名稱（smart-mail-agent）
  gh repo create --public --source . --remote origin --push --confirm
fi

# 3) 推 .env 到 GitHub Secrets（使用現有工具）
chmod +x tools/push_secrets_from_env.sh || true
./tools/push_secrets_from_env.sh

# 4) 觸發 CI（SMTP 線上測試）
echo "[info] trigger workflow: SMTP Online Test"
gh workflow run "SMTP Online Test" || gh workflow run ".github/workflows/smtp-online.yml"

# 5) 追蹤狀態（顯示最近一次工作與即時 watch）
echo "== recent runs =="
gh run list --limit 5
echo "== watching =="
gh run watch
