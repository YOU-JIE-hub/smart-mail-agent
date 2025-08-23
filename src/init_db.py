from __future__ import annotations
__all__ = ["init_users_db", "init_emails_log_db", "init_processed_mails_db", "init_tickets_db"]

# Try to import real implementations; fallback to simple SQLite if missing.
try:
    from smart_mail_agent.ingestion.init_db import init_users_db as _real_init_users  # type: ignore
except Exception:
    _real_init_users = None  # type: ignore
try:
    from smart_mail_agent.ingestion.init_db import init_emails_log_db as _real_init_emails  # type: ignore
except Exception:
    _real_init_emails = None  # type: ignore
try:
    from smart_mail_agent.ingestion.init_db import init_processed_mails_db as _real_init_processed  # type: ignore
except Exception:
    _real_init_processed = None  # type: ignore
try:
    from smart_mail_agent.ingestion.init_db import init_tickets_db as _real_init_tickets  # type: ignore
except Exception:
    _real_init_tickets = None  # type: ignore

def _mk_db(path: str, ddl: str, ok_msg: str) -> str:
    import sqlite3
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as conn:
        conn.execute(ddl)
        conn.commit()
    print(f"{ok_msg} {p}")
    return str(p)

def init_users_db(db_path: str | None = None) -> str:
    if _real_init_users:
        return _real_init_users(db_path)  # type: ignore[misc]
    ddl = ("CREATE TABLE IF NOT EXISTS users ("
           "id INTEGER PRIMARY KEY, "
           "email TEXT UNIQUE)")
    return _mk_db(db_path or "data/users.db", ddl, "Initialized users DB at")

def init_emails_log_db(db_path: str | None = None) -> str:
    if _real_init_emails:
        return _real_init_emails(db_path)  # type: ignore[misc]
    ddl = ("CREATE TABLE IF NOT EXISTS emails_log ("
           "id INTEGER PRIMARY KEY, "
           "sender TEXT, subject TEXT, body TEXT, ts TEXT)")
    return _mk_db(db_path or "data/emails_log.db", ddl, "Initialized emails log DB at")

def init_processed_mails_db(db_path: str | None = None) -> str:
    if _real_init_processed:
        return _real_init_processed(db_path)  # type: ignore[misc]
    ddl = ("CREATE TABLE IF NOT EXISTS processed_mails ("
           "id INTEGER PRIMARY KEY, "
           "message_id TEXT UNIQUE, "
           "status TEXT, "
           "processed_at TEXT)")
    return _mk_db(db_path or "data/processed_mails.db", ddl, "Initialized processed mails DB at")

def init_tickets_db(db_path: str | None = None) -> str:
    if _real_init_tickets:
        return _real_init_tickets(db_path)  # type: ignore[misc]
    ddl = ("CREATE TABLE IF NOT EXISTS tickets ("
           "id INTEGER PRIMARY KEY, "
           "subject TEXT, "
           "status TEXT, "
           "created_at TEXT)")
    return _mk_db(db_path or "data/tickets.db", ddl, "Initialized tickets DB at")
