import pathlib
import sqlite3

from smart_mail_agent.features.support import support_ticket as st


def _reset_db():
    p = pathlib.Path(st.DB_PATH)
    if p.exists():
        p.unlink()


def test_create_list_show_update(capsys):
    _reset_db()
    st.create_ticket("主旨A", "內容A", sender="u@x", category="Bug", confidence=0.7)
    st.list_tickets()
    out1 = capsys.readouterr().out
    assert "最新工單列表" in out1 or "工單列表" in out1

    # 讀取第一筆 id
    with sqlite3.connect(st.DB_PATH) as conn:
        row = conn.execute(
            f"SELECT id FROM {st.TABLE} ORDER BY id DESC LIMIT 1"
        ).fetchone()
        tid = row[0]

    st.show_ticket(tid)
    out2 = capsys.readouterr().out
    assert f"ID         : {tid}" in out2

    st.update_ticket(tid, status="done", summary="完成")
    with sqlite3.connect(st.DB_PATH) as conn:
        row = conn.execute(
            f"SELECT status, summary FROM {st.TABLE} WHERE id=?", (tid,)
        ).fetchone()
        assert row == ("done", "完成")
