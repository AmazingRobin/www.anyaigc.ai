"""Build the 26 static MiniMax topic pages: python scripts/minimax_pages.py."""

from decimal import Decimal
from html import escape, unescape
from pathlib import Path
import json
import re

from minimax_data import MODELS, MODEL_BY_SLUG, CHECKED_DATE, PRICING_URL, CATALOG_SAVINGS, savings_label, savings_detail
from minimax_examples import examples
import payments
import trust

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.anyaigc.ai"
REG = "https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9"
SUPPORT = "https://anyaigc.ai/customersupport"
VER = "20261109e"
ICON = (ROOT / "assets/icons/minimax-color.svg").read_text(encoding="utf-8")


def pick(lang, zh, en):
    return zh if lang == "zh" else en


def txt(value):
    return unescape(re.sub(r"<[^>]+>", "", value))


def h(value):
    return escape(str(value), quote=True)


def url(lang, slug):
    return f"{SITE}/{lang}/models/{slug}"


def breadcrumb_items(lang, model):
    items = [(pick(lang, "模型专题", "Model guides"), f"{SITE}/{lang}/models/"),
             ("MiniMax", url(lang, "minimax"))]
    if model:
        short_name = model["name"].removeprefix("MiniMax ").replace("TURBO", "Turbo")
        items.append((short_name, url(lang, model["slug"])))
    return items


def doc_url(lang, value):
    value = value.replace("https://docs.anyaigc.ai/en/", "https://docs.anyaigc.ai/")
    return value if lang == "zh" else value.replace("https://docs.anyaigc.ai/", "https://docs.anyaigc.ai/en/", 1)


def logo(identifier):
    icon = ICON.replace("lobe-icons-minimax-_R_0_", f"mm-gradient-{identifier}")
    icon = re.sub(r'<svg\b[^>]*>', '<svg class="mm-mark" viewBox="0 0 24 24" width="32" height="32" aria-hidden="true" focusable="false">', icon, count=1)
    return re.sub(r"<title>.*?</title>", "", icon)


def section(sid, kicker, title, lead, body, soft=False):
    cls = "mm-section mm-soft" if soft else "mm-section"
    return (f'<section class="{cls}" id="{sid}" aria-labelledby="{sid}-title"><div class="mm-wrap">\n'
            f'<p class="mm-kicker">{h(kicker)}</p><h2 id="{sid}-title">{h(title)}</h2>\n'
            f'<p class="mm-section-lead">{lead}</p>\n{body}\n</div></section>\n')


def button(label, href, secondary=False, **attrs):
    more = " ".join(f'{k.replace("_", "-")}="{h(v)}"' for k, v in attrs.items())
    return f'<a class="mm-btn mm-btn-{"secondary" if secondary else "primary"}" href="{h(href)}" {more}>{h(label)} <span aria-hidden="true">↗</span></a>'


def metadata(lang, model):
    name = model["name"] if model else "MiniMax"
    if model is None:
        title = pick(lang, "MiniMax API 价格与接入｜对话视频语音 - AnyAIGC", "MiniMax API Pricing | Chat, video, speech - AnyAIGC")
    else:
        title_zh = {"chat": "编程对话", "speech": "语音合成", "video": "视频生成", "voice-design": "音色设计"}[model["kind"]]
        title_en = {"chat": "Coding", "speech": "Speech", "video": "Video", "voice-design": "Voice design"}[model["kind"]]
        title = pick(lang, f"{name} API 价格与接入｜{title_zh} - AnyAIGC", f"{name} API Pricing | {title_en} - AnyAIGC")
    if model is None:
        desc = pick(lang,
                    "MiniMax API 全系价格与接入：12 个对话、视频与语音模型，文本输入 $0.0603/百万 tokens 起，覆盖编程、H3 视频和语音合成，并发不限，支持对公转账、合同与增值税专票。",
                    "MiniMax API pricing for chat, video and speech. Text from $0.0603/1M input tokens, unlimited concurrency, bank transfers and VAT invoices on AnyAIGC.")
    else:
        kind = model["kind"]
        short_zh = {"chat": "对话、编程与应用开发", "speech": "文本转语音与配音工作流", "video": "768P/2K 视频与原生立体声音频", "voice-design": "文字描述设计音色与声音原型"}[kind]
        short_en = {"chat": "1M input tokens for chat and coding", "speech": "10K characters for text-to-speech", "video": "second for 768P video with audio", "voice-design": "10K characters for voice design"}[kind]
        desc = pick(lang,
                    f'{name} API 价格与接入：${model["price_start"]}/{model["price_unit_zh"]}，用于{short_zh}，提供请求示例与完整价格表，并发不限，支持对公转账、服务合同与增值税专票。',
                    f'{name} API: ${model["price_start"]}/{short_en}. Unlimited concurrency, bank transfers and VAT invoices on AnyAIGC.')
    if model is None:
        title = pick(lang, "MiniMax API 价格与接入｜低至约官方4折 - AnyAIGC", "MiniMax API Pricing | Save up to 59% vs. Official - AnyAIGC")
        desc = pick(lang,
                    "MiniMax API 全系价格与接入：M3.1 Flash 约官方4折、省59%，输入 $0.0603/百万 tokens 起。覆盖对话、H3视频和语音，并发不限，支持对公转账与增值税专票。",
                    "MiniMax APIs: save up to 59% vs. official. Chat from $0.0603/1M input tokens, plus video and speech. Unlimited concurrency, VAT invoices and contracts.")
    elif model["slug"] in CATALOG_SAVINGS:
        percent = CATALOG_SAVINGS[model["slug"]]
        title = pick(lang, f"{name} API 价格｜{savings_label(lang, model)} - AnyAIGC", f"{name} API Pricing | Save {percent}% - AnyAIGC")
        desc = pick(lang,
                    f'{name} API 模型广场标注比官方省{percent}%，输入 ${model["price_start"]}/百万 tokens，支持对话与编程。提供完整价格表和接入示例，并发不限，支持对公转账与增值税专票。',
                    f'{name} API: save {percent}% vs. official, from ${model["price_start"]}/1M input tokens for chat and coding. Unlimited concurrency, VAT invoices and contracts.')
    assert len(desc) <= (120 if lang == "zh" else 160), (name, lang, len(desc), desc)
    assert len(desc) >= (60 if lang == "zh" else 120), (name, lang, len(desc), desc)
    assert (sum(2 if ord(c) > 0x2e7f else 1 for c in title) <= 64 if lang == "zh" else len(title) <= 65), title
    return name, title, desc


def price_label(lang, model, price):
    if model["kind"] == "voice-design":
        return pick(lang, "音色设计（字符计费）", "Voice design (character billing)")
    return price["label_" + lang]


