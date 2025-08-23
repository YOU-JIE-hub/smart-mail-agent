from pathlib import Path
import sqlite3, importlib
lw = importlib.import_module("smart_mail_agent.observability.log_writer")

def test_log_to_db(tmp_path):
    db = tmp_path/"e.db"
    rowid = lw.log_to_db(subject="s", content="c", summary="",
                         predicted_label="sales", confidence=0.9,
                         action="send_quote", error="", db_path=str(db))
    assert isinstance(rowid, int) and rowid >= 1
    # 查核
    with sqlite3.connect(str(db)) as conn:
        cnt = conn.execute("SELECT COUNT(*) FROM emails_log").fetchone()[0]
        assert cnt >= 1
