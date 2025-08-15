#!/usr/bin/env python3
# 檔案位置：bootstrap_project.py
# 模組用途：一鍵建立/更新 Smart-Mail-Agent 專案必要檔案與結構（可加 --force 覆蓋）

import argparse
import os  # noqa: F401
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent

FILES = {
    # -------------------- 開發/測試設定 --------------------
    "pyproject.toml": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：pyproject.toml
        # 模組用途：定義 black / isort / flake8 / mypy 統一規範

        [tool.black]
        target-version = ["py311"]
        line-length = 100
        include = '\\.pyi?$'
        exclude = '''
        /(
          \\.venv
        | \\.git
        | data
        | dist
        | build
        )/
        '''

        [tool.isort]
        profile = "black"
        line_length = 100
        src_paths = ["src", "tests", "scripts"]

        [tool.flake8]
        max-line-length = 100
        extend-ignore = ["E203","W503"]
        exclude = [".venv","data","build","dist",".git"]

        [tool.mypy]
        python_version = "3.11"
        ignore_missing_imports = true
        warn_redundant_casts = true
        warn_unused_ignores = true
        warn_return_any = false
        no_implicit_optional = true
        strict_optional = false
    """
    ).lstrip(),
    ".editorconfig": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：.editorconfig
        # 模組用途：統一 IDE/編輯器行為（縮排、換行、編碼）

        root = true

        [*]
        charset = utf-8
        end_of_line = lf
        insert_final_newline = true
        trim_trailing_whitespace = true
        indent_style = space
        indent_size = 4

        [*.md]
        trim_trailing_whitespace = false
    """
    ).lstrip(),
    "pytest.ini": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：pytest.ini
        # 模組用途：pytest 探測與輸出統一

        [pytest]
        testpaths = tests
        addopts = -q -ra
        filterwarnings =
            ignore::DeprecationWarning
        pythonpath = src
    """
    ).lstrip(),
    ".pre-commit-config.yaml": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：.pre-commit-config.yaml
        # 模組用途：git 提交前自動格式/檢查

        repos:
          - repo: https://github.com/psf/black
            rev: 24.4.2
            hooks:
              - id: black
          - repo: https://github.com/pycqa/isort
            rev: 5.13.2
            hooks:
              - id: isort
          - repo: https://github.com/pycqa/flake8
            rev: 7.0.0
            hooks:
              - id: flake8
    """
    ).lstrip(),
    "Makefile": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：Makefile
        # 模組用途：提供常用開發指令（安裝、格式、檢查、測試、稽核）

        .PHONY: init fmt lint test audit all

        init:
\tpython -m venv .venv && . .venv/bin/activate && pip install -U pip
\t. .venv/bin/activate && pip install -r requirements.txt
\t. .venv/bin/activate && pip install black isort flake8 mypy pre-commit
\tpre-commit install

        fmt:
\t. .venv/bin/activate && isort .
\t. .venv/bin/activate && black .

        lint:
\t. .venv/bin/activate && flake8 .
\t. .venv/bin/activate && mypy src || true

        test:
\t. .venv/bin/activate && PYTHONPATH=src pytest -q

        audit:
