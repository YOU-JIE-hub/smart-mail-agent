import json
import subprocess
import sys


def run(subject, content, sender):
    out = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "src.smart_mail_agent.cli_spamcheck",
            "--subject",
            subject,
            "--content",
            content,
            "--sender",
            sender,
        ],
        text=True,
    )
    return json.loads(out)


def test_spam_sample():
    res = run(
        "FREE bonus!!! Limited offer",
        "Click https://bit.ly/abc now to claim $100 USD",
        "promo@example.com",
    )
    assert res["is_spam"] is True
    assert res["score"] >= 0.6  # 目前是 0.68，留一點彈性


def test_ham_sample():
    res = run(
        "會議紀要", "附件為今天會議紀要與行動項，請查收。", "colleague@yourcompany.com"
    )
    assert res["is_spam"] is False
    assert res["score"] < 0.5


# --- extra edge cases ---
def test_zh_keywords_with_shortlink_spam():
    res = run("限時優惠", "免費加碼，詳見 https://t.co/xyz", "promo@x.com")
    assert res["is_spam"] is True
    assert res["score"] >= 0.6


def test_mixed_case_spam_words():
    res = run("FREE ViAgRa deal", "see tinyurl.com/xxx", "spam@x.com")
    assert res["is_spam"] is True
    assert res["score"] >= 0.6


def test_empty_subject_or_content_is_ham():
    res = run("", "", "someone@x.com")
    assert res["is_spam"] is False
    assert res["score"] < 0.5


def test_benign_offer_word_only_is_ham():
    # 僅含單字「offer」但無連結/金額，應低分且非垃圾
    res = run(
        "We offer to help with docs",
        "Let's review the draft tomorrow.",
        "colleague@x.com",
    )
    assert res["is_spam"] is False
    assert res["score"] < 0.5


def test_threshold_flag_overrides_env():
    out = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "src.smart_mail_agent.cli_spamcheck",
            "--subject",
            "FREE",
            "--content",
            "visit http://x",
            "--sender",
            "s@x.com",
            "--threshold",
            "0.99",
        ],
        text=True,
    )
    res = json.loads(out)
    # 0.99 幾乎一定比任何啟發式分數高，因此應為非垃圾
    assert res["is_spam"] is False


def test_explain_flag_includes_reasons():
    out = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "src.smart_mail_agent.cli_spamcheck",
            "--subject",
            "FREE bonus",
            "--content",
            "see tinyurl.com/a",
            "--sender",
            "s@x.com",
            "--explain",
        ],
        text=True,
    )
    res = json.loads(out)
    assert isinstance(res.get("explain"), list) and len(res["explain"]) >= 1
