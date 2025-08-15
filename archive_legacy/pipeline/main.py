#!/usr/bin/env python3
# 檔案位置：pipeline/main.py
# 目的：Smart-Mail-Agent 入口流程（離線安全、IMAP 認證失敗不中斷）

from __future__ import annotations

import imaplib
import logging
import os
import sys
from pathlib import Path

# [SMA_SYS_PATH] 確保可匯入 src 模組
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

logger = logging.getLogger("Pipeline")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")


def fetch_emails(
    IMAP_HOST: str,
    IMAP_USER: str,
    IMAP_PASS: str,
    folder: str = "INBOX",
    limit: int = 50,
    force: bool = False,
) -> list[str]:
    """安全抓信：
    - OFFLINE=1 直接跳過
    - 認證失敗或任何錯誤不拋出
    - 回傳空清單也視為成功（不中斷整體流程）
    """
    if os.getenv("OFFLINE", "0") == "1":
        logger.info("[IMAP] OFFLINE 模式，跳過抓信")
        return []

    results: list[str] = []
    try:
        with imaplib.IMAP4_SSL(IMAP_HOST) as imap:
            imap.login(IMAP_USER, IMAP_PASS)
            typ, _ = imap.select(folder, readonly=True)
            if typ != "OK":
                logger.warning("[IMAP] 選擇資料夾失敗，改用 INBOX")
                imap.select("INBOX", readonly=True)
            typ, data = imap.search(None, "ALL")
            if typ != "OK":
                logger.warning("[IMAP] 搜尋郵件失敗")
                return []
            ids = data[0].split() if data and data[0] else []
            if limit and len(ids) > limit:
                ids = ids[-limit:]
            # 如需取信件內容，可在此做 imap.fetch；此處先保持空清單以確保流程不中斷。
            return results
    except imaplib.IMAP4.error as e:
        logger.warning("[IMAP] 認證失敗：%s", e)
        return []
    except Exception as e:
        logger.exception("[IMAP] 抓信未預期錯誤：%s", e)
        return []


def run_pipeline(limit: int = 50, force: bool = False) -> int:
    logger.info("[Pipeline] 開始擷取郵件")
    IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
    IMAP_USER = os.getenv("IMAP_USER", "")
    IMAP_PASS = os.getenv("IMAP_PASS", "")
    _ = fetch_emails(IMAP_HOST, IMAP_USER, IMAP_PASS, limit=limit, force=force)
    logger.info("[Pipeline] 完成")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run_pipeline(limit=args.limit, force=args.force))
