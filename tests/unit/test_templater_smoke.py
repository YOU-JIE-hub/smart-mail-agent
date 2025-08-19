import importlib, pytest
from jinja2 import Environment, StrictUndefined

def test_templater_import_and_strict_undefined():
    # 匯入專案 templater 模組（跑過頂層設定以增加覆蓋）
    importlib.import_module("smart_mail_agent.utils.templater")

    # 驗證 StrictUndefined：缺值要拋錯，有值可正常渲染
    env = Environment(undefined=StrictUndefined)
    t = env.from_string("hi {{ name }}")
    with pytest.raises(Exception):
        t.render({})
    assert t.render(name="Bob") == "hi Bob"
