    0 * * * * cd $HOME/projects/smart-mail-agent && . .venv/bin/activate && OFFLINE=1 PYTHONPATH=src python -m src.run_action_handler --tasks classify >> logs/cron.log 2>&1

# Smart Mail Agent

一個可離線驗證的 AI + RPA 郵件處理範例專案。

快速連結：
- [Architecture](architecture.md)
- [Cookbook](cookbook.md)
[![tests](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml)
![coverage](https://raw.githubusercontent.com/YOU-JIE-hub/smart-mail-agent/main/?t=1755652144)



**離線展示：**
```bash
scripts/demo_offline.sh

![coverage](https://raw.githubusercontent.com/YOU-JIE-hub/smart-mail-agent/main/badges/coverage.svg?t=1755654111)
