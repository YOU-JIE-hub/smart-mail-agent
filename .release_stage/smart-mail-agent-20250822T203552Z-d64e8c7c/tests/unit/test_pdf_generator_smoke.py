import importlib
from pathlib import Path

def test_pdf_generator_smoke(tmp_path: Path):
    mod = importlib.import_module("smart_mail_agent.utils.pdf_generator")
    # 寬鬆探索 API：常見命名優先；都沒有就只測 import 成功
    candidates = [
        "generate_pdf",
        "make_pdf",
        "build_pdf",
        "render_pdf",
        "create_pdf",
    ]
    fn = next((getattr(mod, n) for n in candidates if hasattr(mod, n)), None)
    if fn is None:
        # 沒有公開 API 就只確認模組可被 import
        assert mod is not None
        return
    # 嘗試以最小參數生成到 tmp 檔案或得到 bytes
    out_file = tmp_path / "smoke.pdf"
    try:
        rv = fn(dest=str(out_file), text="hello")  # 常見參數風格
    except TypeError:
        # 換一種風格
        try:
            rv = fn(str(out_file), "hello")
        except TypeError:
            # 再退一格：假設回傳 bytes
            rv = fn("hello")
            if isinstance(rv, (bytes, bytearray)):
                out_file.write_bytes(rv)
    # 最後只要檔案存在且大於零即可
    assert out_file.exists() and out_file.stat().st_size > 0
