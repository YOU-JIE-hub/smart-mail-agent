#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
export OFFLINE=0
export PYTHONPATH=src
while true; do
  python pipeline/main.py --limit 50 || true
  sleep 60
done
