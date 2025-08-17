#!/usr/bin/env python3
# 檔案位置: tools/build_text_pack.py
# 模組用途: 將整個專案的純文字原始碼打包為多個 .txt 檔（帶行號與檔案邊界），並標記疑似舊版/重複檔
#
# 特色:
# 1) 穩定順序：以不分大小寫排序的相對路徑輸出，便於對齊審閱。
# 2) 安全過濾：只納入常見文字檔，排除 .venv、__pycache__、build、data 等大型或二進位目錄。
# 3) 標記輔助：依路徑與內容特徵標記 legacy_candidate、sys_path_hack、duplicate_basename。
# 4) 自動分片：預設每片最多 40 個檔、上限約 300KB。可用參數調整，避免一次貼文過長。
#
# 使用:
#   cd ~/projects/smart-mail-agent
#   python tools/build_text_pack.py
# 產物:
#   review_pack/
#     index.tsv                 檔案清單與標記摘要
#     pack_0001.txt             第 1 片文本包
#     pack_0002.txt             第 2 片文本包
#     ...
#
# 自訂參數:
#   python tools/build_text_pack.py --files-per-part 50 --max-bytes-per-part 400000
#   python tools/build_text_pack.py --single-file   # 產出單一 pack_all.txt（檔大時不建議）
#
# 後續流程:
#   將 pack_0001.txt 內容完整貼到聊天中，我會逐行審閱並回「一鍵覆蓋修正」腳本。
#   然後再貼 pack_0002.txt，以此類推，直到看完全部。

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

# 允許的文字檔類型與特定檔名
ALLOWED_EXTS = {
    ".py",
    ".pyi",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
    ".txt",
    ".cfg",
    ".ini",
    ".json",
    ".sh",
    ".bash",
    ".ps1",
    ".sql",
    ".rst",
}
ALLOWED_BASENAMES = {
    "Dockerfile",
    "Makefile",
    ".gitignore",
    ".env.example",
    "requirements.txt",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
}

# 排除的目錄（整個樹狀任何層級命中即排除）
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "build",
    "dist",
    "share",
    "outputs",
    "output",
    "out",
    "data",
    "assets",
    ".idea",
    ".vscode",
    "logs",
}

# 判定 legacy 的路徑關鍵字（命中任一即標記為 legacy_candidate）
LEGACY_DIR_HINTS = {".archive", "archive", "legacy", "deprecated", "old", "tmp", "draft", "sandbox"}

# 偵測舊式 sys.path 手動注入的特徵（遇到這些字樣標記 sys_path_hack）
SYS_PATH_PATTERNS = (
    r"sys\.path\.insert\(",
    r"os\.path\.dirname\(__file__\)",
    r"SRC_PATH\s*=",
    r"sys\.path\.append\(",
)

BANNER = "=" * 80


def project_root() -> Path:
    # 優先以常見位置或向上尋找 src/run_action_handler.py 判斷專案根
    candidates = [
        (
            Path(os.environ.get("PROJECT_DIR", "")).resolve()
            if os.environ.get("PROJECT_DIR")
            else None
        ),
        Path.home() / "projects" / "smart-mail-agent",
        Path.home() / "smart-mail-agent",
        Path.cwd(),
    ]
    for p in candidates:
        if not p:
            continue
        if (p / "src" / "run_action_handler.py").exists():
            return p.resolve()

    cur = Path.cwd().resolve()
    for _ in range(6):
        if (cur / "src" / "run_action_handler.py").exists():
            return cur
        cur = cur.parent
    return Path.cwd().resolve()


def is_text_file(path: Path) -> bool:
    if path.name in ALLOWED_BASENAMES:
        return True
    return path.suffix.lower() in ALLOWED_EXTS


def in_excluded_dir(path: Path) -> bool:
    parts = set(path.parts)
    return any(d in parts for d in EXCLUDE_DIRS)


def iter_files(root: Path) -> Iterable[Path]:
    # 優先以 git 列出檔案，若失敗則走 os.walk
    git = root / ".git"
    files: List[Path] = []
    if git.exists():
        try:
            import subprocess

            cp = subprocess.run(
                ["git", "ls-files"], cwd=str(root), text=True, capture_output=True, check=False
            )
            for line in cp.stdout.splitlines():
                if not line.strip():
                    continue
                p = (root / line.strip()).resolve()
                if p.is_file() and is_text_file(p) and not in_excluded_dir(p):
                    files.append(p)
        except Exception:
            files = []
    if not files:
        for cur, dirnames, filenames in os.walk(root):
            cpath = Path(cur)
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for f in filenames:
                p = cpath / f
                if p.is_file() and is_text_file(p) and not in_excluded_dir(p):
                    files.append(p)
    files = [p for p in files if p.exists()]
    files.sort(key=lambda x: str(x.relative_to(root)).lower())
    return files


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"[讀取失敗] {e}"


def detect_sys_path_hack(text: str) -> bool:
    for pat in SYS_PATH_PATTERNS:
        if re.search(pat, text):
            return True
    return False


