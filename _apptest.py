# -*- coding: utf-8 -*-
"""遍历所有模块，用 Streamlit AppTest 验证渲染无异常。"""
from streamlit.testing.v1 import AppTest

MENUS = ["📊 总览", "🗺️ 地理分析", "📦 商品分析", "💳 支付分析", "⭐ 评分与评论", "👤 客户价值"]

total = 0
for m in MENUS:
    at = AppTest.from_file("streamlit_app.py", default_timeout=240)
    at.run()
    at.radio[0].set_value(m)
    at.run()
    n = len(at.exception)
    total += n
    print(m, "exceptions:", n)
    for e in at.exception:
        print("  EXC:", e.value)
print("TOTAL exceptions:", total)
print("ALL MODULES DONE")
