# Smart Mail Agent

Quickstart:
```bash
python -m venv .venv && . .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
OFFLINE=1 PYTHONPATH=src pytest -q -k "not online"
```