def faq_items(lang, model):
    name = model["name"] if model else "MiniMax"
    if model:
        kind = model["kind"]
        price_answer = "; ".join(f'{p["label_" + lang]} ${p["amount"]}/{p["unit_" + lang]}' for p in model["prices"])
        price_answer += pick(lang, "。单位为 USD，实时价格以模型广场为准。", ". All prices are in USD; consult the model catalog for current rates.")
        if kind == "voice-design":
            price_answer = pick(lang, "模型广场列示 $0.3176/万字符。具体计入哪些文本、何时扣费，请在正式批量调用前联系客服确认。", "The catalog lists $0.3176 per 10,000 characters. Confirm which text counts and when charges apply with support before a batch rollout.")
        endpoint = "、".join(model["endpoints"]) if lang == "zh" else "; ".join(model["endpoints"])
        endpoint_answer = pick(lang, f'使用 {endpoint}，API 域名为 https://anyaigc.ai，通过 Authorization: Bearer 传入 API Key。', f'Use {endpoint} at https://anyaigc.ai and pass your API key through Authorization: Bearer.')
        if kind == "voice-design":
            endpoint_answer += pick(lang, "音色设计请求使用 prompt、preview_text 与自定义 voice_id，不发送 model 字段。", " Voice Design takes prompt, preview_text and a custom voice_id; it does not use a model field.")
        if kind == "speech":
            detail_q = pick(lang, "音色如何选择？会有额外费用吗？", "How do I choose a voice, and can it cost extra?")
            detail_a = pick(lang, "同步示例通过 voice_setting.voice_id 指定可用音色。请使用你有权调用的音色 ID；模型广场提示非预设音色可能另有音色费用，具体金额需按所选音色确认。", "Set voice_setting.voice_id to a voice available to your account. The catalog notes that non-preset voices may incur a separate voice fee; confirm the charge for the voice you choose.")
        elif kind == "video":
            detail_q = pick(lang, "H3 支持哪些时长、分辨率和参考素材？", "Which durations, resolutions and references does H3 support?")
            detail_a = pick(lang, "MiniMax-H3 支持 4–15 秒、768P 或 2K。content 必须包含且只包含一段非空文本；可提供首尾帧或参考图片、视频、音频，两种模式不能混用。纯文生视频需指定 ratio。", "MiniMax-H3 supports 4–15 seconds at 768P or 2K. The content array must contain exactly one non-empty text item. Use first/last frames or reference images, video and audio; do not mix those modes. Text-only generation requires ratio.")
        elif kind == "voice-design":
            detail_q = pick(lang, "音色设计需要提交哪些内容？", "What should I provide for Voice Design?")
            detail_a = pick(lang, "prompt 描述想要的音色与表达方式，preview_text 提供试听用文本，voice_id 使用自定义唯一音色 ID。示例通过 MINIMAX_DESIGNED_VOICE_ID 环境变量读取该 ID。", "Describe the desired voice and delivery in prompt, provide sample text in preview_text, and choose a unique custom voice_id. The examples read that ID from MINIMAX_DESIGNED_VOICE_ID.")
        else:
            detail_q = pick(lang, f"{name} 适合什么任务？", f"What is {name} suited for?")
            detail_a = model["desc_" + lang]
            if model["id"] == "MiniMax-M3":
                detail_a += pick(lang, "输入不超过 512K 时使用第一档价格，超过 512K 且不超过 1M 时使用第二档；输出价格也随该输入档位变化。", " Inputs up to 512K use the first price tier; inputs above 512K and up to 1M use the second, including its output rate.")
        output = model["output_" + lang]
        if kind == "voice-design":
            output = pick(lang, "接口文档正文描述返回 voice_id，但响应示例显示 data.task_id，二者不一致。本页示例保留完整 JSON 响应，不假定字段位置或下载方式；正式对接前请确认实际响应。", "The documentation describes a voice_id result, but its example shows data.task_id. The examples print the full JSON response without assuming a field or download flow. Confirm the actual response before integrating it.")
        if kind == "speech":
            output = pick(lang, "本页同步示例返回 JSON，其中 data.audio 为音频内容或 URL，具体格式以请求设置和实际响应为准。异步端点也列在模型广场中；任务查询与下载请按当前接口文档接入。", "The synchronous example returns JSON; data.audio contains audio data or a URL according to the request and actual response. The catalog also lists an asynchronous endpoint. Follow its current documentation for task retrieval and downloads.")
        six = [(pick(lang, f"{name} API 多少钱？", f"How much does the {name} API cost?"), price_answer),
               (pick(lang, "应该使用哪个 API 接口？", "Which API endpoint should I use?"), endpoint_answer),
               (detail_q, detail_a),
               (pick(lang, "一次请求会返回什么？", "What does one request return?"), output)]
    else:
        six = [
            (pick(lang, "MiniMax API 的起步价格是多少？", "What are the starting prices for MiniMax APIs?"), pick(lang, "M3.1 Flash 输入 $0.0603/百万 tokens；Speech Turbo 语音 $0.3176/万字符，HD 语音 $0.5559/万字符；H3 768P 输出视频 $0.0750/秒。各功能采用不同计费单位，完整价格见表格，实时价格以模型广场为准。", "M3.1 Flash input is $0.0603 per 1M tokens; Speech Turbo is $0.3176 and HD is $0.5559 per 10,000 characters; H3 768P output is $0.0750 per second. Units differ by service. See the full table and the catalog for current prices.")),
            (pick(lang, "12 个模型如何选择？", "How should I choose among the 12 models?"), pick(lang, "对话与开发可选 M3.1 Flash、M3、M2.7 或 M2.5；视频选 H3；文本转语音按版本和 HD/Turbo 选择六个 Speech 型号；文字设计音色选 Voice Design。请先用自己的任务和音色做小规模测试。", "Choose M3.1 Flash, M3, M2.7 or M2.5 for chat and development; H3 for video; one of six Speech versions and HD/Turbo variants for narration; and Voice Design for text-guided voices. Test with your own workload and voice first.")),
            (pick(lang, "这些模型使用同一个接口吗？", "Do these models share one endpoint?"), pick(lang, "使用同一个 AnyAIGC API Key 和域名，但端点按能力区分：对话用 /v1/chat/completions，H3 用 /minimax/v2/video_generation，语音用 /minimax/v1/t2a_v2 或 /minimax/v1/t2a_async_v2，音色设计用 /minimax/v1/voice_design。", "They share an AnyAIGC API key and domain. Chat uses /v1/chat/completions, H3 uses /minimax/v2/video_generation, speech uses /minimax/v1/t2a_v2 or /minimax/v1/t2a_async_v2, and Voice Design uses /minimax/v1/voice_design.")),
            (pick(lang, "视频、语音和音色设计如何获取结果？", "How do I receive video, speech and voice-design results?"), pick(lang, "H3 创建请求先返回 task_id；同步语音返回音频相关 JSON。Voice Design 文档正文与响应示例的字段不一致，接入时保留原始响应并确认格式。各独立专题提供对应的最小请求。", "H3 creation returns a task_id first, while synchronous speech returns audio-related JSON. Voice Design has inconsistent result fields in its documentation; retain the full response and confirm the contract. Each guide includes a minimal request.")),
        ]
    discount = savings_detail(lang, model)
    if discount:
        question, answer = six[0]
        six[0] = (question, answer + " " + discount)
    six += [
        (pick(lang, "并发和 RPM 有限制吗？", "Are there concurrency or RPM limits?"), pick(lang, "AnyAIGC 的 MiniMax 接入并发不限，不设固定 RPM 上限。模型生成仍需要处理时间，请在应用中配置超时、错误处理和合理重试。", "AnyAIGC offers unlimited concurrency for MiniMax, with no fixed RPM cap. Generation still takes time; configure timeouts, error handling and appropriate retries in your application.")),
        (pick(lang, "生成内容可以商用吗？", "Can generated content be used commercially?"), pick(lang, "模型与输出的商用授权以 MiniMax 官方条款为准。使用参考素材、音色及生成内容时，也应具备相关权利或授权。AnyAIGC 是独立 API 服务商。", "Commercial use of the models and their outputs is governed by MiniMax's official terms. Ensure you have the relevant rights to reference material, voices and generated content. AnyAIGC is an independent API provider.")),
    ]
    enterprise = [
        (pick(lang, "AnyAIGC 能开发票吗？支持增值税专票吗？", "Can AnyAIGC issue invoices, including VAT special invoices?"), pick(lang, "支持。可按实际充值金额开具增值税普通发票和增值税专用发票，联系企业客服办理即可。", "Yes. AnyAIGC can issue invoices for actual top-ups, including Chinese VAT general and VAT special invoices. Contact enterprise support to arrange them.")),
        (pick(lang, "企业可以对公转账和签合同吗？", "Can my company pay by bank transfer and sign a contract?"), pick(lang, "可以。支持企业对公转账充值，可签订服务合同，并提供专属客服与技术对接，配合采购、财务和研发流程。", "Yes. Companies can top up by corporate bank transfer, sign a service contract, and work with dedicated support and a technical contact for procurement and integration.")),
    ]
    all_items = six + enterprise + [(payments.Q[lang], payments.A[lang])] + trust.FAQ[lang]
    assert len(all_items) == 12
    return all_items


