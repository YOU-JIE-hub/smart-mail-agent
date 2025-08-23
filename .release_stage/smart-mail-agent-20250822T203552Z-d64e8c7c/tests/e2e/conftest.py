import pathlib

import pytest

HERE = pathlib.Path(__file__).parent.resolve()


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        p = pathlib.Path(str(getattr(item, "fspath", ""))).resolve()
        if p and (p == HERE or HERE in p.parents):
            item.add_marker(pytest.mark.online)
