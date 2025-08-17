    0 * * * * cd $HOME/projects/smart-mail-agent && . .venv/bin/activate && OFFLINE=1 PYTHONPATH=src python -m src.run_action_handler --tasks classify >> logs/cron.log 2>&1
