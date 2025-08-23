from pathlib import Path
import sqlite3, importlib
st = importlib.import_module("smart_mail_agent.observability.stats_collector")

def test_stats_init_and_increment(tmp_path):
    st.DB_PATH = str(tmp_path/"s.db")  # 直接覆寫路徑
    st.init_stats_db()
    st.increment_counter("sales_inquiry", 0.123)
    with sqlite3.connect(st.DB_PATH) as c:
        cnt = c.execute("SELECT COUNT(*) FROM stats").fetchone()[0]
        assert cnt == 1
