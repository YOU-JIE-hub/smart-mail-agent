# === GitHub CLI / Secrets / CI (auto-generated) ===

gh-install:
	@sudo apt update && sudo apt install -y gh || true

gh-login:
	@gh auth status || gh auth login

gh-secrets:
	@tools/push_secrets_from_env.sh

ci-smtp:
	@gh workflow run "SMTP Online Test" || gh workflow run ".github/workflows/smtp-online.yml"

ci-watch:
	@gh run list --limit 5
	@gh run watch
