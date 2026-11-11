"""MiniMax catalog facts checked on 2026-11-09.

Source: https://anyaigc.ai/pricing?provider=Minimax and its public
/api/pricing_new?lang=zh response. Monetary strings preserve the catalog's
displayed precision. Each token model uses the lowest displayed rate; other
available routes can have different prices. Details record unresolved billing
or endpoint gaps explicitly rather than inventing a contract.
"""

CHECKED_DATE = "2026-11-11"
PRICING_URL = "https://anyaigc.ai/pricing?provider=Minimax"
OFFICIAL_URL = "https://www.minimax.cn/"
DOC_CHAT = "https://docs.anyaigc.ai/reference/v1/chat/completions"
DOC_SPEECH = "https://docs.anyaigc.ai/en/reference/minimax/v1/t2a_v2?leaf=415373651"
DOC_H3 = "https://docs.anyaigc.ai/en/reference/v1/minimax/v2/video_generation?leaf=c%3A1791537497564"


def price(label_zh, label_en, amount, unit_zh, unit_en, **extra):
    return dict(label_zh=label_zh, label_en=label_en, amount=amount,
                unit_zh=unit_zh, unit_en=unit_en, **extra)


MODELS = [
    dict(
        id="MiniMax-M3.1-Flash", slug="minimax-m3.1-flash", name="MiniMax M3.1 Flash",
        kind="chat", category_zh="对话", category_en="Chat",
        desc_zh="原生多模态、1M 上下文的编程模型，支持工具调用、图片理解与可调思考深度。",
        desc_en="A native multimodal coding model with a 1M context window, tool use, image understanding, and adjustable reasoning depth.",
        capabilities_zh=["编程与 Agent 工作流", "图片理解", "1M 上下文", "可调思考深度"],
        capabilities_en=["Coding and agent workflows", "Image understanding", "1M context window", "Adjustable reasoning depth"],
        endpoints=["POST /v1/chat/completions"], doc=DOC_CHAT,
        prices=[price("输入", "Input", "0.0603", "1M tokens", "1M tokens"),
                price("输出", "Output", "0.2412", "1M tokens", "1M tokens"),
                price("缓存命中", "Cache hit", "0.0060", "1M tokens", "1M tokens")],
        price_start="0.0603", price_unit_zh="1M 输入 tokens", price_unit_en="1M input tokens",
        output_zh="一次请求返回模型回复；流式请求逐段返回。", output_en="One request returns a model response; streaming delivers it incrementally.",
    ),
    dict(
        id="MiniMax-M3", slug="minimax-m3", name="MiniMax M3",
        kind="chat", category_zh="对话", category_en="Chat",
        desc_zh="面向 Agent 推理、工具调用、代码与长上下文任务的 M 系列模型。",
        desc_en="An M-series language model for agent reasoning, tool calling, coding, and long-context tasks.",
        capabilities_zh=["Agent 推理", "工具调用", "代码生成", "长上下文任务"],
        capabilities_en=["Agent reasoning", "Tool calling", "Code generation", "Long-context tasks"],
        endpoints=["POST /v1/chat/completions"], doc=DOC_CHAT,
        prices=[price("输入（≤512K）", "Input (≤512K)", "0.2025", "1M tokens", "1M tokens"),
                price("输出（≤512K）", "Output (≤512K)", "0.8100", "1M tokens", "1M tokens"),
                price("缓存命中（≤512K）", "Cache hit (≤512K)", "0.0405", "1M tokens", "1M tokens"),
                price("输入（>512K，≤1M）", "Input (>512K, ≤1M)", "0.4050", "1M tokens", "1M tokens"),
                price("输出（>512K，≤1M）", "Output (>512K, ≤1M)", "1.6200", "1M tokens", "1M tokens"),
                price("缓存命中（>512K，≤1M）", "Cache hit (>512K, ≤1M)", "0.0810", "1M tokens", "1M tokens")],
        price_start="0.2025", price_unit_zh="1M 输入 tokens", price_unit_en="1M input tokens",
        output_zh="一次请求返回模型回复；超过 512K 输入 tokens 时使用第二档价格。",
        output_en="One request returns a model response; inputs above 512K tokens use the second price tier.",
        step_sizes=[512000, 1000000],
    ),
    dict(
        id="MiniMax-M2.7", slug="minimax-m2.7", name="MiniMax M2.7",
        kind="chat", category_zh="对话", category_en="Chat",
        desc_zh="面向编程、工具使用、搜索与办公任务的对话模型。",
        desc_en="A language model for coding, tool use, search, and office workflows.",
        capabilities_zh=["代码任务", "工具调用", "搜索工作流", "办公辅助"],
        capabilities_en=["Coding tasks", "Tool calling", "Search workflows", "Office assistance"],
        endpoints=["POST /v1/chat/completions"], doc=DOC_CHAT,
        prices=[price("输入", "Input", "0.4455", "1M tokens", "1M tokens"),
                price("输出", "Output", "1.7820", "1M tokens", "1M tokens")],
        price_start="0.4455", price_unit_zh="1M 输入 tokens", price_unit_en="1M input tokens",
        output_zh="一次请求返回模型回复；工具执行由应用编排。", output_en="One request returns a model response; your application handles tool execution.",
    ),
    dict(
        id="MiniMax-M2.5", slug="minimax-m2.5", name="MiniMax M2.5",
        kind="chat", category_zh="对话", category_en="Chat",
        desc_zh="适用于编程、工具调用、搜索与办公自动化的 M 系列对话模型。",
        desc_en="An M-series language model for coding, tool calling, search, and office automation.",
        capabilities_zh=["编程辅助", "工具调用工作流", "搜索辅助", "办公任务"],
        capabilities_en=["Coding assistance", "Tool workflows", "Search assistance", "Office tasks"],
        endpoints=["POST /v1/chat/completions"], doc=DOC_CHAT,
        prices=[price("输入", "Input", "0.2025", "1M tokens", "1M tokens"),
                price("输出", "Output", "0.8100", "1M tokens", "1M tokens"),
                price("缓存创建（5 分钟）", "Cache creation (5 minutes)", "0.2531", "1M tokens", "1M tokens"),
                price("缓存创建（1 小时）", "Cache creation (1 hour)", "0.4050", "1M tokens", "1M tokens")],
        price_start="0.2025", price_unit_zh="1M 输入 tokens", price_unit_en="1M input tokens",
        output_zh="一次请求返回模型回复；缓存参数支持情况以当前接口说明为准。",
        output_en="One request returns a model response; consult current API documentation for cache parameter support.",
    ),
    dict(
        id="MiniMax-H3", slug="minimax-h3", name="MiniMax H3",
        kind="video", category_zh="视频", category_en="Video",
        desc_zh="理解文本、图片、视频与音频参考，生成 768P 或 2K、最长 15 秒且带原生立体声的视频。",
        desc_en="Generate video up to 15 seconds in 768P or 2K with native stereo audio, using text, image, video, and audio context.",
        capabilities_zh=["文生视频与图生视频", "多模态参考", "768P / 2K", "原生立体声音频"],
        capabilities_en=["Text-to-video and image-to-video", "Multimodal references", "768P / 2K", "Native stereo audio"],
        endpoints=["POST /minimax/v2/video_generation"], doc=DOC_H3,
        prices=[price("768P 输出视频", "768P output video", "0.0750", "秒", "second"),
                price("768P 输入视频", "768P input video", "0.0750", "秒", "second"),
                price("2K 输出视频", "2K output video", "0.1219", "秒", "second"),
                price("2K 输入视频", "2K input video", "0.1219", "秒", "second"),
                price("视频再生成", "Video regeneration", "0.0450", "秒", "second"),
                price("参考图（前 5 张）", "Reference images (first 5)", "0", "张", "image"),
                price("参考图（第 6 张起）", "Reference images (from the 6th)", "0.0375", "张", "image")],
        price_start="0.0750", price_unit_zh="秒（768P 输出）", price_unit_en="second of 768P output",
        output_zh="异步生成任务，输出 4–15 秒的视频。", output_en="An asynchronous task generates a video lasting 4–15 seconds.",
        resolution=["768P", "2K"], durations=list(range(4, 16)),
    ),
    # Hailuo H3 through the tencent-vod AIGC route (catalog id aigc-video-hailuo).
    # Prices from the catalog detail view on 2026-11-11; docs leaf=399032083.
    dict(
        id="aigc-video-hailuo", slug="hailuo-h3", name="Hailuo H3",
        kind="hailuo", category_zh="视频", category_en="Video",
        desc_zh="海螺 H3 与 H3-Max 视频模型：H3 支持文生、首尾帧图生与多模态参考，H3-Max 为极速版，最长 15 秒。",
        desc_en="Hailuo H3 and H3-Max video: H3 handles text, first/last-frame and multimodal reference input; H3-Max is the fast version. Up to 15 seconds.",
        capabilities_zh=["H3 与 H3-Max 两个版本", "文生与首尾帧图生", "多模态参考（H3）", "768P / 2K / 480P"],
        capabilities_en=["H3 and H3-Max versions", "Text and first/last-frame input", "Multimodal references (H3)", "768P / 2K / 480P"],
        endpoints=["POST /tencent-vod/v1/aigc-video", "GET /tencent-vod/v1/query/{task_id}"],
        doc="https://docs.anyaigc.ai/en/reference/tencent-vod/v1/aigc-video?leaf=399032083",
        prices=[price("H3 768P 输出视频", "H3 768P output video", "0.0972", "秒", "second"),
                price("H3 768P 输入视频", "H3 768P input video", "0.0972", "秒", "second"),
                price("H3 2K 输出视频", "H3 2K output video", "0.1579", "秒", "second"),
                price("H3 2K 输入视频", "H3 2K input video", "0.1579", "秒", "second"),
                price("H3-Max 480P 输出视频", "H3-Max 480P output video", "0.0607", "秒", "second"),
                price("H3-Max 768P 输出视频", "H3-Max 768P output video", "0.0972", "秒", "second"),
                price("输入图片（前 5 张）", "Input images (first 5)", "0", "张", "image"),
                price("输入图片（第 6 张起）", "Input images (from the 6th)", "0.0486", "张", "image")],
        price_start="0.0607", price_unit_zh="秒（H3-Max 480P）", price_unit_en="second of H3-Max 480P",
        output_zh="异步任务，一次生成一段视频：H3 4–15 秒，H3-Max 5–15 秒，按实际输出秒数计费。",
        output_en="One asynchronous task produces one video: 4–15 seconds on H3, 5–15 on H3-Max, billed by actual output seconds.",
    ),
]

