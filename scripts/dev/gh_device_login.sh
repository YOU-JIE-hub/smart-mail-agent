#!/usr/bin/env bash
set -euo pipefail

# 1) 啟動裝置登入流程（終端機會顯示一組代碼：XXXX-XXXX）
echo "[info] 先看終端機的『First copy your one-time code:』那行，複製代碼"
gh auth login --hostname github.com --git-protocol https --device || true

# 2) 幫你在 Windows 開登入頁（若可用）
powershell.exe /c start https://github.com/login/device 2>/dev/null || true
explorer.exe "https://github.com/login/device" 2>/dev/null || true

echo
echo "[next] 把剛剛複製的代碼貼到瀏覽器頁面，完成授權後回到這邊按 Enter 繼續"
read -r _

# 3) 驗證登入狀態
echo "[info] 檢查 gh 登入狀態…"
gh auth status

echo "[ok] 登入成功。如果要繼續把 .env 寫到 GitHub Secrets，跑：make gh-secrets"
echo "[ok] 觸發線上寄信測試：make ci-smtp  ；觀看執行：make ci-watch"
