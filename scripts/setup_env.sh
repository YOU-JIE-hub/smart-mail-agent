#!/usr/bin/env bash
set -Eeuo pipefail
python -m venv .venv
. .venv/bin/activate
pip install -U pip
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f requirements-dev.txt ] && pip install -r requirements-dev.txt
