"""Compatibility shim: use smart_mail_agent.cli.sma_spamcheck

This file stays for backward-compat imports/tests:
  python -m smart_mail_agent.cli_spamcheck
  from smart_mail_agent import cli_spamcheck
"""

from smart_mail_agent.cli.sma_spamcheck import main  # re-export

if __name__ == "__main__":
    raise SystemExit(main())
