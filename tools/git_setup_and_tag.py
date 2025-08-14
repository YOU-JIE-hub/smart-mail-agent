#!/usr/bin/env python3
# 檔案：tools/git_setup_and_tag.py
# 用途：在目前 repo 內一鍵設定 git 用戶資訊、初始化 main 分支、建立首個提交、可選設定遠端並推送
#
# 以環境變數提供資訊（無交互）：
#   SMA_GIT_NAME   例如：export SMA_GIT_NAME="Your Name"
#   SMA_GIT_EMAIL  例如：export SMA_GIT_EMAIL="you@example.com"
#   SMA_GIT_REMOTE （可選）例如：export SMA_GIT_REMOTE="git@github.com:your/repo.git"
#   SMA_TAG        （可選）例如：export SMA_TAG="v0.1.0"
#
# 用法：
#   python tools/git_setup_and_tag.py

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def sh(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check)


def main() -> None:
    name = os.environ.get("SMA_GIT_NAME")
    email = os.environ.get("SMA_GIT_EMAIL")
    remote = os.environ.get("SMA_GIT_REMOTE")
    tag = os.environ.get("SMA_TAG")

    if not name or not email:
        print("[ERR] 請先設定環境變數 SMA_GIT_NAME / SMA_GIT_EMAIL 再執行。")
        print('      例：export SMA_GIT_NAME="Your Name"; export SMA_GIT_EMAIL="you@example.com"')
        raise SystemExit(2)

    # 1) 確保 git repo
    if not (Path(".git").exists()):
        sh(["git", "init"])

    # 2) 設定使用者
    sh(["git", "config", "user.name", name])
    sh(["git", "config", "user.email", email])

    # 3) 若沒有提交，建立 main 與首個提交
    # 檢查是否已有 commit
    has_commit = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    if not has_commit:
        # 設定預設分支為 main（僅空 repo 有效）
        try:
            sh(["git", "symbolic-ref", "HEAD", "refs/heads/main"])
        except subprocess.CalledProcessError:
            pass
        sh(["git", "add", "-A"])
        # 首次提交避免空提交
        sh(["git", "commit", "-m", "chore: initial commit [sma]"])

    # 4) 設定遠端（可選）
    if remote:
        # 如果已存在 origin 就 set-url；否則 add
        has_origin = (
            subprocess.run(
                ["git", "remote", "get-url", "origin"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )
        if has_origin:
            sh(["git", "remote", "set-url", "origin", remote])
        else:
            sh(["git", "remote", "add", "origin", remote])

        # 推 main
        # 先確認目前分支名
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
        cur = res.stdout.strip() or "main"
        try:
            sh(["git", "push", "-u", "origin", cur])
        except subprocess.CalledProcessError:
            print("[WARN] push 失敗，請檢查遠端權限或分支保護策略。")

    # 5) 打 tag（可選）
    if tag:
        # 若 tag 已存在，略過
        exists = (
            subprocess.run(
                ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )
        if not exists:
            sh(["git", "tag", tag])
            if remote:
                try:
                    sh(["git", "push", "origin", tag])
                except subprocess.CalledProcessError:
                    print("[WARN] 推送 tag 失敗，請檢查遠端權限。")
        else:
            print(f"[INFO] tag {tag} 已存在，略過。")

    print("[ok] git 設定與初始化完成。")


if __name__ == "__main__":
    main()
