from __future__ import annotations
import sqlite3
from typing import Dict, List

# --- helpers ---------------------------------------------------------------

def _ensure_schema(conn: sqlite3.Connection) -> None:
    """建立測試需要的兩張表（若不存在）。"""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            email   TEXT PRIMARY KEY,
            phone   TEXT,
            address TEXT
        );
        CREATE TABLE IF NOT EXISTS diff_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT,
            欄位        TEXT,
            原值        TEXT,
            新值        TEXT,
            created_at TEXT
        );
        """
    )

def _parse_content(content: str) -> Dict[str, str]:
    """從自然語句取出 phone/address（支援：冒號/全形冒號）。"""
    phone = None
    address = None
    for raw in (content or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        # 電話
        if line.startswith(("電話", "手機")):
            parts = line.split(":", 1) if ":" in line else line.split("：", 1)
            if len(parts) == 2:
                phone = parts[1].strip()
        # 地址
        elif line.startswith("地址"):
            parts = line.split(":", 1) if ":" in line else line.split("：", 1)
            if len(parts) == 2:
                address = parts[1].strip()
    out: Dict[str, str] = {}
    if phone:
        out["phone"] = phone
    if address:
        out["address"] = address
    return out

# --- public API ------------------------------------------------------------

def update_user_info(email: str, content: str, db_path: str) -> Dict[str, object]:
    """
    更新 SQLite 的 users(phone/address)，並寫 diff_log。
    回傳：
      - {"status":"updated","changes":[...]}
      - {"status":"no_change"}
      - {"status":"not_found"}
    """
    email = (email or "").strip()
    if not email:
        return {"status": "not_found"}

    conn = sqlite3.connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.cursor()

        # 取現況
        cur.execute("SELECT phone, address FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        if not row:
            return {"status": "not_found"}
        current_phone, current_address = row

        # 解析新內容
        patch = _parse_content(content)
        changes: List[str] = []

        # 計算差異
        new_phone   = current_phone
        new_address = current_address

        if "phone" in patch and patch["phone"] != current_phone:
            new_phone = patch["phone"]
            changes.append("phone")

        if "address" in patch and patch["address"] != current_address:
            new_address = patch["address"]
            changes.append("address")

        if not changes:
            return {"status": "no_change"}

        # 更新 users
        sets, params = [], []
        if "phone" in changes:
            sets.append("phone=?");   params.append(new_phone)
        if "address" in changes:
            sets.append("address=?"); params.append(new_address)
        params.append(email)
        cur.execute(f"UPDATE users SET {', '.join(sets)} WHERE email=?", tuple(params))

        # 寫 diff_log
        import datetime as _dt
        now = _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        for field in changes:
            old = current_phone if field == "phone" else current_address
            new = new_phone    if field == "phone" else new_address
            cur.execute(
                "INSERT INTO diff_log (email, 欄位, 原值, 新值, created_at) VALUES (?,?,?,?,?)",
                (email, field, old or "", new or "", now),
            )

        conn.commit()
        return {"status": "updated", "changes": changes}
    finally:
        conn.close()
