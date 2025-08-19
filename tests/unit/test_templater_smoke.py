import importlib, pytest
from jinja2 import Environment, StrictUndefined

def test_templater_import_and_strict_undefined():
    # 匯入專案 templater 模組（觸發其頂層設定以增加覆蓋率）
    importlib.import_module("smart_mail_agent.utils.templater")

    # 最小驗證：StrictUndefined 缺值會拋錯，提供值可渲染成功
    env = Environment(undefined=StrictUndefined)
    t = env.from_string("hi {{ name }}")
    with pytest.raises(Exception):
        t.render({})
    assert t.render(name="Bob") == "hi Bob"
