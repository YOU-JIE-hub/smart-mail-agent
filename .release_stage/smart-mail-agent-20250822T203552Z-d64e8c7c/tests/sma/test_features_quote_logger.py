from pathlib import Path
import importlib, sqlite3
mod = importlib.import_module("smart_mail_agent.features.quote_logger")

def test_quote_logger_e2e(tmp_path):
    db = tmp_path/"q.db"
    mod.ensure_db_exists(str(db))
    mod.log_quote("客戶A","專業", "/tmp/quote.pdf", db_path=str(db))
    row = mod.get_latest_quote(db_path=str(db))
    assert row and row[0]=="客戶A" and row[1]=="專業"