for version in ("2.8", "2.6", "02"):
    for tier, amount in (("hd", "0.5559"), ("turbo", "0.3176")):
        model_id = f"speech-{version}-{tier}"
        if version == "2.8":
            desc_zh = ("注重音色相似度与语调细节的语音合成模型。" if tier == "hd" else
                       "注重响应速度与生动自然表达的语音合成模型。")
            desc_en = ("A speech model focused on voice similarity and fine tonal detail." if tier == "hd" else
                       "A speech model focused on fast responses and vivid, natural expression.")
        else:
            desc_zh = "根据文本上下文表达情绪与语调，适用于播客、有声书、新闻、教育与数字人配音。"
            desc_en = "Context-aware speech synthesis for podcasts, audiobooks, news, education, and digital-human narration."
        MODELS.append(dict(
            id=model_id, slug=model_id, name=f"MiniMax Speech {version} {tier.upper()}",
            kind="speech", category_zh="语音", category_en="Speech",
            desc_zh=desc_zh, desc_en=desc_en,
            capabilities_zh=["文本转语音", "同步与异步接入", "可配置音色", "配音工作流"],
            capabilities_en=["Text-to-speech", "Synchronous and asynchronous APIs", "Configurable voices", "Narration workflows"],
            endpoints=["POST /minimax/v1/t2a_v2", "POST /minimax/v1/t2a_async_v2"], doc=DOC_SPEECH,
            prices=[price("语音合成", "Speech synthesis", amount, "万字符", "10,000 characters")],
            price_start=amount, price_unit_zh="万字符", price_unit_en="10,000 characters",
            output_zh="一次同步请求返回合成音频数据；异步请求返回任务，完成后获取音频。",
            output_en="A synchronous request returns synthesized audio; asynchronous requests return a task to retrieve later.",
            voice_tier=tier, version=version,
        ))

