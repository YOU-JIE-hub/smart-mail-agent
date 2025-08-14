import importlib
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]  # 專案根目錄
SRC_DIR = ROOT / "src"


def _exists(p):
    return pathlib.Path(p).exists()


def _nonempty(p):
    return _exists(p) and pathlib.Path(p).stat().st_size > 0


def test_generate_quote_pdf(tmp_path):
    """
    符合你目前的簽名：
      generate_pdf_quote(out_dir: Optional[path|str]=None, *, package: Optional[str]=None, client_name: Optional[str]=None) -> str
    reportlab 缺/字型缺時，允許 .txt 保底。
    """
    os.environ["OFFLINE"] = "1"
    # 確保能 import src.*
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    mod = importlib.import_module(
        "modules.quotation" if (SRC_DIR / "modules" / "quotation.py").exists() else "src.modules.quotation"
    )
    fn = getattr(mod, "generate_pdf_quote", None)
    assert fn, "generate_pdf_quote missing"

    # 優先使用具名參數（符合你簽名），若舊行為只吃 out_dir 也能兼容
    try:
        rv = fn(out_dir=str(tmp_path), package="基礎", client_name="test@example.com")
    except TypeError:
        rv = fn(str(tmp_path))

    out_path = pathlib.Path(rv) if isinstance(rv, (str, pathlib.Path)) else tmp_path / "quote.pdf"
    assert _nonempty(out_path), f"no output generated at {out_path}"
    assert out_path.suffix in {".pdf", ".txt"}, f"unexpected suffix: {out_path.suffix}"


def test_cli_smoke(tmp_path):
    """
    以 CLI 跑一趟 action handler（離線，不碰 API 金鑰）。
    run_action_handler 內部用 'python -m action_handler'，
    我們設定 PYTHONPATH=src，讓子程序找得到 action_handler。
    """
    env = os.environ.copy()
    env["OFFLINE"] = "1"
    # 讓子進程（python -m action_handler）找得到 src/*
    env["PYTHONPATH"] = str(SRC_DIR)

    in_json = tmp_path / "in.json"
    out_json = tmp_path / "out.json"

    # 提供最小可用 payload（action_handler 會自行決定動作）
    payload = {
        "subject": "請提供報價",
        "from": "alice@example.com",
        "body": "需要 quotation，請回覆細節與檔案",
    }
    in_json.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    # 用目前測試環境的 python 啟動 CLI（確保使用到 venv）
    cmd = [
        sys.executable,
        "-m",
        "src.run_action_handler",
        "--input",
        str(in_json),
        "--output",
        str(out_json),
    ]
    # 若你的包是以頂層 import（action_handler.py 在 src/），上面已設 PYTHONPATH，子程序會接手。
    subprocess.check_call(cmd, env=env)

    assert _nonempty(out_json), "CLI did not produce output JSON"
    # 能 parse 即可（內容格式依 action_handler 輸出，這裡不綁特定 schema）
    json.loads(out_json.read_text(encoding="utf-8"))
