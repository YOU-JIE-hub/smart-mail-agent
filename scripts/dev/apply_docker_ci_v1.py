#!/usr/bin/env python3
# 檔案位置：tools/apply_docker_ci_v1.py
# 模組用途：一鍵建立/更新 Dockerfile、.dockerignore、docker-compose.yml、docker entrypoint、Docker CI workflow

import argparse
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, content: str, force: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        print(f"[skip] {path} 已存在（未覆蓋）")
        return
    path.write_text(content, encoding="utf-8")
    print(f"[ok]   寫入 {path}")


def main():
    ap = argparse.ArgumentParser(description="Apply Docker & Compose & Docker CI files")
    ap.add_argument("--force", action="store_true", help="強制覆蓋既有檔案")
    args = ap.parse_args()

    files = {
        # ---- Dockerfile ----
        ROOT / "Dockerfile": dedent(
            """
            # syntax=docker/dockerfile:1.6
            # 檔案位置：Dockerfile
            # 模組用途：Smart-Mail-Agent 容器建置（python:3.11-slim、非 root、Noto CJK 字型）

            FROM python:3.11-slim AS base

            # 系統依賴與字型（FPDF 中文）
            RUN apt-get update && apt-get install -y --no-install-recommends \\
                gosu tini locales fonts-noto-cjk \\
                && rm -rf /var/lib/apt/lists/*

            # 設定 UTF-8
            RUN sed -i '/zh_TW.UTF-8/s/^# //g' /etc/locale.gen && \\
                sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \\
                locale-gen
            ENV LANG=zh_TW.UTF-8 LC_ALL=zh_TW.UTF-8

            # 非 root 使用者
            ARG APP_USER=app
            RUN useradd -ms /bin/bash ${APP_USER}

            WORKDIR /app
            COPY requirements.txt /app/requirements.txt
            RUN pip install -U pip && pip install -r /app/requirements.txt

            # 複製專案
            COPY . /app

            # 預設環境
            ENV PYTHONUNBUFFERED=1 \\
                PYTHONPATH=src

            # 建立資料目錄與字型連結（若沒給 QUOTE_FONT_PATH，FPDF 仍可用 Noto CJK）
            RUN mkdir -p /app/data /app/logs /app/assets/fonts && \\
                ln -sf /usr/share/fonts/opentype/noto /app/assets/fonts/system-noto

            # 權限
            RUN chown -R ${APP_USER}:${APP_USER} /app
            USER ${APP_USER}

            # entrypoint：先初始化 DB，再跑 pipeline（若存在），否則跑 scripts/run_all.py
            RUN chmod +x docker/entrypoint.sh || true

            ENTRYPOINT ["/usr/bin/tini","--"]
            CMD ["bash","-lc","docker/entrypoint.sh"]
        """
        ).lstrip(),
        # ---- docker/entrypoint.sh ----
        ROOT / "docker" / "entrypoint.sh": dedent(
            """
            #!/usr/bin/env bash
            # 檔案位置：docker/entrypoint.sh
            # 模組用途：容器啟動：初始化 DB → 執行主流程或 run_all

            set -e

            echo "[entrypoint] 初始化資料庫…"
            python init_db.py || true

            if [ -f "pipeline/main.py" ]; then
              echo "[entrypoint] 執行 pipeline/main.py"
              exec python pipeline/main.py --limit "${LIMIT:-50}" --force
            elif [ -f "scripts/run_all.py" ]; then
              echo "[entrypoint] 執行 scripts/run_all.py"
              exec python scripts/run_all.py
            else
              echo "[entrypoint] 找不到 pipeline/main.py 或 scripts/run_all.py，進入睡眠以便除錯"
              exec tail -f /dev/null
            fi
        """
        ).lstrip(),
        # ---- .dockerignore ----
        ROOT / ".dockerignore": dedent(
            """
            # 檔案位置：.dockerignore
            # 模組用途：避免把不必要檔案打包進 Docker context

            .git
            .venv
            __pycache__
            .pytest_cache
            .mypy_cache
            .DS_Store
            *.db
            data/
            logs/
            .env
            .coverage
            dist/
            build/
            .gitignore
            README.md
        """
        ).lstrip(),
        # ---- docker-compose.yml ----
        ROOT / "docker-compose.yml": dedent(
            """
            # 檔案位置：docker-compose.yml
            # 模組用途：本地或伺服器一鍵啟動 Smart-Mail-Agent

            services:
              smart-mail-agent:
                build: .
                image: smart-mail-agent:local
                env_file:
                  - .env
                environment:
                  - PYTHONPATH=src
                  # LIMIT 可覆蓋 entrypoint 的抓信數量
                  - LIMIT=50
                volumes:
                  - ./data:/app/data
                  - ./logs:/app/logs
                # 若你沒有 pipeline/main.py，可改成跑 scripts/run_all.py
                command: []
        """
        ).lstrip(),
        # ---- GitHub Actions：Docker build（驗證能建置） ----
        ROOT / ".github" / "workflows" / "docker.yml": dedent(
            """
            # 檔案位置：.github/workflows/docker.yml
            # 模組用途：在 PR 與 main push 驗證 Docker 能成功 build

            name: Docker Build

            on:
              push:
                branches: [ main, master ]
              pull_request:
                branches: [ main, master ]

            jobs:
              docker-build:
                runs-on: ubuntu-latest
                steps:
                  - name: Checkout
                    uses: actions/checkout@v4

                  - name: Set up QEMU
                    uses: docker/setup-qemu-action@v3

                  - name: Set up Docker Buildx
                    uses: docker/setup-buildx-action@v3

                  - name: Build (no push)
                    uses: docker/build-push-action@v6
                    with:
                      context: .
                      file: ./Dockerfile
                      push: false
                      platforms: linux/amd64
        """
        ).lstrip(),
    }

    for p, content in files.items():
        write(p, content, args.force)

    print("\\n[提醒] 設定 docker/entrypoint.sh 執行權限：")
    print("chmod +x docker/entrypoint.sh")


if __name__ == "__main__":
    main()