def head(lang, slug, model, faqs):
    name, title, desc = metadata(lang, model)
    me = url(lang, slug)
    image = f"{SITE}/assets/og/{slug}-{lang}.png"
    prices = [(m, p) for m in ([model] if model else MODELS) for p in m["prices"]]
    amounts = [Decimal(p["amount"]) for _, p in prices]
    offers = [{"@type": "Offer", "name": f'{m["id"]} {price_label(lang, m, p)} / {p["unit_" + lang]}',
               "price": p["amount"], "priceCurrency": "USD", "url": me + "#pricing"} for m, p in prices]
    crumbs = [{"@type": "ListItem", "position": i, "name": label, "item": href}
              for i, (label, href) in enumerate(breadcrumb_items(lang, model), 1)]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": SITE + "/#org", "name": "AnyAIGC", "url": "https://anyaigc.ai", "logo": SITE + "/logo.webp"},
        {"@type": "WebSite", "@id": SITE + "/#website", "name": "AnyAIGC", "url": SITE + "/", "publisher": {"@id": SITE + "/#org"}},
        {"@type": "WebPage", "@id": me + "#webpage", "url": me, "name": title, "description": desc, "inLanguage": pick(lang, "zh-CN", "en"), "dateModified": CHECKED_DATE, "isPartOf": {"@id": SITE + "/#website"}, "breadcrumb": {"@id": me + "#breadcrumb"}, "mainEntity": {"@id": me + "#product"}},
        {"@type": "BreadcrumbList", "@id": me + "#breadcrumb", "itemListElement": crumbs},
        {"@type": "Product", "@id": me + "#product", "name": name + " API (AnyAIGC)", "description": desc, "sku": model["id"] if model else "minimax", "image": image, "brand": {"@type": "Brand", "name": "MiniMax"}, "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": str(min(amounts)), "highPrice": str(max(amounts)), "offerCount": len(offers), "url": me + "#pricing", "offers": offers}},
        {"@type": "FAQPage", "@id": me + "#faq", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": txt(a)}} for q, a in faqs]},
    ]}
    locale, alternate = ("zh_CN", "en_US") if lang == "zh" else ("en_US", "zh_CN")
    keys = pick(lang, f"{name} API,{name} API 价格,{name} API key,{name} API 企业,{name} API 发票,MiniMax API", f"{name} API,{name} API pricing,{name} API key,{name} API for business,MiniMax API")
    return f'''<!DOCTYPE html>
<html lang="{pick(lang, 'zh-CN', 'en')}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{h(title)}</title>
<meta name="description" content="{h(desc)}">
<meta name="keywords" content="{h(keys)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#181a23">
<link rel="canonical" href="{me}">
<link rel="alternate" hreflang="zh-CN" href="{url('zh', slug)}">
<link rel="alternate" hreflang="en" href="{url('en', slug)}">
<link rel="alternate" hreflang="x-default" href="{url('en', slug)}">
<link rel="icon" href="/favicon.ico">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AnyAIGC">
<meta property="og:locale" content="{locale}">
<meta property="og:locale:alternate" content="{alternate}">
<meta property="og:url" content="{me}">
<meta property="og:title" content="{h(title)}">
<meta property="og:description" content="{h(desc)}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{h(name)} API · AnyAIGC">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{h(title)}">
<meta name="twitter:description" content="{h(desc)}">
<meta name="twitter:image" content="{image}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261024b">
<link rel="stylesheet" href="/assets/models/minimax.css?v={VER}">
<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
'''


