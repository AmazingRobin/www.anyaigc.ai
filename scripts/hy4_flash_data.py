"""Tencent Hy4 flash catalog facts checked on 2026-11-17.

AnyAIGC prices: https://anyaigc.ai/pricing?keyword=hy4-flash (lowest rate in the model's
detail drawer; USD per 1M tokens, strings keep catalog precision):
  input $0.0281, output $0.1130, cache hit $0.0012. The drawer shows "省 59%".
Endpoints (catalog drawer): POST /v1/chat/completions (openai), POST /v1/messages (anthropic).
Catalog description: MoE multimodal text model, 1M context, preserved deep thinking,
Function Calling, structured JSON output, image understanding, cache acceleration.

Official list price (Tencent Hunyuan release post, 2026-11-16,
https://hy.tencent.com/research/hy4-flash): per 1M tokens, input 0.5 CNY, output 2 CNY,
cache-hit input 0.02 CNY. The post also states 224B total parameters (64B Engram),
12B active, multimodal, 1M context, decoding above 150 tps.
USD list prices use about 7.19 CNY per USD, the same rate hy4_data.py used:
  input $0.0695, output $0.2782, cache $0.0028.
Tencent also runs a limited 50%-off promotion on TokenHub until 2026-11-30. That promo is
NOT used as the baseline; the page says so.
The post gives no maximum output length, so the page does not state one.
"""

from decimal import Decimal

CHECKED_DATE = "2026-11-17"
RELEASE_DATE = "2026-11-16"
PRICING_URL = "https://anyaigc.ai/pricing?keyword=hy4-flash"
OFFICIAL_URL = "https://hy.tencent.com/research/hy4-flash"
DOC_CHAT = "https://docs.anyaigc.ai/reference/v1/chat/completions"
SLUG = "hy4-flash"
MODEL_ID = "hy4-flash"
NAME = "Hy4 Flash"

# key, AnyAIGC price, official USD list price, official CNY list price
PRICES = [
    dict(key="input", amount="0.0281", official="0.0695", cny="0.5"),
    dict(key="output", amount="0.1130", official="0.2782", cny="2"),
    dict(key="cache", amount="0.0012", official="0.0028", cny="0.02"),
]

LABEL = {
    "input": ("输入", "Input"),
    "output": ("输出", "Output"),
    "cache": ("缓存命中", "Cache hit"),
}

# Input and output sit at about 40% of the official list price (the catalog says "省 59%").
# The cache-hit rate is only quoted to 4 decimals ($0.0012), so its share is coarser.
for _p in PRICES:
    _share = Decimal(_p["amount"]) / Decimal(_p["official"])
    _low, _high = (Decimal("0.38"), Decimal("0.46")) if _p["key"] == "cache" else (Decimal("0.39"), Decimal("0.42"))
    assert _low <= _share <= _high, (_p, _share)

SAVE = 60  # percent below official list ("约官方 4 折"); the catalog shows 59 because it truncates
SHARE = 40  # percent of official list
