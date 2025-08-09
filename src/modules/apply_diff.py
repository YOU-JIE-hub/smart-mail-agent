#!/usr/bin/env python3
# 檔案位置：src/modules/apply_diff.py
# 模組用途：解析使用者信件內容，從 users.db 中比對異動欄位並更新資料與記錄差異。

import re
import sqlite3
from datetime import datetime
from typing import Any, Dict

from utils.logger import logger

DB_PATH: str = "data/users.db"  # 可由外部 CLI 或環境變數注入路徑


def extract_fields(content: str) -> Dict[str, Any]:
    """
    從信件內容中擷取聯絡資料欄位（電話與地址）

    參數:
        content (str): 信件內容（純文字）

    回傳:
        dict: 擷取出的欄位內容，如 {'phone': '09xx...', 'address': '...'}
    """
    fields = {}
    phone_match = re.search(r"(電話|手機)[：: ]*([0-9\-]{7,})", content)
    addr_match = re.search(r"(地址)[：: ]*(.+)", content)

    if phone_match:
        fields["phone"] = phone_match.group(2).strip()
    if addr_match:
        fields["address"] = addr_match.group(2).strip()

    return fields


def update_user_info(email: str, content: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    依據信件內容比對與更新使用者資料，若有異動則寫入 diff_log

    參數:
        email (str): 使用者 Email（主鍵）
        content (str): 使用者信件內容
        db_path (str): 資料庫路徑（預設：data/users.db）

    回傳:
        dict: 狀態資訊，例如:
              - {"status": "not_found", "email": ...}
              - {"status": "no_change", "email": ...}
              - {"status": "updated", "email": ..., "changes": {...}}
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT phone, address FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if not row:
            logger.warning("[ApplyDiff] 查無使用者：%s", email)
            return {"status": "not_found", "email": email}

        old_data = {"phone": row[0], "address": row[1]}
        new_fields = extract_fields(content)

        changed: Dict[str, Dict[str, Any]] = {}
        for key, new_val in new_fields.items():
            if key in old_data and new_val != old_data[key]:
                changed[key] = {"old": old_data[key], "new": new_val}
                cursor.execute(f"UPDATE users SET {key} = ? WHERE email = ?", (new_val, email))
                cursor.execute(
                    """
                    INSERT INTO diff_log (email, 欄位, 原值, 新值, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        email,
                        key,
                        old_data[key],
                        new_val,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )

        conn.commit()
        conn.close()

        if not changed:
            logger.info("[ApplyDiff] 無異動：%s", email)
            return {"status": "no_change", "email": email}

        logger.info("[ApplyDiff] 使用者 %s 已更新欄位：%s", email, list(changed.keys()))
        return {"status": "updated", "email": email, "changes": changed}

    except Exception as e:
        logger.error(f"[ApplyDiff] 處理過程失敗：{e}")
        return {"status": "error", "email": email, "error": str(e)}
