import sqlite3

from smart_mail_agent.utils.log_writer import log_to_db


def test_log_to_db_writes_row(tmp_path):
    db = tmp_path / "emails_log.db"
    rid = log_to_db("s", "c", "sum", "lbl", 0.9, "act", "", db_path=db)
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT subject, predicted_label, action FROM emails_log WHERE rowid=?",
            (rid,),
        ).fetchone()
        assert row == ("s", "lbl", "act")
