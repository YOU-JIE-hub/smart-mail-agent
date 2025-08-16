from __future__ import annotations

from pathlib import Path

from modules.quotation import choose_package, generate_pdf_quote


def test_choose_package_needs_manual_by_phrase():
    res = choose_package(subject="附件很大，請協助", content="")
    assert res["needs_manual"] is True


def test_choose_package_needs_manual_by_size():
    res = choose_package(subject="", content="附件約 6MB，麻煩")
    assert res["needs_manual"] is True


def test_choose_package_other_patterns():
    r1 = choose_package(subject="想問 workflow 自動化", content="")
    assert r1["package"] in ("進階自動化", "企業整合", "專業")
    r2 = choose_package(subject="", content="需要 ERP / SSO 整合")
    assert r2["package"] in ("企業整合", "企業")


def test_generate_pdf_quote_legacy_signature(tmp_path):
    out = generate_pdf_quote("ACME", [("Basic", 1, 100.0)], outdir=str(tmp_path))
    p = Path(out)
    assert p.exists()
    assert p.suffix in (".pdf", ".txt")
