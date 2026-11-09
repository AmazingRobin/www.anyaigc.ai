"""Xiaomi MiMo catalog facts checked on 2026-11-09.

AnyAIGC prices: https://anyaigc.ai/pricing?provider=XiaomiMiMo (lowest rate shown
in each model's detail dialog; USD per 1M tokens, strings keep catalog precision).
Official prices: https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go and the model
pages https://mimo.mi.com/models/zh-CN/mimo-v2.6-pro / mimo-v2.6-flash (USD list).
Retirement: https://mimo.mi.com/docs/zh-CN/updates/deprecate — mimo-v2.5-pro and
mimo-v2.5 were retired 2026-10-21 10:00 (UTC+8); since 2026-10-14 18:00 Xiaomi
routes them to mimo-v2.6-pro / mimo-v2.6-flash.
"""

from decimal import Decimal

CHECKED_DATE = "2026-11-09"
PRICING_URL = "https://anyaigc.ai/pricing?provider=XiaomiMiMo"
OFFICIAL_PRICE_URL = "https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go"
DEPRECATE_URL = "https://mimo.mi.com/docs/zh-CN/updates/deprecate"
DOC_CHAT = "https://docs.anyaigc.ai/reference/v1/chat/completions"


def rate(key, amount, official=None):
    return dict(key=key, amount=amount, official=official)


LABEL = {
    "input": ("输入", "Input"),
    "output": ("输出", "Output"),
    "cache": ("缓存命中", "Cache hit"),
}

MODELS = [
    dict(
        id="mimo-v2.6-pro", slug="mimo-v2.6-pro", name="MiMo-V2.6-Pro", short="V2.6 Pro",
 legacy=False, card="card-pro.webp", tier="pro",
        tagline_zh="小米 MiMo 当前的全模态旗舰模型", tagline_en="Xiaomi MiMo's current omni-modal flagship",
        desc_zh="小米 MiMo 的全模态旗舰模型，面向专业、长程、复杂的工作流，重点优化代码、办公、设计、科研与网络安全任务。",
        desc_en="Xiaomi MiMo's omni-modal flagship for professional, long-horizon workflows, tuned for coding, office work, design, research and security tasks.",
 specs_zh=[("输入模态", "文本、图像、视频、音频"), ("输出模态", "文本"), ("上下文长度", "1M tokens"), ("最大输出", "128K tokens")],
 specs_en=[("Input", "Text, image, video, audio"), ("Output", "Text"), ("Context window", "1M tokens"), ("Max output", "128K tokens")],
 caps_zh=["全模态理解", "深度思考", "工具调用", "流式输出", "结构化输出", "上下文缓存"],
        caps_en=["Omni-modal understanding", "Deep thinking", "Tool calling", "Streaming", "Structured output", "Context caching"],
        prices=[rate("input", "0.1749", "0.435"), rate("output", "0.3497", "0.87"), rate("cache", "0.0014", "0.0036")],
    ),
    dict(
 id="mimo-v2.6-flash", slug="mimo-v2.6-flash", name="MiMo-V2.6-Flash", short="V2.6 Flash",
        legacy=False, card="card-flash.webp", tier="flash",
        tagline_zh="全模态、高智能、低成本的高效推理模型", tagline_en="Omni-modal, capable and efficient at low cost",
        desc_zh="全模态、高智能、低成本的高效推理模型，适合专业办公中的高频调用与规模化任务。",
        desc_en="An efficient omni-modal reasoning model for high-volume office workloads and tasks that need to run at scale.",
        specs_zh=[("输入模态", "文本、图像、视频、音频"), ("输出模态", "文本"), ("上下文长度", "1M tokens"), ("最大输出", "128K tokens")],
        specs_en=[("Input", "Text, image, video, audio"), ("Output", "Text"), ("Context window", "1M tokens"), ("Max output", "128K tokens")],
 caps_zh=["全模态理解", "深度思考", "工具调用", "流式输出", "结构化输出", "上下文缓存"],
        caps_en=["Omni-modal understanding", "Deep thinking", "Tool calling", "Streaming", "Structured output", "Context caching"],
        prices=[rate("input", "0.0563", "0.14"), rate("output", "0.1126", "0.28"), rate("cache", "0.0011", "0.0028")],
    ),
    dict(
 id="mimo-v2.5-pro", slug="mimo-v2.5-pro", name="MiMo-V2.5-Pro", short="V2.5 Pro",
 legacy=True, successor="mimo-v2.6-pro", card=None, tier="pro",
 tagline_zh="面向 Agent 与编程的上一代 Pro 模型", tagline_en="The previous-generation Pro model for agents and coding",
        desc_zh="上一代 Pro 模型，面向复杂任务，针对 Agent 与编程场景深度优化，仅支持文本输入。",
 desc_en="The previous-generation Pro model for complex tasks, optimized for agent and coding work, with text-only input.",
 specs_zh=[("输入模态", "文本"), ("输出模态", "文本"), ("官方状态", "2026-10-21 停用"), ("官方替代", "mimo-v2.6-pro")],
        specs_en=[("Input", "Text"), ("Output", "Text"), ("Official status", "Retired 2026-10-21"), ("Replacement", "mimo-v2.6-pro")],
        caps_zh=["Agent 任务", "编程", "工具调用", "流式输出"],
 caps_en=["Agent tasks", "Coding", "Tool calling", "Streaming"],
        prices=[rate("input", "0.4404"), rate("output", "0.8809"), rate("cache", "0.0037")],
    ),
    dict(
        id="mimo-v2.5", slug="mimo-v2.5", name="MiMo-V2.5", short="V2.5",
        legacy=True, successor="mimo-v2.6-flash", card=None, tier="flash",
        tagline_zh="上一代原生全模态模型", tagline_en="The previous-generation native omni-modal model",
 desc_zh="上一代原生全模态模型，支持文本、图像、视频与音频理解，具备 Agent 能力。",
        desc_en="The previous-generation native omni-modal model, with text, image, video and audio understanding and agent capabilities.",
        specs_zh=[("输入模态", "文本、图像、视频、音频"), ("输出模态", "文本"), ("官方状态", "2026-10-21 停用"), ("官方替代", "mimo-v2.6-flash")],
        specs_en=[("Input", "Text, image, video, audio"), ("Output", "Text"), ("Official status", "Retired 2026-10-21"), ("Replacement", "mimo-v2.6-flash")],
        caps_zh=["全模态理解", "Agent 任务", "工具调用", "流式输出"],
        caps_en=["Omni-modal understanding", "Agent tasks", "Tool calling", "Streaming"],
        prices=[rate("input", "0.1418"), rate("output", "0.2835"), rate("cache", "0.0028")],
    ),
]

MODEL_BY_SLUG = {m["slug"]: m for m in MODELS}
SLUGS = ["mimo"] + [m["slug"] for m in MODELS]


def ratio(model):
    """AnyAIGC input price as a share of the official input price, e.g. 0.402."""
    p = model["prices"][0]
    if not p["official"]:
        return None
    return Decimal(p["amount"]) / Decimal(p["official"])


# Every current (non-legacy) model must really be about 40% of the official list price.
for _m in MODELS:
    for _p in ([] if _m["legacy"] else _m["prices"][:2]):
        _share = Decimal(_p["amount"]) / Decimal(_p["official"])
        assert Decimal("0.39") <= _share <= Decimal("0.41"), (_m["id"], _p, _share)


def deal(lang, model=None):
    """Short '官方 4 折' label for current models (and the overview)."""
    if model is not None and model["legacy"]:
        return ""
    return "官方 4 折" if lang == "zh" else "~60% off official"