MODELS.append(dict(
    id="MiniMax-Voice-Design", slug="minimax-voice-design", name="MiniMax Voice Design",
    kind="voice-design", category_zh="语音", category_en="Speech",
    desc_zh="通过文字描述设计音色，为语音应用创建个性化的声音。",
    desc_en="Design a voice from a text description for personalized speech applications.",
    capabilities_zh=["文字描述设计音色", "语音角色原型", "品牌声音探索", "配音应用接入"],
    capabilities_en=["Text-guided voice design", "Voice character prototyping", "Brand voice exploration", "Narration integration"],
    endpoints=["POST /minimax/v1/voice_design"], doc="https://docs.anyaigc.ai/en/reference/minimax/v1/voice_design?leaf=418271561",
    prices=[price("音色设计", "Voice design", "0.3176", "万字符", "10,000 characters")],
    price_start="0.3176", price_unit_zh="万字符", price_unit_en="10,000 characters",
    output_zh="提交文字描述与预览文本，返回音色设计响应；示例输出完整 JSON。",
    output_en="Submit a voice description and preview text; the example prints the complete voice-design response.",
    endpoint_missing_from_catalog=False,
))

MODEL_BY_SLUG = {model["slug"]: model for model in MODELS}
MODEL_BY_ID = {model["id"]: model for model in MODELS}
SLUGS = ["minimax", *MODEL_BY_SLUG]

