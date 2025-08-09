#!/usr/bin/env python3
# 檔案位置：scripts/run_all.py
# 模組用途：一鍵執行：初始化 DB →（可 OFFLINE）→ 檢查 emails_log

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 確保可匯入 src.* 與 utils.*（src 裡面的模組常用絕對匯入 from utils.*）
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

os.environ.setdefault("PYTHONPATH", "src")

# 固定用 src.log_writer（離線種資料要用）
try:
    from src.log_writer import log_to_db  # type: ignore
except Exception as e:  # pragma: no cover
    print("[seed] 無法匯入 src.log_writer：", e)
    log_to_db = None  # type: ignore


def run(cmd):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def seed_demo_rows():
    if log_to_db is None:
        print("[seed] 找不到 log_to_db，略過示範資料注入")
        return
    samples = [
        dict(
            subject="我要報價",
            content="請問企業版報價與合約",
            summary="詢問報價",
            label="業務接洽或報價",
            confidence=0.92,
            action="demo",
            error="",
        ),
        dict(
            subject="忘記密碼",
            content="登入失敗求協助",
            summary="技術支援",
            label="請求技術支援",
            confidence=0.88,
            action="demo",
            error="",
        ),
        dict(
            subject="功能建議",
            content="希望新增黑名單匯入",
            summary="建議",
            label="其他",
            confidence=0.70,
            action="demo",
            error="",
        ),
    ]
    for s in samples:
        log_to_db(
            subject=s["subject"],
            content=s["content"],
            summary=s["summary"],
            label=s["label"],
            confidence=s["confidence"],
            action=s["action"],
            error=s["error"],
        )
    print("[seed] 已寫入 3 筆示範資料至 emails_log")


def main():
    # 1) 初始化 DB
    rc = run([sys.executable, "init_db.py"])
    if rc != 0:
        print("[ERR] init_db 失敗")
        sys.exit(rc)

    # 2) schema 遷移（合併/補欄位）
    mig = ROOT / "tools" / "db_migrate_emails_log.py"
    if mig.exists():
        rc = run([sys.executable, str(mig)])
        if rc != 0:
            print("[WARN] emails_log 遷移腳本回傳非 0")
    else:
        print("[WARN] 找不到 tools/db_migrate_emails_log.py（建議保留）")

    offline = os.getenv("OFFLINE", "0") == "1"

    # 3) 跑 pipeline（若存在且非 offline）
    pipe = ROOT / "pipeline" / "main.py"
    if not offline and pipe.exists():
        rc = run([sys.executable, "pipeline/main.py", "--limit", "20", "--force"])
        if rc != 0:
            print("[WARN] pipeline 執行回傳非 0（可設 OFFLINE=1 先 demo）")
    else:
        print("[INFO] OFFLINE 模式或找不到 pipeline/main.py：跳過抓信，注入示範資料…")
        seed_demo_rows()

    # 4) 檢查結果
    checker = ROOT / "scripts" / "check_email_log.py"
    if checker.exists():
        run([sys.executable, str(checker)])
    else:
        print("[INFO] 未找到 scripts/check_email_log.py，略過結果檢查")


if __name__ == "__main__":
    main()
