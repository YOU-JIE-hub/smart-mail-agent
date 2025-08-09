#!/usr/bin/env python3
# 檔案：tools/apply_imap_debug_v2.py
# 作用：覆寫 scripts/imap_debug.py，修正檔首縮排/三引號造成的語法錯誤

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scripts" / "imap_debug.py"

CONTENT = """#!/usr/bin/env python3
# 檔案：scripts/imap_debug.py
# 目的：用 .env 的 IMAP_* 做連線與登入測試，輸出細節與常見修法提示

from __future__ import annotations
import os
import imaplib
import ssl

# 載入 .env
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def main() -> int:
    host = os.getenv("IMAP_HOST", "")
    user = os.getenv("IMAP_USER", "")
    pwd = os.getenv("IMAP_PASS", "")
    folder = os.getenv("IMAP_FOLDER", "INBOX")

    print(f"[IMAP] host={host} folder={folder} user={user}")
    if not all([host, user, pwd]):
        print("[IMAP] 參數不足：請設定 IMAP_HOST / IMAP_USER / IMAP_PASS")
        return 2

    try:
        ctx = ssl.create_default_context()
        with imaplib.IMAP4_SSL(host, ssl_context=ctx) as im:
            print("[IMAP] 嘗試登入…")
            im.login(user, pwd)
            print("[IMAP] 登入成功")
            typ, _ = im.select(folder, readonly=True)
            print(f"[IMAP] select {folder}：{typ}")
            typ, data = im.search(None, "ALL")
            ids = data[0].split() if (typ == "OK" and data and data[0]) else []
            print(f"[IMAP] 搜尋 ALL：{typ}，可見郵件數：{len(ids)}")
            return 0
    except imaplib.IMAP4.error as e:
        print(f"[IMAP][AUTH] 認證失敗：{e}")
        print(
            "== 常見修法 ==\\n"
            "1) Gmail → 設定 → 轉寄與 POP/IMAP → 啟用 IMAP\\n"
            "2) 必須使用『應用程式密碼』當作 IMAP_PASS（不是一般登入密碼）\\n"
            "3) 兩步驟驗證開啟後，到『Google 帳戶→安全性→應用程式密碼』產生 16 碼\\n"
            "4) 產生的 16 碼請去除空白貼到 .env（避免隱藏空白）\\n"
            "5) SMTP_PASS 與 IMAP_PASS 可分開各自生成（建議）"
        )
        return 1
    except Exception as e:
        print(f"[IMAP][ERR] 一般錯誤：{e!r}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(CONTENT, encoding="utf-8")
    print(f"[ok] 寫入 {OUT}")


if __name__ == "__main__":
    main()
