#!/usr/bin/env python3
from __future__ import annotations
from smart_mail_agent.ingestion.init_db import (
    ensure_dir,
    init_users_db,
    init_tickets_db,
    init_emails_log_db,
    init_processed_mails_db,
    main as _impl_main,
)

__all__ = [
    "ensure_dir",
    "init_users_db",
    "init_tickets_db",
    "init_emails_log_db",
    "init_processed_mails_db",
    "main",
]


def main() -> None:
    _impl_main()


if __name__ == "__main__":
    main()
