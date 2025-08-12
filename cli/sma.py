from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(prog="sma", description="Smart Mail Agent CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="跑矩陣 + 產 HTML 報告 + 嘗試開啟")
    sub.add_parser("matrix", help="僅跑矩陣")
    sub.add_parser("verify", help="驗證 PDF 降級路徑")
    args = parser.parse_args()

    ROOT = Path(__file__).resolve().parents[1]
    SRC, TOOLS = ROOT / "src", ROOT / "tools"
    env = os.environ.copy()
    env.update({"OFFLINE": "1", "PYTHONPATH": str(SRC)})

    def run(cmd):
        import subprocess

        print("[RUN]", " ".join(cmd))
        return subprocess.run(cmd, cwd=str(ROOT), env=env, text=True).returncode

    if args.cmd == "verify":
        run([sys.executable, str(TOOLS / "verify_pdf_degrade.py")])
    elif args.cmd == "matrix":
        run([sys.executable, str(TOOLS / "run_actions_matrix.py")])
    elif args.cmd == "demo":
        run([sys.executable, str(TOOLS / "run_actions_matrix.py")])
        rep = TOOLS / "generate_offline_report.py"
        if rep.exists():
            run([sys.executable, str(rep)])
        # 嘗試自動開啟
        report = ROOT / "reports" / "offline_demo_report.html"
        for opener in ("wslview", "xdg-open"):
            from shutil import which

            if which(opener):
                import subprocess

                subprocess.Popen([opener, str(report)])
                break
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
