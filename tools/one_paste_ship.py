#!/usr/bin/env python3
# tools/one_paste_ship.py
import fnmatch
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
VENV = ROOT / ".venv"
BIN = VENV / ("Scripts" if os.name == "nt" else "bin")
PY = str(BIN / "python") if (BIN / "python").exists() else sys.executable
PIP = str(BIN / "pip") if (BIN / "pip").exists() else sys.executable + " -m pip"

EXCLUDE_DIRS = [
    ".git/",
    ".venv/",
    "__pycache__/",
    ".pytest_cache/",
    "logs/",
    "htmlcov/",
    "diagnostics/",
    "backup_dedup_",
    "modules_legacy_backup_",
    ".github/",
]
EXCLUDE_GLOBS = [
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.svg",
    "*.ico",
    "*.ttf",
    "*.otf",
    "*.woff",
    "*.woff2",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.tgz",
    "*.mp4",
    "*.mov",
    "*.pdf",
    "sma-codeonly.tar.gz",
]
DEFAULT_BRANCH = os.getenv("TARGET_BRANCH", "main")
PASTE_FILE = ROOT / "ALL_CODE_FOR_PASTE.txt"


def run(cmd, check=True, env=None, cwd=None, quiet=False):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    p = subprocess.run(
        cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    if not quiet:
        sys.stdout.write(p.stdout)
    if check and p.returncode != 0:
        raise SystemExit(p.stdout or p.returncode)
    return p


def ensure_venv_and_tools():
    if not VENV.exists():
        print("==> creating venv")
        run([sys.executable, "-m", "venv", str(VENV)])
    print("==> upgrading pip")
    run(shlex.split(f"{PIP} -q install -U pip"))
    # 專案必備 + 開發工具
    print("==> installing project reqs")
    req = ROOT / "requirements.txt"
    if req.exists():
        run(shlex.split(f"{PIP} -q install -r {req}"), check=False)
    print("==> installing dev tools")
    run(shlex.split(f"{PIP} -q install -U pytest black isort flake8 python-dotenv"))


def format_and_lint():
    print("==> isort / black / flake8")
    run([PY, "-m", "isort", "."])
    run([PY, "-m", "black", "."])
    run([PY, "-m", "flake8"])


def run_offline_tests():
    print("==> pytest -k 'not online'")
    env = os.environ.copy()
    env["OFFLINE"] = "1"
    run([PY, "-m", "pytest", "-q", "-k", "not online"], env=env)


def git_ls_files():
    try:
        out = run(["git", "ls-files", "-z"], quiet=True).stdout
        files = [Path(p) for p in out.split("\x00") if p]
    except Exception:
        files = [p for p in ROOT.rglob("*") if p.is_file()]
    return files


def is_excluded(path: Path) -> bool:
    rel = path.as_posix()
    for d in EXCLUDE_DIRS:
        if f"{d}" in rel:
            return True
    for g in EXCLUDE_GLOBS:
        if fnmatch.fnmatch(rel, g):
            return True
    return False


def is_text_file(path: Path) -> bool:
    try:
        b = path.read_bytes()
    except Exception:
        return False
    if b"\x00" in b[:4096]:
        return False
    try:
        b.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def ensure_readme_and_ignore():
    gi = ROOT / ".gitignore"
    gi.touch(exist_ok=True)
    needed = [
        ".venv/",
        "logs/",
        "__pycache__/",
        ".pytest_cache/",
        "htmlcov/",
        ".coverage*",
        "data/output/",
        "sma-codeonly.tar.gz",
        "backup_dedup_*/",
        "modules_legacy_backup_*/",
        "assets/fonts/*.ttf",
    ]
    cur = gi.read_text(encoding="utf-8").splitlines()
    changed = False
    for p in needed:
        if p not in cur:
            cur.append(p)
            changed = True
    if changed:
        gi.write_text("\n".join(cur) + "\n", encoding="utf-8")
        print("updated .gitignore")

    readme = ROOT / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Smart Mail Agent\n\n"
            "Quickstart:\n"
            "```bash\n"
            "python -m venv .venv && . .venv/bin/activate\n"
            "pip install -U pip && pip install -r requirements.txt\n"
            'OFFLINE=1 PYTHONPATH=src pytest -q -k "not online"\n'
            "```\n",
            encoding="utf-8",
        )
        print("created README.md")


def export_all_code(paste_path: Path = PASTE_FILE):
    print(f"==> building {paste_path.name}")
    files = []
    for f in git_ls_files():
        if not f.is_file():
            continue
        if is_excluded(f):
            continue
        if not is_text_file(f):
            continue
        try:
            if f.stat().st_size > 800 * 1024:
                continue
        except Exception:
            pass
        files.append(f)

    files.sort(key=lambda p: p.as_posix())
    with open(paste_path, "w", encoding="utf-8", newline="\n") as out:
        out.write(f"# ALL_CODE_FOR_PASTE\n# generated: {datetime.utcnow().isoformat()}Z\n")
        out.write("# format: ===FILE: <relative path>\n")
        for f in files:
            rel = f.as_posix()
            out.write(f"\n===FILE: {rel}\n")
            out.write(f.read_text(encoding="utf-8"))
            out.write("\n===END===\n")
    print(f"wrote {paste_path}")


def import_from_paste(paste_path: Path):
    print(f"==> importing from {paste_path}")
    if not paste_path.exists():
        raise SystemExit(f"{paste_path} not found")
    txt = paste_path.read_text(encoding="utf-8")
    blocks = txt.split("\n===FILE: ")
    created = 0
    for blk in blocks[1:]:
        header, _, body = blk.partition("\n")
        rel = header.strip()
        content, _, _end = body.partition("\n===END===\n")
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        created += 1
    print(f"restored {created} files")


def git_commit_push(
    message: str = "chore: interview-ready snapshot (offline green, formatted, export bundle)",
):
    print("==> git add/commit/push")
    run(["git", "fetch", "origin"])
    cur = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], quiet=True).stdout.strip()
    if cur != DEFAULT_BRANCH:
        run(["git", "checkout", DEFAULT_BRANCH])
    run(["git", "pull", "--ff-only"])
    run(["git", "add", "-A"])
    st = run(["git", "diff", "--cached", "--name-only"], quiet=True).stdout.strip()
    if not st:
        print("no staged changes; skip commit")
    else:
        run(["git", "commit", "-m", message])
    run(["git", "push", "-u", "origin", DEFAULT_BRANCH])


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="One-paste ship: format > lint > offline test > export > (optional) push"
    )
    ap.add_argument("--no-venv", action="store_true", help="不要建立/升級 venv（用現有環境）")
    ap.add_argument("--format", action="store_true", help="只做 isort/black/flake8")
    ap.add_argument("--test", action="store_true", help="只跑離線測試")
    ap.add_argument("--export", action="store_true", help="輸出 ALL_CODE_FOR_PASTE.txt")
    ap.add_argument("--import", dest="import_file", help="從 ALL_CODE_FOR_PASTE.txt 還原專案")
    ap.add_argument("--push", action="store_true", help="完成後 git push 到 main")
    ap.add_argument(
        "--message",
        default="chore: interview-ready snapshot (offline green, formatted, export bundle)",
    )
    args = ap.parse_args()

    if not args.no_venv:
        ensure_venv_and_tools()

    if args.import_file:
        import_from_paste(Path(args.import_file))
        return

    ensure_readme_and_ignore()
    format_and_lint()
    run_offline_tests()
    export_all_code(PASTE_FILE)
    if args.push:
        git_commit_push(args.message)


if __name__ == "__main__":
    main()
