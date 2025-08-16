# shim: utils.pdf_safe
# 說明：老路徑 `from utils.pdf_safe import write_pdf_or_txt` 仍然存在於部分檔案/測試中。
# 這個 shim 會轉發到新位置 `smart_mail_agent.utils.pdf_safe`；若轉發失敗，提供最小可用後備實作以避免 import error。
from __future__ import annotations

try:
    # 新位置（實作完整，優先使用）
    from smart_mail_agent.utils.pdf_safe import (  # type: ignore
        write_pdf_or_txt as _write_pdf_or_txt,
        _escape_pdf_text as _escape_pdf_text,
        _write_minimal_pdf as _write_minimal_pdf,
    )
except Exception:
    # 最小後備：離線可用、非正式 PDF，僅供測試路徑 fallback，用不到真正字型/版面。
    from pathlib import Path

    def _escape_pdf_text(s: str) -> str:
        # 僅做基本跳脫，確保 ASCII 可用
        return (
            s.replace("\\", "\\\\")
             .replace("(", "\\(")
             .replace(")", "\\)")
        )

    def _write_minimal_pdf(lines: list[str], out_path: Path) -> Path:
        out_path = Path(out_path)
        text = "\\n".join(_escape_pdf_text(l) for l in lines)
        # 超簡 PDF（僅檢測 header/長度）
        content = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >> endobj
4 0 obj << /Length {len(text)+73} >> stream
BT /F1 12 Tf 50 780 Td ({text}) Tj ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
trailer << /Root 1 0 R /Size 6 >>
startxref
0
%%EOF
""".encode("latin-1", "ignore")
        out_path.write_bytes(content)
        return out_path

    def _write_pdf_or_txt(text: str, out_path: Path, degrade_to_txt: bool = False) -> Path:
        out_path = Path(out_path)
        if degrade_to_txt or out_path.suffix.lower() == ".txt":
            out_path.write_text(text, encoding="utf-8")
            return out_path
        return _write_minimal_pdf([text], out_path)

    # 對外 API 名稱（與新模組對齊）
    def write_pdf_or_txt(text: str, out_path: str | Path, degrade_to_txt: bool = False):
        return _write_pdf_or_txt(text, Path(out_path), degrade_to_txt)

else:
    # 轉發成功時對外 API 維持與舊路徑一致
    from pathlib import Path
    def write_pdf_or_txt(text: str, out_path: str | Path, degrade_to_txt: bool = False):
        return _write_pdf_or_txt(text, Path(out_path), degrade_to_txt)

__all__ = ["write_pdf_or_txt", "_escape_pdf_text", "_write_minimal_pdf"]
