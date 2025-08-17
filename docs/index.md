# Smart Mail Agent / Docs

這是簡化版文件讓 GitHub Pages 可以發布。

## 快速開始
1. python3 -m venv .venv
2. . .venv/bin/activate
3. pip install -U pip && pip install -e .
4. cp -n .env.example .env

## 常用指令
- python -m smart_mail_agent.cli_spamcheck --subject "免費中獎" --body "恭喜獲得獎金"
- OFFLINE=1 python -m smart_mail_agent.routing.run_action_handler --input data/sample/email.json
