"""Tencent Hy4 catalog facts checked on 2026-11-13.

AnyAIGC prices: https://anyaigc.ai/pricing?keyword=hy4 (lowest rate in the model's
detail dialog, group Self-Deployed-2; USD per 1M tokens, strings keep catalog precision).
Endpoints (catalog dialog): POST /v1/chat/completions (openai), POST /v1/messages (anthropic).
Official list price (Tencent Cloud, from https://hy.tencent.com/research/hy4):
  input 6 CNY, output 18 CNY, cache hit 0.3 CNY per 1M tokens.
USD equivalents come from the catalog base price (model_ratio 0.417 x 2 = $0.834 input),
which matches OpenRouter's Tencent Cloud list price at about 7.19 CNY/USD:
  input $0.834, output $2.501, cache $0.042.
OpenRouter shows a separate 50% promo price; it is NOT used as the baseline.
"""

from decimal import Decimal

CHECKED_DATE = "2026-11-13"
PRICING_URL = "https://anyaigc.ai/pricing?keyword=hy4"
OFFICIAL_URL = "https://hy.tencent.com/research/hy4"
DOC_CHAT = "https://docs.anyaigc.ai/reference/v1/chat/completions"
SLUG = "hy4"
MODEL_ID = "hy4"
NAME = "Hy4"

# key, AnyAIGC price, official USD list price, official CNY list price
PRICES = [
    dict(key="input", amount="0.5630", official="0.834", cny="6"),
    dict(key="output", amount="1.6880", official="2.501", cny="18"),
    dict(key="cache", amount="0.0283", official="0.042", cny="0.3"),
]

LABEL = {
    "input": ("输入", "Input"),
    "output": ("输出", "Output"),
    "cache": ("缓存命中", "Cache hit"),
}

# Every row must really sit at about 67.5% of the official list price (catalog says "省 32%").
for _p in PRICES:
    _share = Decimal(_p["amount"]) / Decimal(_p["official"])
    assert Decimal("0.66") <= _share <= Decimal("0.69"), (_p, _share)

SAVE = 32  # percent below official list, as the catalog displays it
SHARE = 67.5  # percent of official list