# Savings badges read directly from the AnyAIGC catalog detail view on 2026-11-09.
# These refer to the lowest rates used above. Do not infer a discount for models
# whose catalog detail does not display one, or expose internal routing names.
CATALOG_SAVINGS = {
    "minimax-m3.1-flash": 59,
    "minimax-m3": 32,
    "minimax-m2.5": 32,
}


def savings_label(lang, model=None):
    if model is None:
        return "低至约官方 4 折" if lang == "zh" else "Save up to 59% vs. official"
    percent = CATALOG_SAVINGS.get(model["slug"])
    if percent is None:
        return ""
    if lang == "en":
        return f"Save {percent}% vs. official"
    return "约官方 4 折" if percent == 59 else f"比官方省 {percent}%"


def savings_detail(lang, model=None):
    if model is None:
        return ("M3.1 Flash 比官方省 59%；M3、M2.5 省 32%。折扣与本页单价对应，以模型广场实时标注为准。" if lang == "zh" else
                "M3.1 Flash saves 59%; M3 and M2.5 save 32% versus official pricing. Savings apply to the rates shown here; see the catalog for current offers.")
    percent = CATALOG_SAVINGS.get(model["slug"])
    if percent is None:
        return ""
    return (f"模型广场标注：比官方省 {percent}%。折扣对应本页展示单价，实时价格与优惠以模型广场为准。" if lang == "zh" else
            f"The catalog lists {percent}% savings versus official pricing for the rates shown here. See the catalog for current prices and savings.")

# Items to settle against the live detail view/docs before publishing copy.
REVIEW_NOTES = [
    "Catalog cards label speech as per-call; the price-detail UI uses 10,000 characters.",
    "Voice Design endpoint is confirmed from docs leaf=418271561; its summary says voice_id while its response example shows data.task_id. Do not assume either in client parsing.",
    "H3 live detail view confirms 0.1219/second for 2K, 0.0450/second for regeneration, and 0.0375/image after five free images.",
    "M2.5 live detail view confirms 0.2531/1M for 5m cache creation and 0.4050/1M for 1h cache creation.",
    "Speech detail view quotes an approximate $1.2/voice fee on first synthesis with a designed or cloned voice; preset voices do not incur this extra fee.",
    "Voice Design detail view confirms /10,000 characters but does not define which request text fields count toward the character total.",
]
