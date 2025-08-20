def test_import_small_modules():
    import modules.quote_logger as _ql
    import modules.sales_notifier as _sn
    import modules.apply_diff as _ad
    assert _ql and _sn and _ad
