from __future__ import annotations

from modules.quotation import choose_package


def test_needs_manual_by_subject_flag():
    r = choose_package(subject="附件很大", content="")
    assert r["needs_manual"] is True


def test_needs_manual_by_content_size():
    r = choose_package(subject="", content="請看 6MB 附件")
    assert r["needs_manual"] is True
