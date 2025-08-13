#!/usr/bin/env bash
set -euo pipefail
summ() {
  local f="$1"
  if command -v jq >/dev/null 2>&1; then
    jq -r '"action_name="+(.action_name|tostring),"subject="+(.subject|tostring),"meta="+(.meta|tostring),"attachments="+(.attachments|tostring),""' "$f"
  else
    echo "== $f =="; cat "$f"
  fi
}
echo "=== out_sales ===";      summ data/output/out_sales.json
echo "=== out_quote ===";      summ data/output/out_quote.json
echo "=== out_overlimit ===";  summ data/output/out_overlimit.json
echo "=== out_whitelist ===";  summ data/output/out_whitelist.json
