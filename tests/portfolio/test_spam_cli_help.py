import os, subprocess, sys, pathlib, textwrap

ROOT = pathlib.Path(__file__).resolve().parents[2]
def test_sma_spamcheck_help_runs():
    env = dict(os.environ)
    env["OFFLINE"] = "1"
    env["PYTHONPATH"] = f".:src"
    r = subprocess.run(
        [sys.executable, "-m", "smart_mail_agent.cli_spamcheck", "--help"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "usage" in r.stdout.lower()