\t. .venv/bin/activate && python tools/repo_tidy.py --check

        all: fmt lint test audit
    """
    ).lstrip(),
    "requirements.txt": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：requirements.txt
        # 模組用途：專案必要套件（去重版）

        accelerate>=0.26.0
        beautifulsoup4
        datasets>=2.18.0
        email-validator
        fpdf2
        matplotlib
        openai>=1.12.0
        pydantic>=2
        python-dotenv
        pytest>=7.0.0
        pytest-html
        rich>=13.0.0
        scikit-learn
        sentencepiece
        tabulate>=0.9.0
        tenacity>=8.0.1
        tiktoken
        tqdm
        torch>=2.0.0
        transformers>=4.41.1
    """
    ).lstrip(),
    ".gitignore": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：.gitignore
        # 模組用途：忽略不需版控的檔案

        .venv/
        __pycache__/
        .pytest_cache/
        .mypy_cache/
        .DS_Store
        data/
        !data/.keep
        logs/
        !logs/.keep
        *.db
        .env
        .coverage
        dist/
        build/
    """
    ).lstrip(),
    ".env.example": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：.env.example
        # 模組用途：環境變數樣板（請複製為 .env 並填入正確值）

        # SMTP
        SMTP_USER=your_account@gmail.com
        SMTP_PASS=app_password_here
        SMTP_HOST=smtp.gmail.com
        SMTP_PORT=465
        SMTP_FROM=Smart-Mail-Agent <your_account@gmail.com>
        REPLY_TO=your_account@gmail.com

        # OpenAI（缺少時系統自動降級，不中斷）
        OPENAI_API_KEY=

        # IMAP（選配）
        IMAP_HOST=imap.gmail.com
        IMAP_USER=your_account@gmail.com
        IMAP_PASS=app_password_here

        # 字型
        QUOTE_FONT_PATH=assets/fonts/NotoSansTC-Regular.ttf

        # 模型
        CLASSIFIER_PATH=outputs/roberta-zh-checkpoint

        # 輸出
        OUTPUT_DIR=data/output
    """
    ).lstrip(),
    "README.md": dedent(
        """
        # Smart-Mail-Agent（企業可部署版）

        ## 快速開始
        ```bash
        python -m venv .venv && . .venv/bin/activate
        pip install -U pip -r requirements.txt
        cp .env.example .env  # 填入 SMTP 等
        python init_db.py     # 建置 emails_log / users+diff_log / processed_mails / tickets
        ```

        ## 一鍵驗證
        ```bash
        make all           # 格式檢查 + 靜態檢查 + 測試 + 稽核
        PYTHONPATH=src python scripts/check_email_log.py
        ```

        ## 端到端（如有 pipeline/main.py）
        ```bash
        PYTHONPATH=src python pipeline/main.py --limit 10
        ```
    """
    ).lstrip(),
    # -------------------- src/ 核心模組 --------------------
    "src/__init__.py": "",
    "src/action_handler.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：src/action_handler.py
        # 模組用途：根據分類結果執行對應處理（工單/異動/RAG/客訴/報價）並記錄統計

        import os  # noqa: F401
        import json
        import time
        import argparse
        import subprocess
        from datetime import datetime
        from utils.logger import logger
        from utils.db_tools import get_user_by_email
        from utils.log_writer import log_to_db
        from utils.rag_reply import generate_rag_reply
        from utils.mailer import send_email_with_attachment
        from quotation import choose_package, generate_pdf_quote
        from quote_logger import log_quote
        from leads_logger import log_lead
        from stats_collector import increment_counter

        def handle_tech_support(data: dict) -> str:
            logger.info("[action_handler] 處理技術支援工單")
            subprocess.run([
                "python", "src/support_ticket.py", "create",
                "--subject", data.get("subject",""),
                "--content", data.get("body",""),
                "--summary", data.get("summary",""),
                "--sender", data.get("sender",""),
                "--category", data.get("predicted_label",""),
                "--confidence", str(data.get("confidence",0))
            ], check=True)
            return "已建立工單"

        def handle_info_change(data: dict) -> str:
            logger.info("[action_handler] 處理資料異動申請")
            try:
                result = subprocess.run([
                    "python", "src/apply_diff.py",
                    "--email", data.get("sender",""),
                    "--content", data.get("body","")
                ], capture_output=True, text=True, check=True)
                output = json.loads(result.stdout or "{}")
                status = output.get("status","")
                pdf_path = output.get("pdf_path","")
                if status == "updated" and pdf_path and os.path.exists(pdf_path):
                    send_email_with_attachment(
                        recipient=data.get("sender",""),
                        subject="RE: 資料異動確認",
                        body_html="<p>您好，附件為您的異動紀錄 PDF，已完成處理。</p>",
                        attachment_path=pdf_path
                    )
                    return "已更新欄位 + 已寄出 PDF"
                elif status == "no_change":
                    return "無異動"
                else:
                    return "未辨識結果"
            except Exception as e:
                logger.error("[action_handler] 處理 info_change 失敗：%s", e)
                raise

        def handle_general_inquiry(data: dict) -> str:
            logger.info("[action_handler] 啟動 RAG 回覆流程")
            query = data.get("body","")
            kb_path = "data/knowledge/faq.md"
            answer = generate_rag_reply(query, kb_path)
            html_body = f"<p>您好，根據您的問題，我們提供以下說明：</p><p>{answer}</p><p>若仍有疑問，歡迎回信詢問。</p>"
            send_email_with_attachment(
                recipient=data.get("sender",""),
                subject=f"RE: {data.get('subject','')}",
                body_html=html_body
            )
            return "已使用 RAG 回信"

        def handle_complaint(data: dict) -> str:
            logger.info("[action_handler] 處理客訴信件")
            email = data.get("sender") or data.get("email")
            subject = data.get("subject","")
            user = get_user_by_email("data/users.db", email)
            name = user.get("name") if user else "貴賓"
            html = f\"\"\"<p>{name}您好：</p>
            <p>我們已收到您的寶貴意見，對於此次造成的不便，我們深感抱歉。</p>
            <p>我們將轉交專人儘速處理，並努力避免類似情況再次發生。</p>
            <p>若有任何補充需求，歡迎直接回覆此信。</p>
            <p>客服團隊 敬上<br>{datetime.now().strftime('%Y-%m-%d')}</p>\"\"\"
            send_email_with_attachment(recipient=email, subject=f"RE: {subject} - 很抱歉造成您的困擾", body_html=html)
            return "已寄送道歉信"

        def handle_quotation(data: dict) -> str:
            logger.info("[action_handler] 處理報價需求")
            subject = data.get("subject",""); content = data.get("body",""); sender = data.get("sender","")
            sel = choose_package(subject, content)
            if sel.get("needs_manual"):
                send_email_with_attachment(recipient=sender, subject=f"RE: {subject} - 已收到需求",
                                           body_html="<p>您好，已收到您的需求，專人將盡速與您聯繫。</p>")
                return "待人工處理"
            pdf_path = generate_pdf_quote(sel["package"], sender)
            send_email_with_attachment(recipient=sender, subject=f"RE: {subject} - 報價單",
                                       body_html=f"<p>您好，附件為 <b>{sel['package']}</b> 報價單，若有疑問歡迎回覆。</p>",
                                       attachment_path=pdf_path)
            log_quote(sender, sel["package"], pdf_path, sent_status="success")
            log_lead(sender, sel["package"], pdf_path)
            return f"已寄送 {sel['package']} 報價單"

        def handle_unknown(data: dict) -> str:
            logger.info("[action_handler] 未定義行為：%s", data.get("predicted_label"))
            return "未定義行為，已紀錄"

        def route_action(label: str, data: dict) -> None:
            subject = data.get("subject",""); body = data.get("body",""); summary = data.get("summary","")
            sender = data.get("sender") or data.get("email") or data.get("recipient")
            confidence = float(data.get("confidence",0)); error = ""; action_result = "none"; start = time.time()
            try:
                handlers = {
                    "請求技術支援": handle_tech_support,
                    "申請修改資訊": handle_info_change,
                    "詢問流程或規則": handle_general_inquiry,
                    "投訴與抱怨": handle_complaint,
                    "業務接洽或報價": handle_quotation
                }
                handler = handlers.get(label, handle_unknown)
                action_result = handler(data)
            except Exception as e:
                error = str(e); logger.error("[action_handler] 執行 '%s' 失敗：%s", label, error)
            try:
                log_to_db(subject=subject, content=body, summary=summary, label=label,
                          confidence=confidence, action=action_result, error=error)
            except Exception as e:
                logger.warning("[action_handler] log 寫入失敗：%s", e)
            elapsed = round(time.time() - start, 3)
            increment_counter(label, elapsed)
            logger.info("[action_handler] 統計完成：%s (+1)，耗時 %.3fs", label, elapsed)

        def main():
            ap = argparse.ArgumentParser(description="根據分類結果觸發對應處理")
            ap.add_argument("--json", required=True, help="分類結果 JSON 檔案路徑")
            args = ap.parse_args()
            with open(args.json, encoding="utf-8") as f:
                data = json.load(f)
            label = data.get("predicted_label","其他")
            logger.info("[action_handler] 執行分類：%s → %s", args.json, label)
            route_action(label, data)

        if __name__ == "__main__":
            main()
    """
    ).lstrip(),
    "src/log_writer.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：src/log_writer.py
        # 模組用途：寫入郵件處理結果到 emails_log 資料表

        import os  # noqa: F401
        import sqlite3
        from datetime import datetime
        from utils.logger import logger

        DB_PATH = "data/emails_log.db"
        TABLE = "emails_log"

        def ensure_log_table(db_path: str = DB_PATH) -> None:
            try:
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                with sqlite3.connect(db_path) as conn:
                    conn.execute(f\"\"\"
                        CREATE TABLE IF NOT EXISTS {TABLE} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            subject TEXT,
                            content TEXT,
                            summary TEXT,
                            predicted_label TEXT,
                            confidence REAL,
                            action TEXT,
                            error TEXT,
                            created_at TEXT
                        )
                    \"\"\")
                    conn.commit()
                logger.debug("[log_writer] emails_log 資料表確認完成")
            except Exception as e:
                logger.warning("[log_writer] 建表失敗：%s", e)

        def log_to_db(subject: str, content: str, label: str, confidence: float,
                      summary: str = "", action: str = "", error: str = "", db_path: str = DB_PATH) -> None:
            try:
                ensure_log_table(db_path)
                with sqlite3.connect(db_path) as conn:
                    conn.execute(f\"\"\"
                        INSERT INTO {TABLE} (subject, content, summary, predicted_label,
                                             confidence, action, error, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    \"\"\", (
                        (subject or "").strip(),
                        (content or "").strip(),
                        (summary or "").strip(),
                        (label or "").strip(),
                        float(confidence or 0.0),
                        (action or "").strip(),
                        (error or "").strip(),
                        datetime.utcnow().isoformat()
                    ))
                    conn.commit()
                logger.info("[log_writer] 已記錄：%s / %s / 信心 %.4f", label, action, confidence)
            except Exception as e:
                logger.warning("[log_writer] 寫入失敗：%s", e)
    """
    ).lstrip(),
    "src/inference_classifier.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：src/inference_classifier.py
        # 模組用途：對外統一 classify_intent()；內部委派到 classifier.IntentClassifier

        import os  # noqa: F401
        import json
        import argparse
        from utils.logger import logger

        DEFAULT_CLASSIFIER_PATH = os.getenv("CLASSIFIER_PATH", "outputs/roberta-zh-checkpoint")

        def classify_intent(subject: str, content: str) -> dict:
            try:
                from classifier import IntentClassifier
                clf = IntentClassifier(model_path=DEFAULT_CLASSIFIER_PATH)
                res = clf.classify(subject=subject, content=content)
                return {"label": res.get("predicted_label","unknown"), "confidence": float(res.get("confidence",0.0))}
            except Exception as e:
                logger.error("[IntentClassifier] 推論失敗：%s", e)
                return {"label": "unknown", "confidence": 0.0}

        def main():
            ap = argparse.ArgumentParser(description="繁體郵件分類（委派 classifier.IntentClassifier）")
            ap.add_argument("--input", required=True)
            ap.add_argument("--output", required=True)
            args = ap.parse_args()
            data = json.loads(open(args.input, encoding="utf-8").read())
            res = classify_intent((data.get("subject") or "").strip(), (data.get("content") or "").strip())
            data.update({"label": res["label"], "confidence": res["confidence"]})
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            open(args.output, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2))
            print("[Output] 分類完成：", args.output)

        if __name__ == "__main__":
            main()
    """
    ).lstrip(),
    "src/stats_collector.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：src/stats_collector.py
        # 模組用途：分類統計收集（對齊測試字串）

        import sqlite3
        import argparse
        from pathlib import Path
        from utils.logger import logger

        DB_PATH = Path("data/stats.db")

        def init_stats_db(db_path: Path = DB_PATH) -> None:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute(\"\"\"
                    CREATE TABLE IF NOT EXISTS stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        label TEXT,
                        elapsed REAL,
                        created_at TEXT DEFAULT (datetime('now'))
                    )
                \"\"\")
                conn.commit()
            print("資料庫初始化完成")
            logger.info("[stats_collector] stats.db 初始化完成：%s", db_path)

        def increment_counter(label: str, elapsed: float, db_path: Path = DB_PATH) -> None:
            if not label:
                raise ValueError("label 不可為空")
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute("INSERT INTO stats (label, elapsed) VALUES (?, ?)", (label, float(elapsed)))
                conn.commit()
            print("已新增統計紀錄")
            logger.info("[stats_collector] 新增統計：%s, elapsed=%.3f", label, elapsed)

        def _cli():
            p = argparse.ArgumentParser(description="分類統計收集工具")
            p.add_argument("--init", action="store_true")
            p.add_argument("--label", type=str)
            p.add_argument("--elapsed", type=float)
            args = p.parse_args()
            if args.init:
                init_stats_db(); return
            if args.label is not None and args.elapsed is not None:
                increment_counter(args.label, args.elapsed); return
            p.print_help()

        if __name__ == "__main__":
            _cli()
    """
    ).lstrip(),
    "init_db.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：init_db.py
        # 模組用途：建立 emails_log / users+diff_log / processed_mails / support_tickets 四個資料庫

        import os  # noqa: F401
        import sqlite3
        from pathlib import Path

        def _ensure_dir(p: str) -> None:
            Path(os.path.dirname(p) or ".").mkdir(parents=True, exist_ok=True)

        def init_emails_log_db(db_path: str = "data/emails_log.db") -> None:
            _ensure_dir(db_path)
            with sqlite3.connect(db_path) as conn:
                conn.execute(\"\"\"
                    CREATE TABLE IF NOT EXISTS emails_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        subject TEXT,
                        content TEXT,
                        summary TEXT,
                        predicted_label TEXT,
                        confidence REAL,
                        action TEXT,
                        error TEXT,
                        created_at TEXT
                    )
                \"\"\")
                conn.commit()

        def init_users_db(db_path: str = "data/users.db") -> None:
            _ensure_dir(db_path)
            with sqlite3.connect(db_path) as conn:
                conn.execute("DROP TABLE IF EXISTS users")
                conn.execute(\"\"\"
                    CREATE TABLE users (
                        email TEXT PRIMARY KEY,
                        name TEXT,
                        phone TEXT,
                        address TEXT
                    )
                \"\"\")
                conn.execute(\"\"\"
                    CREATE TABLE IF NOT EXISTS diff_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT,
                        欄位 TEXT,
                        原值 TEXT,
                        新值 TEXT,
                        created_at TEXT
                    )
                \"\"\")
                conn.commit()

        def init_processed_mails_db(db_path: str = "data/db/processed_mails.db") -> None:
            _ensure_dir(db_path)
            with sqlite3.connect(db_path) as conn:
                conn.execute(\"\"\"
                    CREATE TABLE IF NOT EXISTS processed_mails (
                        uid TEXT PRIMARY KEY,
                        subject TEXT,
                        sender TEXT
                    )
                \"\"\")
                conn.commit()

        def init_tickets_db(db_path: str = "data/tickets.db") -> None:
            _ensure_dir(db_path)
            with sqlite3.connect(db_path) as conn:
                conn.execute(\"\"\"
                    CREATE TABLE IF NOT EXISTS support_tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        subject TEXT,
                        content TEXT,
                        summary TEXT,
                        sender TEXT,
                        category TEXT,
                        confidence REAL,
                        created_at TEXT,
                        updated_at TEXT,
                        status TEXT,
                        priority TEXT
                    )
                \"\"\")
                conn.commit()

        if __name__ == "__main__":
            init_emails_log_db()
            init_users_db()
            init_processed_mails_db()
            init_tickets_db()
            print("OK: 初始化完成")
    """
    ).lstrip(),
    # -------------------- 相容層（讓舊測試可 import） --------------------
    "modules/__init__.py": "#!/usr/bin/env python3\n# 檔案位置：modules/__init__.py\n# 模組用途：相容層封裝\n",
    "modules/quotation.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：modules/quotation.py
        # 模組用途：相容層，轉發至實作

        try:
            from quotation import choose_package, generate_pdf_quote
        except Exception:  # pragma: no cover
            from src.quotation import choose_package, generate_pdf_quote
    """
    ).lstrip(),
    "modules/quote_logger.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：modules/quote_logger.py
        # 模組用途：相容層，轉發至實作

        try:
            from quote_logger import ensure_db_exists, log_quote
        except Exception:  # pragma: no cover
            from src.quote_logger import ensure_db_exists, log_quote
    """
    ).lstrip(),
    "modules/sales_notifier.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：modules/sales_notifier.py
        # 模組用途：相容層，轉發至實作

        try:
            from sales_notifier import notify_sales
        except Exception:  # pragma: no cover
            from src.sales_notifier import notify_sales
    """
    ).lstrip(),
    "modules/apply_diff.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：modules/apply_diff.py
        # 模組用途：相容層，轉發至實作

        try:
            from apply_diff import update_user_info
        except Exception:  # pragma: no cover
            from src.apply_diff import update_user_info
    """
    ).lstrip(),
    "spam/__init__.py": "#!/usr/bin/env python3\n# 檔案位置：spam/__init__.py\n# 模組用途：相容層封裝\n",
    "spam/spam_filter_orchestrator.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：spam/spam_filter_orchestrator.py
        # 模組用途：相容層，轉發至 src.spam

        from importlib import import_module as _imp
        _SF = _imp("src.spam.spam_filter_orchestrator")
        SpamFilterOrchestrator = _SF.SpamFilterOrchestrator
    """
    ).lstrip(),
    # -------------------- tools/ 輔助 --------------------
    "tools/__init__.py": "",
    "tools/repo_tidy.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：tools/repo_tidy.py
        # 模組用途：補 shebang/檔頭、簡易檢查 emails_log 表名

        import argparse, re
        from pathlib import Path

        ROOT = Path(__file__).resolve().parents[1]
        TARGET_DIRS = ["src", "utils", "scripts", "modules", "spam"]
        HEADER_RE = re.compile(r"^#!/usr/bin/env python3\\n# 檔案位置：.*\\n# 模組用途：.*", re.M)

        def list_py():
            files=[]
            for d in TARGET_DIRS:
                p=ROOT/d
                if p.exists():
                    files+=list(p.rglob("*.py"))
            return files

        def ensure_header(p: Path, dry: bool=False):
            rel = p.relative_to(ROOT).as_posix()
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if HEADER_RE.search(txt): return False
            header=f"#!/usr/bin/env python3\\n# 檔案位置：{rel}\\n# 模組用途：請補充此模組用途說明\\n\\n"
            if not dry: p.write_text(header+txt, encoding="utf-8")
            return True

        def main():
            ap=argparse.ArgumentParser()
            ap.add_argument("--check", action="store_true")
            args=ap.parse_args()
            changed=0
            for p in list_py():
                changed+=1 if ensure_header(p, dry=args.check) else 0
            print(("[檢查]" if args.check else "[修正]")+f" 檔頭處理：{changed} 檔")

        if __name__=="__main__":
            main()
    """
    ).lstrip(),
    "tools/project_catalog.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：tools/project_catalog.py
        # 模組用途：掃描專案並產生 PROJECT_STATUS.md

        import re, sys
        from pathlib import Path
        from collections import defaultdict

        ROOT = Path(__file__).resolve().parents[1]
        OUT = ROOT / "PROJECT_STATUS.md"

        ENTRY = re.compile(r'if\\s+__name__\\s*==\\s*[\\'"]__main__[\\'"]')
        ARG = re.compile(r"argparse\\.ArgumentParser")
        DDL = re.compile(r"CREATE TABLE IF NOT EXISTS\\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.I)

        def list_py():
            return [p for p in ROOT.rglob("*.py") if ".venv" not in str(p)]

        def main():
            files = list_py()
            entries=[str(p.relative_to(ROOT)) for p in files if ENTRY.search(p.read_text(encoding="utf-8", errors="ignore"))]
            clis=[str(p.relative_to(ROOT)) for p in files if ARG.search(p.read_text(encoding="utf-8", errors="ignore"))]
            tables=defaultdict(set)
            for p in files:
                for m in DDL.finditer(p.read_text(encoding="utf-8", errors="ignore")):
                    tables[m.group(1)].add(str(p.relative_to(ROOT)))
            md=[]
            md.append("# PROJECT STATUS\\n")
            md.append("## Entries\\n"); md+= [f"- {e}" for e in sorted(entries)]
            md.append("\\n## CLI-capable modules\\n"); md+= [f"- {e}" for e in sorted(clis)]
            md.append("\\n## Detected DB tables\\n")
            for t, locs in sorted({k:sorted(v) for k,v in tables.items()}.items()):
                md.append(f"- **{t}**: {', '.join(locs)}")
            OUT.write_text("\\n".join(md)+"\\n", encoding="utf-8")
            print(f"Wrote {OUT}")

        if __name__=="__main__":
            sys.exit(main())
    """
    ).lstrip(),
    # -------------------- scripts/ 工具 --------------------
    "scripts/__init__.py": "",
    "scripts/check_email_log.py": dedent(
        """
        #!/usr/bin/env python3
        # 檔案位置：scripts/check_email_log.py
        # 模組用途：檢查 emails_log.db 最新紀錄與統計

        import sqlite3
        from tabulate import tabulate
        from pathlib import Path

        DB_PATH = "data/emails_log.db"
        TABLE = "emails_log"

        def fetch_latest(limit=20):
            if not Path(DB_PATH).exists():
                print(f"[錯誤] 找不到 DB：{DB_PATH}"); return []
            try:
                conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
                cur.execute(f"SELECT id, subject, predicted_label, action, error, created_at FROM {TABLE} ORDER BY id DESC LIMIT ?", (limit,))
                rows = cur.fetchall(); conn.close(); return rows
            except Exception as e:
                print("[錯誤] 查詢失敗：", e); return []

        def show_stats():
            if not Path(DB_PATH).exists(): print("[錯誤] DB 不存在"); return
            try:
                conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
                cur.execute(f"SELECT COUNT(*) FROM {TABLE}"); total = cur.fetchone()[0]
                cur.execute(f"SELECT COUNT(*) FROM {TABLE} WHERE LOWER(predicted_label)='spam'"); spam = cur.fetchone()[0]
                cur.execute(f"SELECT COUNT(*) FROM {TABLE} WHERE error IS NOT NULL AND error!=''"); errors = cur.fetchone()[0]
                print("信件處理統計報告"); print(f"- 總筆數：{total}"); print(f"- 被過濾為 Spam：{spam}"); print(f"- 發生錯誤：{errors}")
                conn.close()
            except Exception as e:
                print("[錯誤] 統計失敗：", e)

        def main():
            rows = fetch_latest()
            if not rows:
                print("目前沒有資料，請先跑主流程或寫入測試資料。"); return
            print(tabulate(rows, headers=["ID","Subject","Label","Action","Error","Created At"], tablefmt="grid"))
            print(); show_stats()

        if __name__ == "__main__":
            main()
    """
    ).lstrip(),
}


def write_file(path: Path, content: str, force: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        print(f"[skip] {path} 已存在（未覆蓋）")
        return
    path.write_text(content, encoding="utf-8")
    print(f"[ok]   寫入 {path}")


def main():
    ap = argparse.ArgumentParser(description="一鍵建立/更新 Smart-Mail-Agent 專案檔案")
    ap.add_argument("--force", action="store_true", help="強制覆蓋已存在檔案")
    args = ap.parse_args()

    for rel, content in FILES.items():
        write_file(ROOT / rel, content, force=args.force)

    # 放置 keep 檔以便版控資料夾
    for d in ["data", "logs", "assets/fonts", "src/spam", "src/utils", "tests"]:
        p = ROOT / d
        p.mkdir(parents=True, exist_ok=True)
        keep = p / ".keep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")

    print("\\n完成。下一步建議：")
    print("1) python -m venv .venv && . .venv/bin/activate")
    print("2) pip install -U pip -r requirements.txt")
    print("3) cp .env.example .env  # 填入 SMTP 等")
    print("4) python init_db.py")
    print("5) make all")
    print("6) PYTHONPATH=src python scripts/check_email_log.py")


if __name__ == "__main__":
    main()
