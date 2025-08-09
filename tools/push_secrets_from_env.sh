#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "[ERR] gh (GitHub CLI) 未安裝。可用：sudo apt update && sudo apt install -y gh"
  exit 1
fi

if [[ ! -f ".env" ]]; then
  echo "[ERR] 找不到 .env"
  exit 1
fi

# 從 .env 取值（若鍵不存在就空字串）
function getenv() { awk -F= -v k="$1" '$1==k {sub(/^"|"$/,"",$2);print $2}' .env | tr -d '\r'; }

SMTP_USER="$(getenv SMTP_USER)"
SMTP_PASS="$(getenv SMTP_PASS)"
REPLY_TO="$(getenv REPLY_TO)"
SMTP_HOST="$(getenv SMTP_HOST)"
SMTP_PORT="$(getenv SMTP_PORT)"
SMTP_FROM="$(getenv SMTP_FROM)"
IMAP_HOST="$(getenv IMAP_HOST)"
IMAP_USER="$(getenv IMAP_USER)"
IMAP_PASS="$(getenv IMAP_PASS)"
OPENAI_API_KEY="$(getenv OPENAI_API_KEY)"

echo "[info] 寫入 GitHub Secrets ..."
gh secret set SMTP_USER --body "$SMTP_USER"
gh secret set SMTP_PASS --body "$SMTP_PASS"
gh secret set REPLY_TO  --body "$REPLY_TO"
# 選配
[[ -n "$SMTP_HOST" ]] && gh secret set SMTP_HOST --body "$SMTP_HOST"
[[ -n "$SMTP_PORT" ]] && gh secret set SMTP_PORT --body "$SMTP_PORT"
[[ -n "$SMTP_FROM" ]] && gh secret set SMTP_FROM --body "$SMTP_FROM"
[[ -n "$IMAP_HOST" ]] && gh secret set IMAP_HOST --body "$IMAP_HOST"
[[ -n "$IMAP_USER" ]] && gh secret set IMAP_USER --body "$IMAP_USER"
[[ -n "$IMAP_PASS" ]] && gh secret set IMAP_PASS --body "$IMAP_PASS"
[[ -n "$OPENAI_API_KEY" ]] && gh secret set OPENAI_API_KEY --body "$OPENAI_API_KEY"

echo "[ok] 完成。可到 Actions 觸發 'SMTP Online Test'"