def detect_legacy_by_path(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    for hint in LEGACY_DIR_HINTS:
        if any(hint == seg or hint in seg for seg in parts):
            return True
    return False


def group_by_basename(paths: List[Path], root: Path) -> Dict[str, List[Path]]:
    m: Dict[str, List[Path]] = {}
    for p in paths:
        bn = p.name.lower()
        m.setdefault(bn, []).append(p)
    return {k: v for k, v in m.items() if len(v) > 1}


def build_index(paths: List[Path], root: Path) -> List[Dict[str, str]]:
    dup = group_by_basename(paths, root)
    rows: List[Dict[str, str]] = []
    for p in paths:
        rel = str(p.relative_to(root)).replace("\\", "/")
        text = read_text(p)
        row = {
            "path": rel,
            "size": str(p.stat().st_size),
            "legacy_candidate": "yes" if detect_legacy_by_path(p) else "no",
            "sys_path_hack": "yes" if detect_sys_path_hack(text) else "no",
            "duplicate_basename": "yes" if p in dup.get(p.name.lower(), []) else "no",
        }
        rows.append(row)
    return rows


def write_index_tsv(index: List[Dict[str, str]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tsv = out_dir / "index.tsv"
    cols = ["path", "size", "legacy_candidate", "sys_path_hack", "duplicate_basename"]
    with tsv.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for row in index:
            f.write("\t".join(row[c] for c in cols) + "\n")


def format_one_file_block(root: Path, path: Path, text: str, tags: Dict[str, str]) -> str:
    rel = str(path.relative_to(root)).replace("\\", "/")
    size = path.stat().st_size
    tag_line = " | ".join(f"{k}={v}" for k, v in tags.items())
    lines = []
    lines.append(BANNER)
    lines.append(f"BEGIN FILE  {rel}  ({size} bytes)")
    if tag_line:
        lines.append(f"TAGS: {tag_line}")
    lines.append("-" * 80)
    for i, line in enumerate(text.splitlines(), 1):
        lines.append(f"{i:6d}: {line}")
    lines.append("-" * 80)
    lines.append(f"END FILE    {rel}")
    lines.append(BANNER)
    return "\n".join(lines) + "\n"


def write_packs(
    paths: List[Path],
    root: Path,
    out_dir: Path,
    files_per_part: int,
    max_bytes: int,
    single_file: bool,
) -> Tuple[int, List[Path]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    parts_written = 0
    outputs: List[Path] = []

    if single_file:
        out = out_dir / "pack_all.txt"
        with out.open("w", encoding="utf-8") as fh:
            for p in paths:
                text = read_text(p)
                tags = {
                    "legacy_candidate": "yes" if detect_legacy_by_path(p) else "no",
                    "sys_path_hack": "yes" if detect_sys_path_hack(text) else "no",
                    "duplicate_basename": "n/a",  # 單檔輸出時不特別標記
                }
                fh.write(format_one_file_block(root, p, text, tags))
        return 1, [out]

    # 多片輸出
    idx = 0
    while idx < len(paths):
        parts_written += 1
        out_path = out_dir / f"pack_{parts_written:04d}.txt"
        outputs.append(out_path)
        written_bytes = 0
        file_count = 0
        with out_path.open("w", encoding="utf-8") as fh:
            while idx < len(paths) and file_count < files_per_part:
                p = paths[idx]
                text = read_text(p)
                tags = {
                    "legacy_candidate": "yes" if detect_legacy_by_path(p) else "no",
                    "sys_path_hack": "yes" if detect_sys_path_hack(text) else "no",
                    "duplicate_basename": "no",  # 最終以 index.tsv 統一檢視
                }
                block = format_one_file_block(root, p, text, tags)
                # 若即將超出上限，結束當前分片
                if max_bytes > 0 and (written_bytes + len(block)) > max_bytes and file_count > 0:
                    break
                fh.write(block)
                written_bytes += len(block)
                file_count += 1
                idx += 1
    return parts_written, outputs


def main() -> None:
    ap = argparse.ArgumentParser(description="打包專案原始碼為多個文本檔，供離線逐行審閱")
    ap.add_argument("--root", help="專案根目錄（預設自動尋找）")
    ap.add_argument("--files-per-part", type=int, default=40, help="每個文本分片最多包含的檔案數")
    ap.add_argument(
        "--max-bytes-per-part",
        type=int,
        default=300000,
        help="每個文本分片最大字元數（0 表示不限制）",
    )
    ap.add_argument(
        "--single-file", action="store_true", help="輸出單一 pack_all.txt（檔案很大時不建議）"
    )
    args = ap.parse_args()

    root = Path(args.root).resolve() if args.root else project_root()
    out_dir = root / "review_pack"

    paths = list(iter_files(root))
    if not paths:
        print("未找到可打包的文字檔。")
        return

    index = build_index(paths, root)
    write_index_tsv(index, out_dir)

    parts, outs = write_packs(
        paths=paths,
        root=root,
        out_dir=out_dir,
        files_per_part=max(1, args.files_per_part),
        max_bytes=max(0, args.max_bytes_per_part),
        single_file=bool(args.single_file),
    )

    print(f"完成：共打包 {len(paths)} 個檔案。輸出分片數量: {parts}")
    for p in outs:
        print(f"- {p}")


if __name__ == "__main__":
    main()