def nav(lang, slug, model):
    other = "en" if lang == "zh" else "zh"
    links = [(f"/{lang}/models/", pick(lang, "模型专题", "Model guides")),
             (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
             ("#pricing", pick(lang, "价格", "Pricing")),
             ("#enterprise", pick(lang, "企业接入", "Enterprise")),
             (doc_url(lang, model["doc"] if model else "https://docs.anyaigc.ai/reference/v1/chat/completions"), pick(lang, "API 文档", "API docs"))]
    return (f'<a class="mm-skip" href="#main">{pick(lang, "跳到主要内容", "Skip to main content")}</a>\n'
            '<header class="mm-nav"><div class="mm-wrap mm-nav-inner">'
            '<a class="mm-brand" href="/">AnyAIGC<span>× MiniMax</span></a>'
            f'<nav id="mm-navigation" aria-label="{pick(lang, "主导航", "Main navigation")}"><ul class="mm-nav-links">'
            + "".join(f'<li><a href="{h(href)}">{label}</a></li>' for href, label in links)
            + '</ul></nav><ul class="mm-nav-actions">'
            f'<li><a href="/{other}/models/{slug}" hreflang="{pick(other, "zh-CN", "en")}">{pick(lang, "EN", "中文")}</a></li>'
            f'<li><a href="https://anyaigc.ai/console">{pick(lang, "登录", "Log in")}</a></li>'
            f'<li>{button(pick(lang, "注册", "Sign up"), REG)}</li></ul>'
            f'<button class="mm-menu" type="button" aria-controls="mm-navigation" aria-expanded="false" aria-label="{pick(lang, "打开导航菜单", "Open navigation menu")}"></button>'
            '</div></header>\n')


def hero(lang, slug, model):
    name = model["name"] if model else "MiniMax"
    kind = model["kind"] if model else "chat"
    hero_media = {"chat": "hero-text", "video": "hero-video", "speech": "hero-speech", "voice-design": "hero-speech"}[kind]
    media = (f'<video class="mm-hero-bg" muted loop playsinline preload="metadata" poster="/assets/models/minimax/{hero_media}.webp" aria-hidden="true">'
             f'<source src="/assets/models/minimax/{hero_media}.mp4" type="video/mp4"></video>')
    items = breadcrumb_items(lang, model)
    crumbs = ''.join(f'<li><a href="{h(href.removeprefix(SITE))}">{h(label)}</a></li>' for label, href in items[:-1])
    crumbs += f'<li aria-current="page">{h(items[-1][0])}</li>'
    back_href = f"/{lang}/models/minimax" if model else f"/{lang}/models/"
    back_label = pick(lang, "MiniMax 全系模型", "All MiniMax models") if model else pick(lang, "全部模型专题", "All model guides")
    back = f'<a class="mm-crumb-back" href="{back_href}"><span aria-hidden="true">←</span>{h(back_label)}</a>'
    if model:
        heading = h(name) + " API"
        lead = h(model["desc_" + lang]) + f' <strong>${model["price_start"]} / {h(model["price_unit_" + lang])}</strong>'
        eyebrow = model["id"] + " · " + model["category_" + lang]
    else:
        heading = "MiniMax API<br>" + pick(lang, "让创作，成为可能。", "Ideas into experiences.")
        lead = pick(lang, "从对话与编程，到视频与声音。一个 AnyAIGC API Key 接入 12 个 MiniMax 模型，文本输入 <strong>$0.0603 / 百万 tokens 起</strong>。", "From conversation and code to video and voice. Access 12 MiniMax models with one AnyAIGC API key, with text input from <strong>$0.0603 / 1M tokens</strong>.")
        eyebrow = pick(lang, "MINIMAX · 对话 / 视频 / 语音", "MINIMAX · CHAT / VIDEO / SPEECH")
    facts = [pick(lang, "并发不限", "Unlimited concurrency"), pick(lang, "300+ 模型 · 一个 Key", "300+ models · One key"), pick(lang, "对公 · 专票 · 合同", "Bank transfer · VAT · Contracts")]
    discount = savings_label(lang, model)
    deal = ""
    if discount:
        percent = CATALOG_SAVINGS[model["slug"]] if model else 59
        scope = model["name"] if model else "MiniMax M3.1 Flash"
        detail = pick(lang, f"{scope} · 比官方省 {percent}%", f"{scope} · Savings shown in the catalog")
        deal = f'<a class="mm-deal" href="#pricing"><strong>{h(discount)}</strong><span>{h(detail)}</span></a>'
    return ('<main id="main">\n<section class="mm-hero" aria-labelledby="hero-title">' + media
            + '<div class="mm-wrap mm-hero-inner">'
            f'<nav class="mm-breadcrumb" aria-label="{pick(lang, "面包屑", "Breadcrumb")}"><ol class="mm-crumbs">{crumbs}</ol>{back}</nav>'
            f'<p class="mm-eyebrow">{logo("hero")}<span>{h(eyebrow)}</span></p>'
            f'<h1 id="hero-title">{heading}</h1>{deal}<p class="mm-lead">{lead}</p>'
            '<div class="mm-actions">' + button(pick(lang, "获取 API Key", "Get an API key"), REG)
            + button(pick(lang, "查看 API 价格", "Explore API pricing"), "#pricing", True)
            + '</div><ul class="mm-facts">' + "".join(f"<li>{h(f)}</li>" for f in facts) + '</ul></div>'
            + f'<button type="button" data-video-toggle hidden>{pick(lang, "播放背景", "Play motion")}</button>'
            + '</section>\n')


def model_grid(lang, slug):
    cards = []
    for item in [MODEL_BY_SLUG[x] for x in ("minimax-m3.1-flash", "minimax-h3", "speech-2.8-hd")]:
        card_media = {"chat": "card-text.webp", "video": "card-video.webp", "speech": "card-speech.webp", "voice-design": "card-speech.webp"}[item["kind"]]
        deal_tag = f'<li class="mm-tag-deal">{h(savings_label(lang, item))}</li>' if savings_label(lang, item) else ""
        cards.append(f'''<article class="mm-model-card"><img src="/assets/models/minimax/{card_media}" width="820" height="500" loading="lazy" alt=""><div class="mm-card-body"><h3><a href="/{lang}/models/{item["slug"]}">{h(item["name"])}</a></h3><p>{h(item["desc_" + lang])}</p><ul class="mm-tags">{deal_tag}<li>{h(item["category_" + lang])}</li><li>${h(item["price_start"])} / {h(item["price_unit_" + lang])}</li><li>{pick(lang, "并发不限", "Unlimited concurrency")}</li></ul></div></article>''')
    return ''.join(cards)


def capabilities(lang, model):
    caps = model["capabilities_" + lang] if model else [pick(lang, x, y) for x, y in [("对话与编程", "Chat and coding"), ("视频生成", "Video generation"), ("语音合成", "Speech synthesis"), ("音色设计", "Voice design"), ("一个 API Key", "One API key"), ("国内直连", "Direct access from China")]]
    kind = model["kind"] if model else "overview"
    descriptions = {
        "chat": [("把需求转成草案、解释或代码，再由应用组织后续步骤。", "Turn a request into a draft, explanation or code, then let your application organize the next steps."), ("围绕明确的输入构建工作流，工具执行与结果校验由应用负责。", "Build around explicit inputs; your application handles tool execution and validates results."), ("选择适合上下文与成本的型号，将资料和要求一并交给模型。", "Choose a model for your context and budget, and provide the relevant material alongside the request."), ("先用真实任务验证输出，再调整提示词和应用侧的处理逻辑。", "Evaluate on real tasks, then refine prompts and your application logic.")],
        "speech": [("将文章、课程或产品文本变成可试听的声音内容。", "Turn articles, lessons or product text into spoken content."), ("短文本可从同步接口开始，长流程再按异步文档设计任务处理。", "Start with synchronous speech for short text; use the asynchronous documentation for task-based workflows."), ("通过 voice_setting.voice_id 选择你可调用的音色。", "Use voice_setting.voice_id to select a voice available to your account."), ("把文稿、音色选择和结果验收串联进现有内容生产流程。", "Connect script preparation, voice selection and review to your content process.")],
        "video": [("从文字镜头描述开始，也可按文档提供首帧或尾帧。", "Begin with a written shot description, or provide first and last frames as documented."), ("支持图片、视频和音频作为参考；参考模式与首尾帧模式不能混用。", "Use image, video and audio references; reference mode cannot be mixed with first/last-frame mode."), ("按用途选择 768P 或 2K，MiniMax-H3 支持 4–15 秒时长。", "Choose 768P or 2K for your workflow. MiniMax-H3 supports a duration of 4–15 seconds."), ("生成带原生立体声音频的视频，适合需要画面与声音一起表达的片段。", "Generate video with native stereo audio for clips that need visuals and sound together.")],
        "voice-design": [("用文字写出声音的音色、表达方式和角色设定。", "Describe the voice, delivery and character in plain language."), ("准备 preview_text，让声音原型有一致的试听文本。", "Supply preview_text so voice prototypes use a consistent sample script."), ("用自定义唯一 voice_id 标识设计，方便后续核对接入结果。", "Choose a unique custom voice_id to identify the design and verify the integration result."), ("返回字段在文档正文与示例中不一致，应用应先确认实际响应格式。", "The documentation and example disagree on result fields; confirm the actual response before integrating it.")],
        "overview": [("M 系列面向对话、编程、工具调用与资料处理。", "M-series models support conversation, coding, tool workflows and working with documents."), ("H3 支持 4–15 秒、768P/2K 视频和原生立体声音频。", "H3 supports 4–15-second video at 768P or 2K with native stereo audio."), ("六个 Speech 型号覆盖 2.8、2.6 与 02 版本的 HD/Turbo 选择。", "Six Speech models cover HD and Turbo variants across versions 2.8, 2.6 and 02."), ("Voice Design 从文字描述开始构建音色原型。", "Voice Design starts with a text description to create a voice prototype."), ("鉴权与余额统一，按任务切换模型与接口。", "Use the same authentication and balance while choosing the model and endpoint for each task."), ("从国内网络直接调用 AnyAIGC API，并按用途配置超时和重试。", "Call AnyAIGC directly from mainland China and configure timeouts and retries for your workload.")],
    }[kind]
    body = ''.join(f'<article class="mm-feature"><span class="mm-number">{i:02d}</span><h3>{h(c)}</h3><p>{h(pick(lang, *descriptions[i-1]))}</p></article>' for i, c in enumerate(caps, 1))
    return section("capabilities", pick(lang, "能力", "CAPABILITIES"), pick(lang, f"{model["name"]} 可以做什么" if model else "一组模型，覆盖从想法到作品", "From a prompt to a finished experience"), pick(lang, "把模型能力放进产品、工作流和创作工具。", "Put the model capability into your product, workflow or creative tool."), f'<div class="mm-feature-grid">{body}</div>')


def money(amount):
    return format(amount, "f").rstrip("0").rstrip(".") if "." in format(amount, "f") else format(amount, "f")


def cost_examples(lang, model):
    selections = [model] if model else [MODEL_BY_SLUG[x] for x in ("minimax-m3.1-flash", "minimax-h3", "speech-2.8-turbo")]
    cards = []
    for item in selections:
        kind = item["kind"]
        rates = item["prices"]
        multiples = [1, 10] if model else [1]
        for n in multiples:
            if kind == "chat":
                a, b = Decimal(rates[0]["amount"]), Decimal(rates[1]["amount"])
                cost = (a + Decimal("0.25") * b) * n
                title = pick(lang, f"{n}M 输入 + {Decimal('0.25') * n}M 输出", f"{n}M input + {Decimal('0.25') * n}M output")
                calc = f"{n} × ${rates[0]['amount']} + {Decimal('0.25') * n} × ${rates[1]['amount']}"
                note = pick(lang, "按多次请求累计用量估算，不含缓存。", "An aggregate across multiple requests, excluding cache charges.")
                if item["id"] == "MiniMax-M3":
                    note += pick(lang, "每次请求输入均不超过 512K，采用第一档价格。", " Every request stays at or below 512K input tokens and uses tier one.")
            elif kind == "video":
                seconds = 5 if n == 1 else 10
                cost = Decimal(rates[0]["amount"]) * seconds
                title = pick(lang, f"{seconds} 秒 768P 视频", f"{seconds}-second 768P video")
                calc = f"{seconds} × ${rates[0]['amount']}"
                note = pick(lang, "纯文生视频，无图片、视频或音频参考，不含再生成。", "Text-only generation with no image, video or audio references and no regeneration.")
            else:
                cost = Decimal(rates[0]["amount"]) * n
                title = pick(lang, f"{n} 万字符", f"{n * 10000:,} characters")
                calc = f"{n} × ${rates[0]['amount']}"
                note = pick(lang, "按标示字符单价估算，不含可能产生的自定义音色费用。", "Estimated at the listed character rate, excluding any custom voice fee.")
                if kind == "voice-design":
                    note = pick(lang, "仅按模型广场标示的字符单价演算，实际计费文本范围需确认。", "Illustrates the listed character rate only; the text included in billing still needs confirmation.")
            cards.append(f'<article class="mm-cost"><h3>{h(item["name"])} · {h(title)}</h3><p><code>{h(calc)}</code></p><strong>${money(cost)}</strong><p>{h(note)}</p></article>')
    return '<div class="mm-cost-grid">' + ''.join(cards) + '</div>'


def pricing(lang, model):
    rows = []
    source = [model] if model else MODELS
    for item in source:
        discount = savings_label(lang, item)
        badge = f' <span class="mm-price-saving">{h(discount)}</span>' if discount else ""
        rows.append(f'<tbody><tr class="mm-group"><th colspan="3">{h(item["name"])}{badge}</th></tr>')
        for p in item["prices"]:
            label = price_label(lang, item, p)
            price_text = pick(lang, "免费", "Free") if Decimal(p["amount"]) == 0 else "$" + p["amount"]
            rows.append(f'<tr><th scope="row">{h(label)}</th><td><code>{h(item["id"])}</code><small>{h(item["category_" + lang])}</small></td><td><strong>{h(price_text)}</strong> / {h(p["unit_" + lang])}</td></tr>')
        rows.append('</tbody>')
    if not rows:
        rows.append('<tr><td colspan="3">—</td></tr>')
    billing = f'<ul class="mm-billing"><li><strong>{pick(lang, "按用量计费", "Usage based")}</strong>{pick(lang, "不同模型使用 token、字符或秒作为单位。", "Units are tokens, characters or seconds depending on the model.")}</li><li><strong>{pick(lang, "并发不限", "Unlimited concurrency")}</strong>{pick(lang, "应用侧请设置合理超时与重试。", "Set timeouts and retries in your application.")}</li><li><strong>{pick(lang, "余额通用", "Shared balance")}</strong>{pick(lang, "一个 Key 调用 300+ 模型。", "One key works across 300+ models.")}</li></ul>'
    note = pick(lang, "单位为 USD，按成功提交计费，实时价格以模型广场为准。", "Prices are in USD, charged on successful submission. Current prices are shown in the model catalog.")
    if not model or model["kind"] in ("speech", "voice-design"):
        note += pick(lang, "语音按万字符列示，非预设音色可能另计音色费用。Voice Design 的实际计费文本范围请在批量调用前确认。", " Speech is listed per 10,000 characters; non-preset voices may incur a separate voice fee. Confirm which text is billable for Voice Design before batch use.")
    output = pick(lang, "一次调用的产出随端点而异：对话回复、视频任务、语音数据或音色设计响应。", "One call yields a chat response, video task, speech data or voice-design response, depending on the endpoint.")
    if model:
        output = model["output_" + lang]
        if model["kind"] == "voice-design":
            output = pick(lang, "一次调用返回音色设计响应；字段结构需以实际接口确认为准。", "One call returns a voice-design response; confirm its field structure against the live interface.")
    discount = savings_label(lang, model)
    savings = (f'<div class="mm-savings"><strong>{h(discount)}</strong><p>{h(savings_detail(lang, model))} '
               f'<a href="{h(PRICING_URL)}">{pick(lang, "查看折扣", "View savings")} ↗</a></p></div>') if discount else ""
    body = savings + billing + f'<div class="mm-table-wrap"><table class="mm-table"><caption>{h(pick(lang, "API 价格表", "API price table"))}</caption><thead><tr><th>{h(pick(lang, "功能", "Operation"))}</th><th>{h(pick(lang, "模型名", "Model"))}</th><th>{h(pick(lang, "单价（USD）", "Unit price (USD)"))}</th></tr></thead>{"".join(rows)}</table></div><p class="mm-note">{h(note)} {h(output)}</p>'
    body += cost_examples(lang, model) + '<div class="mm-actions">' + button(pick(lang, "获取 API Key", "Get an API key"), REG) + f'<a href="{h(PRICING_URL)}">{pick(lang, "在模型广场查看", "View in the model catalog")} ↗</a></div>'
    return section("pricing", pick(lang, "价格", "PRICING"), pick(lang, f"{model["name"]} API 价格" if model else "MiniMax API 价格", "MiniMax API pricing"), pick(lang, "按模型广场当前价格展示，单位和计费逻辑写在每一行。", "Current catalog rates with the billing unit shown on every row."), body, soft=True)


def quickstart(lang, model):
    item = model or MODELS[0]
    kind = item["kind"]
    example_kind = {"chat": "text", "video": "video", "speech": "speech", "voice-design": "design"}[kind]
    tabs = examples(lang, item["id"], example_kind)
    panels = []
    buttons = []
    for i, (label, code) in enumerate(tabs):
        pid = f"mm-code-{example_kind}-{i}"
        buttons.append(f'<button type="button" data-panel="{pid}" aria-selected="{"true" if i == 0 else "false"}">{label}</button>')
        panels.append(f'<div class="mm-code-panel" id="{pid}"{"" if i == 0 else " hidden"}><div class="mm-code-head"><span>{label}</span><button class="mm-copy" type="button" data-copy="{pid}-source">{pick(lang, "复制", "Copy")}</button></div><pre><code id="{pid}-source">{h(code)}</code></pre></div>')
    steps = ''.join(f'<li><b>{i:02d}</b><span>{h(t)}</span></li>' for i, t in enumerate([pick(lang, "注册 AnyAIGC 并创建 API Key。", "Sign up and create an API key."), pick(lang, "将 API Key 放进 ANYAIGC_API_KEY 环境变量。", "Set the ANYAIGC_API_KEY environment variable."), pick(lang, f"按文档使用 {item["id"]} 发起请求。", f"Send a request with {item["id"]} using the docs.")], 1))
    endpoints = ''.join(f'<li><code>{h(e)}</code></li>' for e in item["endpoints"])
    api_info = (f'<div class="mm-api-info"><ul class="mm-endpoints" aria-label="{pick(lang, "API 接口", "API endpoints")}">{endpoints}</ul>'
                f'<a class="mm-doc-link" href="{h(doc_url(lang, item["doc"]))}">{pick(lang, "阅读对应 API 文档", "Read the API reference")} ↗</a></div>')
    body = f'<ol class="mm-steps">{steps}</ol>{api_info}<div class="mm-code-tabs">{"".join(buttons)}</div>{"".join(panels)}'
    if kind == "voice-design":
        body += f'<p class="mm-note">{pick(lang, "文档正文称返回 voice_id，响应示例却显示 data.task_id。示例仅打印完整 JSON，不假定返回字段；实际响应和计费文本范围请在正式接入前确认。", "The documentation describes voice_id, while its response example shows data.task_id. These examples print the full JSON without assuming a result field. Confirm the actual response and billable text before integration.")}</p>'
    elif kind == "speech":
        body += f'<p class="mm-note">{pick(lang, "MINIMAX_VOICE_ID 应设置为你可使用的音色 ID。此处展示同步请求；异步接口的完整参数、查询与下载流程请以当前文档为准。", "Set MINIMAX_VOICE_ID to a voice available to your account. The example uses synchronous synthesis; follow the current documentation for asynchronous parameters, retrieval and downloads.")}</p>'
    elif kind == "video":
        body += f'<p class="mm-note">{pick(lang, "创建请求返回 task_id；本示例仅提交任务，不等待视频生成完成。", "Creation returns task_id. This example submits the task and does not wait for the finished video.")} <a href="{h(doc_url(lang, "https://docs.anyaigc.ai/reference/v1/minimax/v2/query/video_generation/%7Btask_id%7D?leaf=c%3A1791792620386"))}">{pick(lang, "查看任务查询文档", "See task-query documentation")} ↗</a></p>'
    return section("quickstart", pick(lang, "快速开始", "QUICKSTART"), pick(lang, f"接入 {item["name"]} API" if model else "三步开始调用 MiniMax", "Three steps to your first request"), pick(lang, "从最小请求开始，再把返回结果接入你的产品。", "Start with the smallest request, then connect the response to your product."), body)


def uses_section(lang, model):
    kind = model["kind"] if model else "overview"
    scenes = {
        "chat": [("开发助手", "Developer assistance", "把需求拆成实现步骤，生成代码草稿、说明与测试思路，再在自己的环境中验证。", "Break down requirements, draft code and explanations, and develop test ideas to validate in your own environment."),
                 ("资料与知识工作", "Research and knowledge work", "围绕给定资料做摘要、信息整理与问答，把模型回复接到已有知识流程中。", "Summarize, organize and ask questions about supplied material, then use the responses in an existing knowledge workflow."),
                 ("业务工作流", "Business workflows", "将请求分类、结构化草稿与工具执行组合起来，应用负责权限控制和结果检查。", "Combine request classification, structured drafts and tool execution, with permissions and result checks handled by your application.")],
        "video": [("分镜预演", "Shot exploration", "用镜头运动和场景描述生成短片段，先查看构图、节奏与声音的整体表现。", "Generate short clips from scene and camera descriptions to review composition, pacing and sound."),
                  ("参考素材创作", "Reference-led production", "结合有权使用的图片、视频或音频素材探索新镜头，并选择合适的参考模式。", "Explore new shots with image, video or audio references you are authorized to use, choosing the appropriate reference mode."),
                  ("短视频素材", "Short-form assets", "按目标展示场景选择画幅与 768P/2K 分辨率，将生成结果交给后续剪辑流程。", "Choose an aspect ratio and 768P or 2K resolution for your destination, then bring the generated clip into editing.")],
        "speech": [("有声书与长文", "Audiobooks and articles", "把文稿转成语音段落，使用一致的音色并逐段校对发音与节奏。", "Turn manuscripts into spoken sections, keeping a consistent voice and reviewing pronunciation and pacing."),
                   ("课程与讲解", "Lessons and explainers", "为教学内容、产品介绍或操作说明制作配音，随文字更新重复合成。", "Narrate educational material, product introductions or instructions, and regenerate speech when the script changes."),
                   ("应用语音交互", "Speech in applications", "把可用音色接入产品提示、助手回复和数字人配音等场景。", "Use available voices for product prompts, assistant responses and digital-human narration.")],
        "voice-design": [("角色声音原型", "Character voice prototypes", "先用文字定义角色的声音方向，再用一致试听文本比较不同设计。", "Describe the direction of a character voice, then compare designs with a consistent sample script."),
                         ("品牌声音探索", "Brand voice exploration", "把产品气质写成明确的音色描述，交由内容团队试听和选择。", "Translate a product's tone into a specific voice description for the content team to review."),
                         ("配音流程准备", "Narration preparation", "规划唯一 voice_id 与素材验收流程，确认响应后再衔接语音合成。", "Plan unique voice IDs and review steps, confirm the API response, then connect the result to speech synthesis.")],
        "overview": [("智能应用", "Intelligent applications", "用 M 系列处理对话、代码与工具工作流，将模型能力接入已有产品。", "Use M-series models for conversation, code and tool workflows inside your product."),
                     ("视频创作", "Video production", "用 H3 探索镜头、参考素材与音画片段，为后续剪辑准备内容。", "Explore shots, references and audiovisual clips with H3 before moving into editing."),
                     ("声音内容", "Spoken content", "用 Speech 制作配音，用 Voice Design 探索适合角色或品牌的声音。", "Produce narration with Speech and explore a character or brand voice with Voice Design.")],
    }[kind]
    cards = ''.join(f'<article class="mm-feature"><span class="mm-number">0{i}</span><h3>{h(pick(lang, a, b))}</h3><p>{h(pick(lang, c, d))}</p></article>' for i, (a, b, c, d) in enumerate(scenes, 1))
    return section("use-cases", pick(lang, "使用场景", "USE CASES"), pick(lang, "从一个具体任务开始", "Start with a concrete task"), pick(lang, "先选适合的模型与输入，再把结果带进你的工作流程。", "Choose the model and input for the job, then bring the output into your workflow."), f'<div class="mm-feature-grid">{cards}</div>')


def platform_section(lang):
    items = [("300+ 模型，一个 Key", "300+ models, one key", "统一 API Key 与账户余额，按任务切换对话、图像、视频和语音模型。", "Use one API key and account balance while choosing chat, image, video and speech models for each task."),
             ("国内直连，按需调用", "Direct access, on demand", "通过 AnyAIGC 域名从国内直接调用；MiniMax 接入并发不限，不设固定 RPM 上限。", "Connect directly through the AnyAIGC domain from mainland China. MiniMax access has unlimited concurrency and no fixed RPM cap."),
             ("单价明确，用量可查", "Clear rates and usage", "按价格表对应的 token、字符或秒计费，在控制台查看调用与扣费明细。", "Pay the listed token, character or second rate and inspect usage and charges in the console.")]
    cards = ''.join(f'<article class="mm-feature"><span class="mm-number">0{i}</span><h3>{h(pick(lang, a, b))}</h3><p>{h(pick(lang, c, d))}</p></article>' for i, (a, b, c, d) in enumerate(items, 1))
    return section("platform", "AnyAIGC", pick(lang, "让模型接入更简单", "Keep integration straightforward"), pick(lang, "把鉴权、余额和账单集中在一个平台，专注自己的应用。", "Keep authentication, balance and billing in one place so you can focus on the application."), f'<div class="mm-feature-grid">{cards}</div>', soft=True)


def enterprise_section(lang, name):
    cards = [(pick(lang, "增值税发票", "Invoices"), pick(lang, "普票、专票都能开", "Including VAT general and special invoices"), pick(lang, "按实际充值金额开具，方便企业报销和抵扣。", "Issued for actual top-ups to support company expense and tax processes.")), (pick(lang, "对公转账", "Bank transfer"), pick(lang, "公司账户直接付款", "Pay from a company account"), pick(lang, "支持企业对公转账充值。", "Top up by corporate bank transfer.")), (pick(lang, "签订合同", "Contracts"), pick(lang, "满足采购与法务流程", "Fits procurement and legal review"), pick(lang, "可与 AnyAIGC 签订服务合同。", "Sign a service agreement with AnyAIGC.")), (pick(lang, "专属对接", "Dedicated support"), pick(lang, "客服与技术支持", "Account and technical contact"), pick(lang, "提供专属客服和技术对接。", "Work with a dedicated support contact and technical contact."))]
    body = ''.join(f'<article><span class="mm-number">{i:02d}</span><h3>{h(t)}</h3><p><strong>{h(sub)}</strong><br>{h(d)}</p></article>' for i, (t, sub, d) in enumerate(cards, 1))
    pay = payments.pay_row(lang, "mm").strip()
    return section("enterprise", pick(lang, "企业接入", "ENTERPRISE"), pick(lang, f"企业接入 {name} API", f"{name} API for teams and enterprises"), pick(lang, "研发、财务、法务和采购可以一起完成接入。", "Engineering, finance, legal and procurement can move together."), f'<div class="mm-enterprise-grid">{body}</div>{pay}<div class="mm-actions">{button(pick(lang, "联系企业客服", "Talk to sales"), SUPPORT)} {button(pick(lang, "先注册试用", "Start with a free account"), REG, True)}</div>', soft=True)


def trust_section(lang):
    # Reuse the verified trust copy, translated by trust.py, but in MiniMax's layout.
    items = trust.ITEMS[lang]
    body = ''.join(f'<li class="mm-trust-item"><h3>{h(t)}</h3><p>{d}</p></li>' for t, d in items)
    return section("trust", pick(lang, "信任与保障", "TRUST"), trust.HEAD[lang][0], trust.HEAD[lang][1], f'<ul class="trust-list">{body}</ul><div class="mm-actions">{button(pick(lang, "先注册领取 200 万 tokens", "Sign up for 2M free tokens"), REG)}</div>')


def family(lang, slug):
    current = 'aria-current="page"' if slug == "minimax" else ""
    links = [f'<a href="/{lang}/models/minimax" {current}><span>MiniMax API</span><small>{pick(lang, "全系总览", "Overview")}</small></a>']
    for item in MODELS:
        current = 'aria-current="page"' if item["slug"] == slug else ""
        links.append(f'<a href="/{lang}/models/{item["slug"]}" {current}><span>{h(item["name"])}</span><small>{h(item["id"])}</small></a>')
    return section("family", pick(lang, "同系列模型", "FAMILY"), pick(lang, "MiniMax 全系模型", "All MiniMax models"), pick(lang, "按任务选择对话、视频、语音和音色设计模型。", "Choose a chat, video, speech or voice-design model for your task."), f'<div class="mm-family">{"".join(links)}</div>')


def faq_section(lang, faqs):
    body = '<div class="mm-faq">' + ''.join(f'<details><summary><h3>{h(q)}</h3></summary><div class="mm-answer"><p>{h(a)}</p></div></details>' for q, a in faqs) + '</div>'
    return section("faq", pick(lang, "常见问题", "FAQ"), pick(lang, "MiniMax API 常见问题", "MiniMax API FAQ"), pick(lang, "价格、接口、结果和企业接入，一次说明白。", "Pricing, endpoints, results and enterprise access in one place."), body)


def final(lang, slug):
    other = "en" if lang == "zh" else "zh"
    return f'''<section class="mm-final" aria-labelledby="final-title"><div class="mm-wrap">{logo("final")}<h2 id="final-title">{h(pick(lang, "把 MiniMax 接入你的下一次创作。", "Put MiniMax into your next build."))}</h2><p>{h(pick(lang, "注册 AnyAIGC，使用一个 API Key 调用 300+ 模型。", "Sign up for AnyAIGC and call 300+ models with one API key."))}</p><div class="mm-actions">{button(pick(lang, "获取 API Key", "Get an API key"), REG)} {button(pick(lang, "查看模型广场", "Open the model catalog"), PRICING_URL, True)}</div><ul class="mm-final-links"><li><a href="/{lang}/models/">{h(pick(lang, "全部模型专题", "All model guides"))}</a></li><li><a href="/{other}/models/{slug}" hreflang="{pick(other, "zh-CN", "en")}">{h(pick(lang, "English 版本", "中文版"))}</a></li><li><a href="{SUPPORT}">{h(pick(lang, "联系客服", "Contact support"))}</a></li></ul></div></section></main>\n<footer class="mm-footer"><div class="mm-wrap"><a class="mm-brand" href="/">AnyAIGC<span>× MiniMax</span></a><nav aria-label="{h(pick(lang, "页脚", "Footer"))}"><a href="/{lang}/models/">{h(pick(lang, "模型专题", "Model guides"))}</a><a href="{PRICING_URL}">{h(pick(lang, "模型广场", "Model catalog"))}</a><a href="https://anyaigc.ai/console">{h(pick(lang, "控制台", "Console"))}</a><a href="/privacy">{h(pick(lang, "隐私政策", "Privacy"))}</a><a href="/terms">{h(pick(lang, "服务条款", "Terms"))}</a></nav><p class="mm-legal">{h(pick(lang, "MiniMax 是 MiniMax 的商标。AnyAIGC 是独立 API 服务商，与 MiniMax 无隶属关系。模型许可与商用条款以 MiniMax 官方条款为准。", "MiniMax is a trademark of MiniMax. AnyAIGC is an independent API provider and is not affiliated with MiniMax. Model licenses and commercial terms are governed by MiniMax's official terms."))}</p></div></footer>\n'''


def render(lang, slug):
    model = MODEL_BY_SLUG.get(slug) if slug != "minimax" else None
    faqs = faq_items(lang, model)
    content = head(lang, slug, model, faqs) + nav(lang, slug, model or MODELS[0]) + hero(lang, slug, model)
    if model is None:
        content += section("models", pick(lang, "模型阵容", "MODELS"), "MiniMax", pick(lang, "12 个模型，覆盖对话、视频和语音。", "12 models across chat, video and speech."), f'<div class="mm-model-grid">{model_grid(lang, slug)}</div>')
    content += capabilities(lang, model) + pricing(lang, model) + uses_section(lang, model) + platform_section(lang) + quickstart(lang, model) + enterprise_section(lang, (model["name"] if model else "MiniMax")) + trust_section(lang) + family(lang, slug) + faq_section(lang, faqs) + final(lang, slug)
    docs = doc_url(lang, (model or MODELS[0])["doc"])
    content = content.replace('<ul class="mm-final-links">', f'<ul class="mm-final-links"><li><a href="{h(docs)}">{pick(lang, "API 文档", "API documentation")}</a></li>', 1)
    return content + '<script src="/assets/models/minimax.js?v=' + VER + '" defer></script>\n</body>\n</html>\n'


def main():
    for lang in ("zh", "en"):
        out = ROOT / lang / "models"
        for slug in ["minimax"] + [m["slug"] for m in MODELS]:
            (out / f"{slug}.html").write_text(render(lang, slug), encoding="utf-8", newline="\n")
            print(lang, slug)


if __name__ == "__main__":
    main()
