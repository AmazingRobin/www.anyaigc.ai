"""Build the 10 static Xiaomi MiMo topic pages: python scripts/mimo_pages.py

Overview /<lang>/models/mimo plus one guide per catalog model. Facts and prices
live in mimo_data.py; official media is prepared by mimo_assets.py.
"""

from decimal import Decimal
from html import escape, unescape
from pathlib import Path
import json
import re

from mimo_data import (MODELS, MODEL_BY_SLUG, SLUGS, CHECKED_DATE, PRICING_URL,
  OFFICIAL_PRICE_URL, DEPRECATE_URL, DOC_CHAT, LABEL, ratio, deal)
import payments
import trust

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.anyaigc.ai"
REG = "https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9"
SUPPORT = "https://anyaigc.ai/customersupport"
CONSOLE = "https://anyaigc.ai/console"
VER = "20261109c"
MEDIA = "/assets/models/mimo/"
LOGO = (ROOT / "assets/icons/xiaomimimo.svg").read_text(encoding="utf-8")
PRO = MODEL_BY_SLUG["mimo-v2.6-pro"]
FLASH = MODEL_BY_SLUG["mimo-v2.6-flash"]


def pick(lang, zh, en):
    return zh if lang == "zh" else en


def h(value):
    return escape(str(value), quote=True)


def txt(value):
    return unescape(re.sub(r"<[^>]+>", "", value))


def url(lang, slug):
    return f"{SITE}/{lang}/models/{slug}"


def doc(lang):
    return DOC_CHAT if lang == "zh" else DOC_CHAT.replace("https://docs.anyaigc.ai/", "https://docs.anyaigc.ai/en/", 1)


def money(value):
    text = format(Decimal(value).normalize(), "f")
    return text


def usd(value):
    """Dollar total without rounding, padded to at least two decimals."""
    whole, _, frac = money(value).partition(".")
    return whole + "." + frac.ljust(2, "0")


def mark(fill="#1a1a1a", cls="mi-mark", size=28):
    body = re.search(r"<svg[^>]*>(.*)</svg>", LOGO, re.S).group(1)
    body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="{size}" height="{size}" fill="{fill}" '
     f'fill-rule="evenodd" aria-hidden="true" focusable="false">{body}</svg>')


def width(text):
    return sum(2 if ord(c) > 0x2E7F else 1 for c in text)


def label(lang, key):
    return pick(lang, *LABEL[key])


def price_of(model, key):
    return next(p for p in model["prices"] if p["key"] == key)


def unit(lang):
    return pick(lang, "百万 tokens", "1M tokens")


def button(text, href, kind="dark", arrow=True):
    tail = ' <span aria-hidden="true">→</span>' if arrow else ""
    return f'<a class="mi-btn mi-btn-{kind}" href="{h(href)}">{h(text)}{tail}</a>'


def section(sid, kicker, title, lead, body, tone=""):
    cls = f"mi-section {tone}".strip()
    lead_html = f'<p class="mi-lead">{lead}</p>' if lead else ""
    return (f'<section class="{cls}" id="{sid}" aria-labelledby="{sid}-title"><div class="mi-wrap">'
     f'<header class="mi-head"><p class="mi-kicker">{h(kicker)}</p>'
            f'<h2 id="{sid}-title">{h(title)}</h2>{lead_html}</header>\n{body}\n</div></section>\n')


# ---------------------------------------------------------------- metadata

def metadata(lang, model):
    if model is None:
        name = "Xiaomi MiMo"
        title = pick(lang, "小米 MiMo API 价格与接入｜官方4折，V2.6 Pro/Flash - AnyAIGC",
       "Xiaomi MiMo API Pricing | About 60% Off Official - AnyAIGC")
        desc = pick(lang,
      "小米 MiMo API 价格与接入：MiMo-V2.6-Pro、V2.6-Flash 约官方 4 折，输入 $0.0563/百万 tokens 起，1M 上下文、全模态输入，并发不限，支持对公转账、合同与增值税专票。",
      "Xiaomi MiMo API at about 60% off official pricing: MiMo-V2.6-Flash from $0.0563/1M input tokens, 1M context, unlimited concurrency, contracts and VAT invoices.")
    elif not model["legacy"]:
        name = model["name"]
        p, o = price_of(model, "input"), price_of(model, "output")
        title = pick(lang, f"{name} API 价格与接入｜官方4折，1M 上下文 - AnyAIGC",
       f"{name} API Pricing | About 60% Off Official - AnyAIGC")
        desc = pick(lang,
      f"{name} API 价格与接入：约官方 4 折，输入 ${p['amount']}/百万 tokens（官方 ${p['official']}），输出 ${o['amount']}，1M 上下文、全模态输入，并发不限，支持对公转账、合同与增值税专票。",
      f"{name} API at about 60% off official pricing: ${p['amount']}/1M input tokens (official ${p['official']}), 1M context, unlimited concurrency, VAT invoices.")
    else:
        name = model["name"]
        succ = MODEL_BY_SLUG[model["successor"]]
        p = price_of(model, "input")
        title = pick(lang, f"{name} API 价格与接入｜停用说明与迁移 - AnyAIGC",
       f"{name} API Pricing | Retirement & Migration - AnyAIGC")
        desc = pick(lang,
      f"{name} API 价格：输入 ${p['amount']}/百万 tokens。小米官方已于 2026-10-21 停用该型号，本页说明如何迁移到约官方 4 折的 {succ['name']}。并发不限，支持对公转账与增值税专票。",
      f"{name} API: ${p['amount']}/1M input tokens. Xiaomi retired it on 2026-10-21; move to {succ['name']} at about 60% off. Unlimited concurrency, VAT invoices.")
    assert (width(title) <= 64 if lang == "zh" else len(title) <= 65), (lang, title)
    assert (60 <= len(desc) <= 120 if lang == "zh" else 120 <= len(desc) <= 160), (lang, len(desc), desc)
    return name, title, desc


def keywords(lang, model):
    name = model["name"] if model else "MiMo"
    base = pick(lang,
         [f"{name} API", f"{name} API 价格", f"{name} API key", f"{name} API 企业", f"{name} API 发票", "小米 MiMo API", "MiMo API 官方4折"],
         [f"{name} API", f"{name} API pricing", f"{name} API key", f"{name} API for business", "Xiaomi MiMo API"])
    if model and model["legacy"]:
        base.append(pick(lang, f"{name} 停用", f"{name} deprecated"))
    return ",".join(base)


# ---------------------------------------------------------------- FAQ

def price_answer(lang, model):
    parts = []
    for p in model["prices"]:
        item = f'{label(lang, p["key"])} ${p["amount"]}'
        if p["official"]:
            item += pick(lang, f'（官方 ${p["official"]}）', f' (official ${p["official"]})')
        parts.append(item)
    joined = pick(lang, "；".join(parts), "; ".join(parts))
    if model["legacy"]:
        succ = MODEL_BY_SLUG[model["successor"]]
        sp = price_of(succ, "input")
        return pick(lang,
      f"按 token 计费，单位 USD/百万 tokens：{joined}。小米官方已停用该型号，没有现行官方价可对比；替代型号 {succ['name']} 输入 ${sp['amount']}，约官方 4 折。实时价格以模型广场为准。",
      f"Billed per token in USD per 1M tokens: {joined}. Xiaomi has retired this model, so there is no current official price to compare; its replacement {succ['name']} is ${sp['amount']} input, about 40% of the official price. See the catalog for current rates.")
    return pick(lang,
  f"按 token 计费，单位 USD/百万 tokens：{joined}。输入与输出约为小米 MiMo 开放平台美元按量价的 40%，即约官方 4 折。实时价格以模型广场为准。",
  f"Billed per token in USD per 1M tokens: {joined}. Input and output are about 40% of Xiaomi MiMo's official pay-as-you-go USD price, roughly 60% off. See the catalog for current rates.")


def common_faq(lang):
    return [
 (pick(lang, "并发和 RPM 有限制吗？", "Are there concurrency or RPM limits?"),
  pick(lang, "AnyAIGC 的 MiMo 接入并发不限，不设固定 RPM 上限，所有用户默认享有。长上下文和深度思考请求耗时更长，请在应用里设置合理的超时与重试。",
       "AnyAIGC offers MiMo with unlimited concurrency and no fixed RPM cap, for every account by default. Long-context and deep-thinking requests take longer, so set sensible timeouts and retries.")),
        (pick(lang, "生成内容可以商用吗？", "Can I use the output commercially?"),
  pick(lang, "模型与输出的使用条款以小米 MiMo 官方条款为准。AnyAIGC 是独立 API 服务商，与小米无隶属关系。",
       "Use of the models and their output is governed by Xiaomi MiMo's official terms. AnyAIGC is an independent API provider and is not affiliated with Xiaomi.")),
    ]


def model_faq(lang, model):
    name = model["name"]
    endpoint = pick(lang,
      f"使用 OpenAI 兼容的 POST https://anyaigc.ai/v1/chat/completions，请求头 Authorization: Bearer <API Key>，model 填 {model['id']}。已有 OpenAI SDK 项目只需改 base_url 为 https://anyaigc.ai/v1。",
      f"Use the OpenAI-compatible POST https://anyaigc.ai/v1/chat/completions with Authorization: Bearer <API Key> and model set to {model['id']}. Existing OpenAI SDK projects only need base_url set to https://anyaigc.ai/v1.")
    items = [(pick(lang, f"{name} API 多少钱？是官方 4 折吗？" if not model["legacy"] else f"{name} API 多少钱？",
     f"How much does the {name} API cost? Is it really 60% off?" if not model["legacy"] else f"How much does the {name} API cost?"),
       price_answer(lang, model))]
    if model["legacy"]:
        succ = MODEL_BY_SLUG[model["successor"]]
        items += [
            (pick(lang, f"{name} 停用了吗？", f"Has {name} been retired?"),
      pick(lang, f"是。小米官方自 2026-10-14 18:00（UTC+8）起把 {model['id']} 的请求路由到 {succ['id']}，2026-10-21 10:00 起旧模型名在官方平台失效。AnyAIGC 模型广场目前仍列出 {model['id']}，新项目建议直接使用 {succ['id']}。",
    f"Yes. From 2026-10-14 18:00 (UTC+8) Xiaomi routed {model['id']} requests to {succ['id']}, and the old name stopped working on Xiaomi's platform at 2026-10-21 10:00. The AnyAIGC catalog still lists {model['id']}; new projects should use {succ['id']}.")),
     (pick(lang, f"怎么迁移到 {succ['name']}？", f"How do I migrate to {succ['name']}?"),
      pick(lang, f"接口相同，把 model 改为 {succ['id']} 即可。" + ("官方说明 API 参数完全适配，且 V2.6-Pro 新增多模态理解。" if model["id"] == "mimo-v2.5-pro" else "官方说明 max_completion_tokens 默认值由 32768 变为 131072，需要固定输出上限时请显式传参。") + "思考模式下 temperature 与 top_p 固定为 1.0 与 0.95。",
    f"The endpoint is the same; change model to {succ['id']}. " + ("Xiaomi says the API parameters are fully compatible, and V2.6-Pro adds multimodal understanding." if model["id"] == "mimo-v2.5-pro" else "Xiaomi notes the max_completion_tokens default rises from 32768 to 131072, so pass it explicitly if you need a fixed cap.") + " In thinking mode, temperature and top_p are fixed at 1.0 and 0.95.")),
     (pick(lang, "应该使用哪个 API 接口？", "Which API endpoint should I use?"), endpoint),
 ]
    else:
        other = FLASH if model is PRO else PRO
        items += [
     (pick(lang, "支持哪些输入？上下文有多长？", "What inputs are supported, and how long is the context?"),
      pick(lang, "官方规格：输入支持文本、图像、视频、音频，输出为文本，上下文 1M tokens，最大输出 128K tokens。AnyAIGC 文档目前给出文本与 image_url 图像输入示例，音频、视频的传参方式请以 API 文档为准。",
    "Official specs: text, image, video and audio input with text output, a 1M-token context and up to 128K output tokens. The AnyAIGC docs currently show text and image_url examples; follow the API docs for audio and video input.")),
     (pick(lang, "应该使用哪个 API 接口？", "Which API endpoint should I use?"), endpoint),
     (pick(lang, f"{name} 和 {other['name']} 怎么选？", f"{name} or {other['name']}: which should I use?"),
      pick(lang, f"V2.6-Pro 面向长程、复杂的 Agent、编程与科研任务；V2.6-Flash 面向高频调用和规模化办公任务，价格约为 Pro 的三分之一。两者都是约官方 4 折，建议用自己的任务各测一轮。",
    "V2.6-Pro targets long-horizon agent, coding and research work; V2.6-Flash targets high-volume office workloads at about a third of Pro's price. Both are about 40% of the official price, so test each on your own tasks.")),
 ]
    return items + common_faq(lang)


def overview_faq(lang):
    return [
 (pick(lang, "小米 MiMo API 多少钱？官方 4 折怎么算？", "How much is the Xiaomi MiMo API, and how is the 60% discount calculated?"),
         pick(lang, "MiMo-V2.6-Pro 输入 $0.1749、输出 $0.3497（官方 $0.435、$0.87）；MiMo-V2.6-Flash 输入 $0.0563、输出 $0.1126（官方 $0.14、$0.28），单位 USD/百万 tokens，约为小米 MiMo 开放平台美元按量价的 40%。实时价格以模型广场为准。",
       "MiMo-V2.6-Pro is $0.1749 input and $0.3497 output (official $0.435 and $0.87); MiMo-V2.6-Flash is $0.0563 and $0.1126 (official $0.14 and $0.28), in USD per 1M tokens. You pay about 40% of Xiaomi MiMo's official pay-as-you-go USD price, that is, about 60% off. See the catalog for current rates.")),
        (pick(lang, "4 个 MiMo 模型怎么选？", "How do I choose among the four MiMo models?"),
         pick(lang, "复杂、长程的 Agent、编程与科研任务选 MiMo-V2.6-Pro；高频调用和规模化办公选 MiMo-V2.6-Flash。MiMo-V2.5-Pro 与 MiMo-V2.5 已被小米官方停用，新项目请使用 V2.6 系列。",
       "Choose MiMo-V2.6-Pro for complex, long-horizon agent, coding and research work, and MiMo-V2.6-Flash for high-volume office workloads. Xiaomi has retired MiMo-V2.5-Pro and MiMo-V2.5, so new projects should use V2.6.")),
        (pick(lang, "MiMo-V2.5 系列停用了吗？", "Has the MiMo-V2.5 series been retired?"),
         pick(lang, "是。小米官方于 2026-10-21 10:00（UTC+8）停用 mimo-v2.5-pro 和 mimo-v2.5，替代型号分别是 mimo-v2.6-pro 和 mimo-v2.6-flash。AnyAIGC 模型广场目前仍列出这两个型号，迁移只需修改 model 字段。",
"Yes. Xiaomi retired mimo-v2.5-pro and mimo-v2.5 at 2026-10-21 10:00 (UTC+8); the replacements are mimo-v2.6-pro and mimo-v2.6-flash. The AnyAIGC catalog still lists both, and migrating only means changing the model field.")),
 (pick(lang, "支持 OpenAI SDK 吗？用哪个接口？", "Does it work with the OpenAI SDK? Which endpoint?"),
  pick(lang, "支持。4 个模型都走 OpenAI 兼容的 POST https://anyaigc.ai/v1/chat/completions，鉴权用 Authorization: Bearer <API Key>。OpenAI SDK 只需把 base_url 设为 https://anyaigc.ai/v1。",
       "Yes. All four models use the OpenAI-compatible POST https://anyaigc.ai/v1/chat/completions with Authorization: Bearer <API Key>. With the OpenAI SDK, set base_url to https://anyaigc.ai/v1.")),
    ] + common_faq(lang)


def faq_items(lang, model):
    own = model_faq(lang, model) if model else overview_faq(lang)
    enterprise = [
        (pick(lang, "AnyAIGC 能开发票吗？支持增值税专票吗？", "Can AnyAIGC issue invoices, including VAT special invoices?"),
  pick(lang, "支持。可按实际充值金额开具增值税普通发票和增值税专用发票，联系企业客服办理即可。",
       "Yes. AnyAIGC issues invoices for actual top-ups, including Chinese VAT general and VAT special invoices. Contact enterprise support to arrange them.")),
 (pick(lang, "企业可以对公转账和签合同吗？", "Can my company pay by bank transfer and sign a contract?"),
  pick(lang, "可以。支持企业对公转账充值，可签订服务合同，并提供专属客服与技术对接。",
       "Yes. Companies can top up by corporate bank transfer, sign a service agreement, and work with dedicated support and a technical contact.")),
    ]
    items = own + enterprise + [(payments.Q[lang], payments.A[lang])] + trust.FAQ[lang]
    assert 10 <= len(items) <= 13, len(items)
    return items


# ---------------------------------------------------------------- head / nav

def head(lang, slug, model, faqs):
    name, title, desc = metadata(lang, model)
    me = url(lang, slug)
    image = f"{SITE}/assets/og/{slug}-{lang}.png"
    rows = [(m, p) for m in ([model] if model else MODELS) for p in m["prices"]]
    amounts = [Decimal(p["amount"]) for _, p in rows]
    offers = [{"@type": "Offer", "name": f'{m["id"]} {label(lang, p["key"])} / {unit(lang)}',
        "price": p["amount"], "priceCurrency": "USD", "url": me + "#pricing"} for m, p in rows]
    crumbs = [{"@type": "ListItem", "position": i, "name": n, "item": u}
       for i, (n, u) in enumerate(breadcrumb_items(lang, model), 1)]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": SITE + "/#org", "name": "AnyAIGC", "url": "https://anyaigc.ai", "logo": SITE + "/logo.webp"},
 {"@type": "WebSite", "@id": SITE + "/#website", "name": "AnyAIGC", "url": SITE + "/", "publisher": {"@id": SITE + "/#org"}},
        {"@type": "WebPage", "@id": me + "#webpage", "url": me, "name": title, "description": desc,
  "inLanguage": pick(lang, "zh-CN", "en"), "dateModified": CHECKED_DATE, "isPartOf": {"@id": SITE + "/#website"},
         "breadcrumb": {"@id": me + "#breadcrumb"}, "mainEntity": {"@id": me + "#product"}},
        {"@type": "BreadcrumbList", "@id": me + "#breadcrumb", "itemListElement": crumbs},
 {"@type": "Product", "@id": me + "#product", "name": name + " API (AnyAIGC)", "description": desc,
         "sku": model["id"] if model else "mimo", "image": image, "brand": {"@type": "Brand", "name": "Xiaomi MiMo"},
  "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": str(min(amounts)), "highPrice": str(max(amounts)),
      "offerCount": len(offers), "url": me + "#pricing", "offers": offers}},
        {"@type": "FAQPage", "@id": me + "#faq", "mainEntity": [
     {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
    ]}
    locale, alternate = ("zh_CN", "en_US") if lang == "zh" else ("en_US", "zh_CN")
    return f'''<!DOCTYPE html>
<html lang="{pick(lang, 'zh-CN', 'en')}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{h(title)}</title>
<meta name="description" content="{h(desc)}">
<meta name="keywords" content="{h(keywords(lang, model))}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#fcfaf8">
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
<link rel="stylesheet" href="/assets/models/mimo.css?v={VER}">
<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
'''


def breadcrumb_items(lang, model):
    items = [(pick(lang, "模型专题", "Model guides"), f"{SITE}/{lang}/models/"), ("Xiaomi MiMo", url(lang, "mimo"))]
    if model:
        items.append((model["name"], url(lang, model["slug"])))
    return items


def topbar(lang, model):
    if model and model["legacy"]:
        succ = MODEL_BY_SLUG[model["successor"]]
        text = pick(lang, f"小米官方已于 2026-10-21 停用 {model['id']}，替代型号 {succ['id']} 在 AnyAIGC 约官方 4 折。",
      f"Xiaomi retired {model['id']} on 2026-10-21. Its replacement {succ['id']} is about 60% off the official price on AnyAIGC.")
        link = (f"/{lang}/models/{succ['slug']}", pick(lang, "查看替代型号", "See the replacement"))
    else:
        text = pick(lang, "MiMo-V2.6-Pro / V2.6-Flash 约官方 4 折，新用户注册送 200 万 tokens。",
      "MiMo-V2.6-Pro and V2.6-Flash at about 60% off Xiaomi's list price. 2M free tokens for new accounts.")
        link = ("#pricing", pick(lang, "查看价格", "See pricing"))
    return (f'<div class="mi-bar"><p>{h(text)}{pick(lang, "", " ")}<a href="{h(link[0])}">{h(link[1])} <span aria-hidden="true">→</span></a></p></div>\n')


def nav(lang, slug):
    other = "en" if lang == "zh" else "zh"
    links = [(f"/{lang}/models/", pick(lang, "模型专题", "Model guides")),
      (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
      ("#pricing", pick(lang, "价格", "Pricing")),
      ("#enterprise", pick(lang, "企业接入", "Enterprise")),
      (doc(lang), pick(lang, "API 文档", "API docs"))]
    items = "".join(f'<li><a href="{h(href)}">{h(text)}</a></li>' for href, text in links)
    return (f'<a class="mi-skip" href="#main">{pick(lang, "跳到主要内容", "Skip to main content")}</a>\n'
     '<header class="mi-nav"><div class="mi-wrap mi-nav-inner">'
     f'<a class="mi-brand" href="/" aria-label="AnyAIGC">AnyAIGC</a><span class="mi-brand-x" aria-hidden="true">×</span>'
     f'<a class="mi-brand-mimo" href="/{lang}/models/mimo" aria-label="Xiaomi MiMo">{mark()}<span>Xiaomi MiMo</span></a>'
     f'<nav id="mi-navigation" aria-label="{pick(lang, "主导航", "Main navigation")}"><ul class="mi-nav-links">{items}</ul></nav>'
     '<ul class="mi-nav-actions">'
            f'<li><a href="/{other}/models/{slug}" hreflang="{pick(other, "zh-CN", "en")}">{pick(lang, "EN", "中文")}</a></li>'
     f'<li><a href="{CONSOLE}">{pick(lang, "登录", "Log in")}</a></li>'
     f'<li>{button(pick(lang, "注册", "Sign up"), REG, arrow=False)}</li></ul>'
     f'<button class="mi-menu" type="button" aria-controls="mi-navigation" aria-expanded="false" aria-label="{pick(lang, "打开导航菜单", "Open navigation menu")}"><span></span></button>'
     '</div></header>\n')


# ---------------------------------------------------------------- hero

def hero(lang, model):
    items = breadcrumb_items(lang, model)
    crumbs = "".join(f'<li><a href="{h(u.removeprefix(SITE))}">{h(n)}</a></li>' for n, u in items[:-1])
    crumbs += f'<li aria-current="page">{h(items[-1][0])}</li>'
    notice = ""
    if model is None:
        title = '<span class="mi-h1-main">Xiaomi MiMo API</span>'
        sub = pick(lang, "官方 4 折，接入 V2.6 全模态旗舰", "V2.6 omni-modal models at about 60% off")
        lead = pick(lang, "一个 AnyAIGC API Key 调用 MiMo-V2.6-Pro、V2.6-Flash 等 4 个模型，OpenAI 兼容接口，并发不限。V2.6-Flash 输入 <strong>$0.0563 / 百万 tokens</strong>（官方 $0.14）。",
      "Call MiMo-V2.6-Pro, V2.6-Flash and two earlier models with one AnyAIGC API key. The endpoint is OpenAI-compatible, and concurrency is unlimited. V2.6-Flash input is <strong>$0.0563 / 1M tokens</strong> (official $0.14).")
        dl = deal_chip(lang, FLASH, overview=True)
    else:
        title = f'<span class="mi-h1-main">{h(model["name"])} API</span>'
        sub = model["tagline_" + lang]
        p = price_of(model, "input")
        lead = h(model["desc_" + lang]) + pick(lang, f'输入 <strong>${p["amount"]} / 百万 tokens</strong>', f' Input is <strong>${p["amount"]} / 1M tokens</strong>')
        if p["official"]:
            lead += pick(lang, f'，官方 ${p["official"]}。', f' (Xiaomi list price: ${p["official"]}).')
        else:
            lead += pick(lang, "。", ".")
        dl = deal_chip(lang, model)
        if model["legacy"]:
            succ = MODEL_BY_SLUG[model["successor"]]
            notice = (f'<p class="mi-notice o-notice" role="note"><strong>{pick(lang, "官方已停用", "Retired by Xiaomi")}</strong>'
        + h(pick(lang, f"小米官方已于 2026-10-21 停用 {model['id']}，替代型号为 {succ['name']}（约官方 4 折）。",
          f"Xiaomi retired {model['id']} on 2026-10-21. The replacement is {succ['name']}, about 40% of the official price."))
        + pick(lang, "", " ") + f'<a href="/{lang}/models/{succ["slug"]}">{pick(lang, "查看", "View")} {h(succ["name"])} →</a></p>')
    facts = [pick(lang, "并发不限", "Unlimited concurrency"), pick(lang, "OpenAI 兼容", "OpenAI compatible"),
      pick(lang, "300+ 模型 · 一个 Key", "300+ models · one key"), pick(lang, "对公 · 专票", "Contracts · invoices"),
      pick(lang, "注册送 200 万 tokens", "2M free tokens")]
    return ('<main id="main">\n<section class="mi-hero" aria-labelledby="hero-title"><div class="mi-wrap">'
     f'<nav class="mi-crumbs" aria-label="{pick(lang, "面包屑", "Breadcrumb")}"><ol>{crumbs}</ol></nav>'
     f'{notice}<h1 id="hero-title">{title}<span class="mi-h1-sub">{h(sub)}</span></h1>{dl}'
     f'<p class="mi-hero-lead">{lead}</p><div class="mi-actions">'
     + button(pick(lang, "获取 API Key", "Get an API key"), REG)
     + button(pick(lang, "查看 API 价格", "See API pricing"), "#pricing", "line")
     + button(pick(lang, "API 文档", "API docs"), doc(lang), "line")
     + '</div><ul class="mi-facts">' + "".join(f"<li>{h(f)}</li>" for f in facts) + "</ul></div></section>\n")


def deal_chip(lang, model, overview=False):
    if model["legacy"]:
        return ""
    p = price_of(model, "input")
    scope = pick(lang, "V2.6-Flash 输入" if overview else "输入", "V2.6-Flash input" if overview else "Input")
    detail = pick(lang, f'{scope} ${p["amount"]} · 官方 ${p["official"]} / 百万 tokens', f'{scope} ${p["amount"]} · official ${p["official"]} / 1M tokens')
    return f'<a class="mi-deal" href="#pricing"><b>{h(deal(lang))}</b><span>{h(detail)}</span></a>'


def banner(lang, model):
    if model and model["legacy"]:
        version = model["short"].split(" ")[0]
        return (f'<div class="mi-wrap"><div class="mi-banner mi-banner-dots" aria-hidden="true"><span>{h(version)}</span>'
  f'<em>{h(pick(lang, "已由 V2.6 接替", "Succeeded by V2.6"))}</em></div></div>\n')
    alt = pick(lang, "小米 MiMo 官方 V2.6 网点动画", "Xiaomi MiMo's official V2.6 halftone animation")
    return (f'<div class="mi-wrap"><figure class="mi-banner">'
            f'<video muted loop playsinline preload="none" poster="{MEDIA}hero.webp" aria-label="{h(alt)}" data-autoplay>'
     f'<source src="{MEDIA}hero.mp4" type="video/mp4"></video>'
     f'<a class="mi-banner-pill" href="#{"models" if model is None else "specs"}">{h(pick(lang, "了解模型", "Explore the models"))}</a>'
     f'<button class="mi-play" type="button" data-video-toggle hidden>{h(pick(lang, "暂停动画", "Pause animation"))}</button>'
     '</figure></div>\n')


# ---------------------------------------------------------------- models / specs

def card_art(model):
    if model["card"]:
        return f'<img src="{MEDIA}{model["card"]}" width="885" height="441" loading="lazy" alt="">'
    return f'<div class="mi-card-art mi-art-{model["tier"]}" aria-hidden="true"><span>{h(model["name"])}</span></div>'


def model_card(lang, model):
    trio = "".join(f'<div><dt>{h(label(lang, p["key"]))}</dt><dd>${h(p["amount"])}</dd></div>' for p in model["prices"])
    tag = (f'<span class="mi-tag mi-tag-deal">{h(deal(lang))}</span>' if not model["legacy"]
    else f'<span class="mi-tag mi-tag-old">{h(pick(lang, "官方已停用", "Retired by Xiaomi"))}</span>')
    return (f'<article class="mi-model">{card_art(model)}<div class="mi-model-body">{tag}'
     f'<h3><a href="/{lang}/models/{model["slug"]}">{h(model["name"])}</a></h3><p>{h(model["desc_" + lang])}</p>'
     f'<dl class="mi-trio">{trio}</dl><p class="mi-unit">USD / {h(unit(lang))}</p></div></article>')


def models_section(lang):
    body = '<div class="mi-models">' + "".join(model_card(lang, m) for m in MODELS) + "</div>"
    return section("models", pick(lang, "模型阵容", "MODELS"), pick(lang, "MiMo 全系模型，一个 Key 全部接入", "The MiMo lineup, one key for all"),
     pick(lang, "V2.6 是小米 MiMo 当前的旗舰系列；V2.5 两个型号已被官方停用，页面保留价格与迁移说明。",
          "V2.6 is Xiaomi MiMo's current flagship series. The two V2.5 models are retired; their pages keep pricing and migration notes."),
     body)


def specs_section(lang, model):
    cells = "".join(f'<div><dt>{h(k)}</dt><dd>{h(v)}</dd></div>' for k, v in model["specs_" + lang])
    caps = "".join(f"<li>{h(c)}</li>" for c in model["caps_" + lang])
    note = pick(lang, "规格来自小米 MiMo 官方模型页。", "Specs from Xiaomi MiMo's official model page.")
    if model["legacy"]:
        note = pick(lang, "规格来自小米 MiMo 官方发布说明与下线公告。", "Specs from Xiaomi MiMo's release notes and retirement notice.")
    body = (f'<div class="mi-specs"><dl class="mi-spec-grid">{cells}</dl><div class="mi-caps"><h3>{pick(lang, "模型能力", "Capabilities")}</h3>'
     f'<ul>{caps}</ul></div></div><p class="mi-note">{h(note)}</p>')
    return section("specs", pick(lang, "模型规格", "SPECS"), pick(lang, f"{model['name']} 模型规格", f"{model['name']} specs"), "", body)


# ---------------------------------------------------------------- pricing

def cost(model, million_in, million_out, cached=Decimal(0)):
    p_in, p_out, p_cache = (Decimal(price_of(model, k)["amount"]) for k in ("input", "output", "cache"))
    total = (million_in - cached) * p_in + cached * p_cache + million_out * p_out
    official = None
    if not model["legacy"]:
        o_in, o_out, o_cache = (Decimal(price_of(model, k)["official"]) for k in ("input", "output", "cache"))
        official = (million_in - cached) * o_in + cached * o_cache + million_out * o_out
    return total, official


def cost_card(lang, model, million_in, million_out, cached=Decimal(0)):
    total, official = cost(model, million_in, million_out, cached)
    p = {k: price_of(model, k)["amount"] for k in ("input", "output", "cache")}
    if cached:
        heading = pick(lang, f"{money(million_in)}M 输入（{money(cached)}M 命中缓存）+ {money(million_out)}M 输出",
         f"{money(million_in)}M input ({money(cached)}M cached) + {money(million_out)}M output")
        calc = f"{money(million_in - cached)} × ${p['input']} + {money(cached)} × ${p['cache']} + {money(million_out)} × ${p['output']}"
    else:
        heading = pick(lang, f"{money(million_in)}M 输入 + {money(million_out)}M 输出", f"{money(million_in)}M input + {money(million_out)}M output")
        calc = f"{money(million_in)} × ${p['input']} + {money(million_out)} × ${p['output']}"
    compare = ""
    if official is not None:
        compare = f'<p class="mi-cost-official">{h(pick(lang, "官方同用量", "Same usage at official price"))} <s>${usd(official)}</s></p>'
    return (f'<article class="mi-cost"><h3>{h(model["name"])}</h3><p class="mi-cost-use">{h(heading)}</p>'
     f'<p><code>{h(calc)}</code></p><strong>${usd(total)}</strong>{compare}</article>')


def pricing_section(lang, model):
    source = [model] if model else MODELS
    rows = []
    for item in source:
        badge = (f' <span class="mi-tag mi-tag-deal">{h(deal(lang))}</span>' if not item["legacy"]
   else f' <span class="mi-tag mi-tag-old">{h(pick(lang, "官方已停用", "Retired by Xiaomi"))}</span>')
        rows.append(f'<tbody><tr class="mi-row-head"><th colspan="4" scope="rowgroup">{h(item["name"])}{badge}<code class="mi-row-id">{h(item["id"])}</code></th></tr>')
        for p in item["prices"]:
            official = f'<s>${h(p["official"])}</s>' if p["official"] else h(pick(lang, "已停用", "Retired"))
            rows.append(f'<tr><th scope="row">{h(label(lang, p["key"]))}</th><td><code>{h(item["id"])}</code></td>'
   f'<td class="mi-official">{official}</td><td><strong>${h(p["amount"])}</strong> / {h(unit(lang))}</td></tr>')
        rows.append("</tbody>")
    table = (f'<div class="mi-table-wrap"><table class="mi-table"><caption>{pick(lang, "MiMo API 价格表（USD）", "MiMo API price table (USD)")}</caption>'
      f'<thead><tr><th scope="col">{pick(lang, "计费项", "Item")}</th><th scope="col">{pick(lang, "模型名", "Model")}</th>'
      f'<th scope="col">{pick(lang, "小米官方价", "Xiaomi official")}</th><th scope="col">{pick(lang, "AnyAIGC 单价", "AnyAIGC price")}</th></tr></thead>'
      + "".join(rows) + "</table></div>")
    current = PRO if model is None else (model if not model["legacy"] else None)
    savings = ""
    if current:
        pi, po = price_of(current, "input"), price_of(current, "output")
        share = int((ratio(current) * 100).quantize(Decimal("1")))
        savings = (f'<div class="mi-savings"><strong>{h(deal(lang))}</strong><p>'
     + h(pick(lang, f"{current['name']} 输入 ${pi['amount']}、输出 ${po['amount']}，小米官方同项为 ${pi['official']}、${po['official']}，约为官方价的 {share}%。"
      + ("V2.6-Flash 同样约官方 4 折。" if model is None else ""),
 f"{current['name']} is ${pi['amount']} input and ${po['amount']} output, versus ${pi['official']} and ${po['official']} from Xiaomi — about {share}% of the official price."
      + (" V2.6-Flash is also about 40% of official." if model is None else "")))
     + pick(lang, "", " ") + f'<a href="{OFFICIAL_PRICE_URL}" rel="noopener">{pick(lang, "官方价格来源", "Official price source")} ↗</a></p></div>')
    billing = ('<ul class="mi-billing">'
        f'<li><strong>{pick(lang, "按 token 计费", "Per-token billing")}</strong>{pick(lang, "输入、输出、缓存命中分别计价。", "Input, output and cache hits are priced separately.")}</li>'
        f'<li><strong>{pick(lang, "并发不限", "Unlimited concurrency")}</strong>{pick(lang, "不设固定 RPM 上限，所有用户默认享有。", "No fixed RPM cap, for every account.")}</li>'
        f'<li><strong>{pick(lang, "余额通用", "Shared balance")}</strong>{pick(lang, "一个 Key 调用 300+ 模型，$1 起充。", "One key for 300+ models; top up from $1.")}</li></ul>')
    note = pick(lang, f"单位 USD/百万 tokens，按成功请求的实际 tokens 计费，实时价格以模型广场为准。小米官方价为其开放平台美元按量价（{CHECKED_DATE} 查询），仅作对比。",
         f"Prices are USD per 1M tokens, charged on the actual tokens of successful requests; see the model catalog for current rates. Xiaomi official prices are its pay-as-you-go USD list (checked {CHECKED_DATE}), shown for comparison.")
    if model is None:
        examples = [cost_card(lang, PRO, Decimal(1), Decimal("0.25")), cost_card(lang, FLASH, Decimal(1), Decimal("0.25")),
      cost_card(lang, FLASH, Decimal(10), Decimal("2.5"), Decimal(8))]
    else:
        examples = [cost_card(lang, model, Decimal(1), Decimal("0.25")), cost_card(lang, model, Decimal(10), Decimal("2.5")),
      cost_card(lang, model, Decimal(10), Decimal("2.5"), Decimal(8))]
    body = (savings + billing + table + f'<p class="mi-note">{h(note)}</p>'
     + f'<h3 class="mi-sub">{pick(lang, "成本示例", "Cost examples")}</h3><div class="mi-costs">{"".join(examples)}</div>'
            + '<div class="mi-actions mi-actions-left">' + button(pick(lang, "获取 API Key", "Get an API key"), REG)
     + f'<a class="mi-text-link" href="{PRICING_URL}">{pick(lang, "在模型广场查看", "View in the model catalog")} ↗</a></div>')
    title = pick(lang, f"{model['name']} API 价格" if model else "MiMo API 价格", f"{model['name']} API pricing" if model else "MiMo API pricing")
    lead = pick(lang, "直接对照小米官方价，每一项单价都写在表里。", "Every rate side by side with Xiaomi's official price.")
    if model and model["legacy"]:
        lead = pick(lang, "小米官方已停用该型号，下表为 AnyAIGC 当前单价。", "Xiaomi has retired this model; the table shows current AnyAIGC rates.")
        note = pick(lang, "单位 USD/百万 tokens，按成功请求的实际 tokens 计费，实时价格以模型广场为准。",
      "Prices are USD per 1M tokens, charged on the actual tokens of successful requests; see the model catalog for current rates.")
    return section("pricing", pick(lang, "价格", "PRICING"), title, lead, body, "mi-tone")


# ---------------------------------------------------------------- benchmarks / showcase

def bench_section(lang, model):
    if model is None or model is PRO:
        adv = [(pick(lang, "综合智能指数 46", "Intelligence Index 46"), pick(lang, "MiMo-V2.6-Pro 在 Artificial Analysis 综合智能指数上 46.32 分（小米官方数据）。", "MiMo-V2.6-Pro scores 46.32 on the Artificial Analysis Intelligence Index (Xiaomi's figure).")),
 (pick(lang, "原生全模态", "Native omni-modal"), pick(lang, "图像、视频、音频、文本联合输入与理解。", "Joint image, video, audio and text input and understanding.")),
        (pick(lang, "面向复杂任务", "Built for complex work"), pick(lang, "1M 上下文，适配多模态、多 Agent 协同任务。", "1M context for multimodal, multi-agent tasks.")),
        (pick(lang, "面向真实场景", "Real-world focus"), pick(lang, "重点优化代码、办公、设计、科研与网络安全。", "Tuned for coding, office, design, research and security."))]
    else:
        adv = [(pick(lang, "原生全模态", "Native omni-modal"), pick(lang, "图像、视频、音频、文本联合输入与理解。", "Joint image, video, audio and text input and understanding.")),
        (pick(lang, "Pareto 前沿", "On the Pareto frontier"), pick(lang, "官方称真实工作流体验接近主流 Pro 级模型，token 效率更高。", "Xiaomi reports Pro-class workflow results with better token efficiency.")),
 (pick(lang, "面向日常任务", "Everyday workloads"), pick(lang, "1M 上下文，适合多模态混合输入与多 Agent 协同。", "1M context for mixed multimodal input and multi-agent work.")),
        (pick(lang, "高频调用", "High-volume calls"), pick(lang, "输入 $0.0563 / 百万 tokens，适合规模化任务。", "$0.0563 per 1M input tokens for work at scale."))]
    cards = "".join(f'<article class="mi-adv"><span>{i:02d}</span><h3>{h(t)}</h3><p>{h(d)}</p></article>' for i, (t, d) in enumerate(adv, 1))
    second = ("aa-index.webp", 1600, 626, pick(lang, "Artificial Analysis 综合智能指数", "Artificial Analysis Intelligence Index"))
    if model is FLASH:
        second = ("pareto.webp", 1600, 805, pick(lang, "智能指数与单任务成本（Pareto 前沿）", "Intelligence vs. cost per task (Pareto frontier)"))
    figures = (f'<figure class="mi-figure mi-figure-tall"><img src="{MEDIA}bench-v26.webp" width="1023" height="1127" loading="lazy" '
 f'alt="{h(pick(lang, "MiMo-V2.6-Pro 与 V2.6-Flash 在编程、通用 Agent 与网络安全基准上的官方成绩", "Official MiMo-V2.6-Pro and V2.6-Flash scores on coding, general-agent and cyber benchmarks"))}">'
        f'<figcaption>{h(pick(lang, "编程、通用 Agent、网络安全基准。空心条为待评测占位；GDPVal 为 Elo，其余为百分比。图源：小米 MiMo 官方。", "Coding, general-agent and cyber benchmarks. Hollow bars are pending evaluations; GDPVal is Elo, the rest are percentages. Source: Xiaomi MiMo."))}</figcaption></figure>'
        f'<figure class="mi-figure"><img src="{MEDIA}{second[0]}" width="{second[1]}" height="{second[2]}" loading="lazy" alt="{h(second[3])}">'
 f'<figcaption>{h(second[3])}{h(pick(lang, "。图源：小米 MiMo V2.6 官方发布文。", ". Source: Xiaomi MiMo V2.6 release post."))}</figcaption></figure>')
    body = f'<div class="mi-advs">{cards}</div><div class="mi-figures">{figures}</div>'
    title = pick(lang, "模型优势与官方评测", "Strengths and official benchmarks")
    return section("benchmarks", pick(lang, "模型优势", "STRENGTHS"), title,
     pick(lang, "以下数据与图表来自小米 MiMo 官方，实际效果请用自己的任务验证。", "Figures and charts are Xiaomi MiMo's own; validate on your tasks."), body)


def showcase_section(lang, model):
    if model is FLASH:
        items = [("image", "demo-web.webp", 960, 540, pick(lang, "前端网页设计", "Front-end design"), pick(lang, "从需求描述生成完整的网页界面。", "Generate a complete web page from a brief.")),
   ("image", "demo-slides.webp", 960, 540, pick(lang, "PPT 演示文稿", "Slide decks"), pick(lang, "把资料整理成结构清晰的演示文稿。", "Turn source material into a structured deck.")),
   ("video", "demo-edit", 960, 540, pick(lang, "代码驱动视频", "Code-driven video"), pick(lang, "用代码完成短片剪辑与动画演示。", "Edit short videos and animations with code."))]
        lead = pick(lang, "来自小米 MiMo V2.6 系列官方发布示例。", "Examples from Xiaomi MiMo's V2.6 series release.")
    else:
        items = [("video", "demo-sim", 960, 540, pick(lang, "具身仿真", "Embodied simulation"), pick(lang, "多智能体协作搭建可交互的仿真场景。", "Agents collaborate to build an interactive simulation.")),
   ("video", "demo-edit", 960, 540, pick(lang, "代码驱动视频创作", "Code-driven video"), pick(lang, "把数学概念转成直观的动画短片。", "Turn mathematical ideas into clear animated shorts.")),
   ("image", "demo-game.webp", 960, 545, pick(lang, "3D 游戏开发", "3D game building"), pick(lang, "从图片、视频或文字拆解任务，生成可运行的交互世界。", "Plan from images, video or text and build a playable world."))]
        lead = pick(lang, "来自小米 MiMo V2.6 官方发布示例。", "Examples from Xiaomi MiMo's V2.6 release.")
    cards = []
    for kind, src, w, ht, title, desc in items:
        if kind == "video":
            media = (f'<video muted loop playsinline preload="none" poster="{MEDIA}{src}-poster.webp" width="{w}" height="{ht}" '
       f'aria-label="{h(title)}" data-autoplay><source src="{MEDIA}{src}.mp4" type="video/mp4"></video>')
        else:
            media = f'<img src="{MEDIA}{src}" width="{w}" height="{ht}" loading="lazy" alt="{h(title)}">'
        cards.append(f'<article class="mi-show">{media}<div><h3>{h(title)}</h3><p>{h(desc)}</p></div></article>')
    return section("showcase", pick(lang, "真实任务", "IN PRACTICE"), pick(lang, "真实任务中的表现", "How it performs on real tasks"), h(lead),
     f'<div class="mi-shows">{"".join(cards)}</div>')


def migration_section(lang, model):
    succ = MODEL_BY_SLUG[model["successor"]]
    sp, mp = price_of(succ, "input"), price_of(model, "input")
    steps = [(pick(lang, "2026-10-14 18:00（UTC+8）", "2026-10-14 18:00 (UTC+8)"), pick(lang, f"小米官方开始把 {model['id']} 的请求路由至 {succ['id']}，按新模型计价。", f"Xiaomi began routing {model['id']} requests to {succ['id']} at the new model's price.")),
      (pick(lang, "2026-10-21 10:00（UTC+8）", "2026-10-21 10:00 (UTC+8)"), pick(lang, f"{model['id']} 在小米官方平台正式下线，旧模型名报错。", f"{model['id']} was retired on Xiaomi's platform; the old name now returns an error.")),
      (pick(lang, "现在", "Now"), pick(lang, f"AnyAIGC 模型广场仍列出 {model['id']}；新项目建议改用 {succ['id']}。", f"The AnyAIGC catalog still lists {model['id']}; new projects should use {succ['id']}."))]
    timeline = "".join(f'<li><time>{h(t)}</time><p>{h(d)}</p></li>' for t, d in steps)
    if model["id"] == "mimo-v2.5-pro":
        diff = [(pick(lang, "API 参数", "API parameters"), pick(lang, "完全适配", "Fully compatible"), pick(lang, "完全适配", "Fully compatible")),
  (pick(lang, "输入模态", "Input"), pick(lang, "仅文本", "Text only"), pick(lang, "文本、图像、视频、音频", "Text, image, video, audio"))]
    else:
        diff = [("max_completion_tokens", pick(lang, "默认 32768", "Default 32768"), pick(lang, "默认 131072", "Default 131072")),
         (pick(lang, "输入模态", "Input"), pick(lang, "文本、图像、视频、音频", "Text, image, video, audio"), pick(lang, "文本、图像、视频、音频", "Text, image, video, audio"))]
    diff.append((pick(lang, "思考模式", "Thinking mode"), "—", pick(lang, "temperature 1.0、top_p 0.95 固定", "temperature 1.0 and top_p 0.95 fixed")))
    diff.append((pick(lang, "AnyAIGC 输入单价", "AnyAIGC input price"), f"${mp['amount']}", f"${sp['amount']}"))
    rows = "".join(f'<tr><th scope="row">{h(a)}</th><td>{h(b)}</td><td>{h(c)}</td></tr>' for a, b, c in diff)
    table = (f'<div class="mi-table-wrap"><table class="mi-table mi-table-diff"><thead><tr><th scope="col">{pick(lang, "差异项", "Difference")}</th>'
      f'<th scope="col"><code>{h(model["id"])}</code></th><th scope="col"><code>{h(succ["id"])}</code></th></tr></thead><tbody>{rows}</tbody></table></div>')
    save = int(((1 - Decimal(sp["amount"]) / Decimal(mp["amount"])) * 100).quantize(Decimal("1")))
    body = (f'<ol class="mi-timeline">{timeline}</ol>{table}'
     f'<div class="mi-savings"><strong>{h(pick(lang, "迁移即省", "Save by switching"))}</strong><p>'
     + h(pick(lang, f"迁移只需把 model 改为 {succ['id']}。在 AnyAIGC 上，{succ['name']} 输入 ${sp['amount']}，比 {model['name']} 的 ${mp['amount']} 低约 {save}%。",
       f"Change model to {succ['id']}. On AnyAIGC, {succ['name']} input is ${sp['amount']}, about {save}% less than {model['name']} (${mp['amount']})."))
     + pick(lang, "", " ") + f'<a href="{DEPRECATE_URL}" rel="noopener">{pick(lang, "官方下线公告", "Xiaomi retirement notice")} ↗</a></p></div>'
     + '<div class="mi-actions mi-actions-left">' + button(pick(lang, f"查看 {succ['name']}", f"View {succ['name']}"), f"/{lang}/models/{succ['slug']}") + "</div>")
    return section("migration", pick(lang, "停用与迁移", "MIGRATION"), pick(lang, f"{model['name']} 停用说明与迁移", f"{model['name']} retirement and migration"),
     pick(lang, "以下时间与差异来自小米 MiMo 官方下线公告。", "Dates and differences are from Xiaomi MiMo's retirement notice."), body, "mi-tone")


# ---------------------------------------------------------------- uses / platform / quickstart

def uses_section(lang, model):
    tier = model["tier"] if model else "overview"
    scenes = {
 "pro": [("编程与 Agent", "Coding and agents", "把需求拆成步骤，生成代码、调用工具并在长程任务里持续修正。", "Break work into steps, write code, call tools and keep correcting across long tasks."),
         ("科研与分析", "Research and analysis", "检索资料、提出假设、整理推理过程，辅助专业研究。", "Search sources, form hypotheses and organize reasoning for expert research."),
         ("多模态理解", "Multimodal understanding", "把截图、图表、视频或音频与文字一起交给模型分析。", "Send screenshots, charts, video or audio together with text for analysis.")],
        "flash": [("办公自动化", "Office automation", "批量处理文档摘要、表格整理、邮件草稿等高频任务。", "Run summaries, table cleanup and email drafts at volume."),
    ("内容生成", "Content generation", "生成网页、PPT 大纲与营销文案，成本可控。", "Draft web pages, slide outlines and copy at a predictable cost."),
    ("客服与助手", "Assistants", "把图片和文字问题一起交给模型，快速给出回复。", "Answer questions that mix images and text quickly.")],
        "overview": [("复杂 Agent 与编程", "Complex agents and coding", "用 MiMo-V2.6-Pro 处理长程、多步骤的开发与研究任务。", "Use MiMo-V2.6-Pro for long, multi-step engineering and research work."),
       ("规模化办公", "Office work at scale", "用 MiMo-V2.6-Flash 承担高频、批量的日常任务。", "Use MiMo-V2.6-Flash for frequent, high-volume everyday tasks."),
("全模态输入", "Omni-modal input", "图像、视频、音频与文本可一起作为输入。", "Combine image, video, audio and text in one request.")],
    }[tier]
    if model and model["id"] == "mimo-v2.5-pro":
        scenes = scenes[:2] + [("长文本处理", "Long-form text work", "处理长文档摘要、改写与结构化抽取等纯文本任务。", "Summarize, rewrite and extract structure from long documents.")]
    cards = "".join(f'<article class="mi-card"><span class="mi-num">0{i}</span><h3>{h(pick(lang, a, b))}</h3><p>{h(pick(lang, c, d))}</p></article>'
      for i, (a, b, c, d) in enumerate(scenes, 1))
    return section("use-cases", pick(lang, "使用场景", "USE CASES"), pick(lang, "从一个具体任务开始", "Start with a concrete task"), "",
     f'<div class="mi-cards">{cards}</div>')


def platform_section(lang):
    items = [("300+ 模型，一个 Key", "300+ models, one key", "统一 API Key 与余额，在 MiMo 与其他模型之间按任务切换。", "One API key and balance across MiMo and other models."),
      ("国内直连，并发不限", "Direct access, unlimited concurrency", "通过 AnyAIGC 域名从国内直接调用，不设固定 RPM 上限。", "Call AnyAIGC directly from mainland China with no fixed RPM cap."),
      ("V2.6 官方 4 折，单价透明", "V2.6 at 60% off, clear rates", "V2.6 系列约官方 4 折，控制台可查每次调用的 tokens 与扣费。", "V2.6 at about 60% off the official price, with per-request usage in the console."),
      ("OpenAI 兼容", "OpenAI compatible", "现有 OpenAI SDK 项目改 base_url 与 model 即可接入。", "Point an existing OpenAI SDK project at the new base_url and model.")]
    cards = "".join(f'<article class="mi-card"><span class="mi-num">0{i}</span><h3>{h(pick(lang, a, b))}</h3><p>{h(pick(lang, c, d))}</p></article>'
      for i, (a, b, c, d) in enumerate(items, 1))
    return section("platform", "AnyAIGC", pick(lang, "为什么通过 AnyAIGC 接入", "Why use MiMo through AnyAIGC"), "",
     f'<div class="mi-cards mi-cards-4">{cards}</div>', "mi-tone")


def examples(lang, model_id, omni):
    zh = lang == "zh"
    prompt = "用三句话介绍你自己，并说明你擅长的任务。" if zh else "Introduce yourself in three sentences and say what tasks you are best at."
    payload = json.dumps({"model": model_id, "messages": [{"role": "user", "content": prompt}]}, ensure_ascii=False, indent=2)
    curl = ('curl https://anyaigc.ai/v1/chat/completions \\\n'
     '  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
     '  -H "Content-Type: application/json" \\\n'
     f"  -d '{payload}'")
    python = ("# pip install openai\n"
       "import os\n"
       "from openai import OpenAI\n\n"
'client = OpenAI(api_key=os.environ["ANYAIGC_API_KEY"], base_url="https://anyaigc.ai/v1")\n\n'
       "completion = client.chat.completions.create(\n"
       f'    model="{model_id}",\n'
       f'    messages=[{{"role": "user", "content": "{prompt}"}}],\n'
       ")\n"
       "print(completion.choices[0].message.content)\n")
    stream = ("# pip install openai\n"
       "import os\n"
       "from openai import OpenAI\n\n"
       'client = OpenAI(api_key=os.environ["ANYAIGC_API_KEY"], base_url="https://anyaigc.ai/v1")\n\n'
"stream = client.chat.completions.create(\n"
f'    model="{model_id}",\n'
       f'    messages=[{{"role": "user", "content": "{prompt}"}}],\n'
       "    stream=True,\n"
       ")\n"
       "for chunk in stream:\n"
       "    if chunk.choices and chunk.choices[0].delta.content:\n"
       '        print(chunk.choices[0].delta.content, end="", flush=True)\n'
       "print()\n")
    node = ("// Node.js 18+，保存为 mimo.mjs 后运行：node mimo.mjs\n" if zh else "// Node.js 18+. Save as mimo.mjs and run: node mimo.mjs\n") + (
     'const res = await fetch("https://anyaigc.ai/v1/chat/completions", {\n'
     '  method: "POST",\n'
     "  headers: {\n"
     "    Authorization: `Bearer ${process.env.ANYAIGC_API_KEY}`,\n"
     '    "Content-Type": "application/json",\n'
     "  },\n"
     "  body: JSON.stringify({\n"
     f'    model: "{model_id}",\n'
     f'    messages: [{{ role: "user", content: "{prompt}" }}],\n'
     "  }),\n"
     "});\n"
     "const data = await res.json();\n"
     "console.log(data.choices[0].message.content);\n")
    tabs = [("cURL", curl), ("Python", python), (pick(lang, "Python 流式", "Python streaming"), stream), ("Node.js", node)]
    if omni:
        question = "这张图里有什么？请列出关键信息。" if zh else "What is in this image? List the key details."
        image = json.dumps({"model": model_id, "messages": [{"role": "user", "content": [
            {"type": "text", "text": question},
     {"type": "image_url", "image_url": {"url": "https://example.com/chart.png"}}]}]}, ensure_ascii=False, indent=2)
        tabs.append((pick(lang, "图像理解", "Image input"), 'curl https://anyaigc.ai/v1/chat/completions \\\n'
       '  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
       '  -H "Content-Type: application/json" \\\n'
       f"  -d '{image}'"))
    return tabs


def quickstart_section(lang, model):
    item = model or FLASH
    omni = item["id"] != "mimo-v2.5-pro"
    tabs = examples(lang, item["id"], omni)
    buttons, panels = [], []
    for i, (name, code) in enumerate(tabs):
        pid = f"mi-code-{i}"
        buttons.append(f'<button type="button" data-panel="{pid}" aria-selected="{"true" if i == 0 else "false"}">{h(name)}</button>')
        panels.append(f'<div class="mi-code" id="{pid}"{"" if i == 0 else " hidden"}><div class="mi-code-head"><span>{h(name)}</span>'
        f'<button class="mi-copy" type="button" data-copy="{pid}-src">{pick(lang, "复制", "Copy")}</button></div>'
 f'<pre><code id="{pid}-src">{h(code)}</code></pre></div>')
    steps = [pick(lang, "注册 AnyAIGC，在控制台创建 API Key。", "Sign up and create an API key in the console."),
      pick(lang, "把 Key 写入环境变量 ANYAIGC_API_KEY。", "Put the key in the ANYAIGC_API_KEY environment variable."),
      pick(lang, f"请求 /v1/chat/completions，model 填 {item['id']}。", f"Call /v1/chat/completions with model {item['id']}.")]
    steps_html = "".join(f"<li><b>{i:02d}</b><span>{h(s)}</span></li>" for i, s in enumerate(steps, 1))
    note = pick(lang, "返回 OpenAI 格式的 JSON：用量在 usage.prompt_tokens、usage.completion_tokens，缓存命中见 usage.prompt_tokens_details.cached_tokens。深度思考开关等扩展参数以 API 文档为准。",
         "Responses use the OpenAI JSON format: usage reports prompt_tokens and completion_tokens, and cache hits appear in usage.prompt_tokens_details.cached_tokens. See the API docs for extension parameters such as the thinking switch.")
    body = (f'<ol class="mi-steps">{steps_html}</ol>'
            f'<div class="mi-endpoint"><code>POST https://anyaigc.ai/v1/chat/completions</code><a href="{doc(lang)}">{pick(lang, "阅读 API 文档", "Read the API reference")} ↗</a></div>'
     f'<div class="mi-tabs" aria-label="{pick(lang, "代码示例", "Code examples")}">{"".join(buttons)}</div>{"".join(panels)}<p class="mi-note">{h(note)}</p>')
    title = pick(lang, f"三步接入 {item['name']} API" if model else "三步开始调用 MiMo API", f"Call {item['name']} in three steps" if model else "Call MiMo in three steps")
    return section("quickstart", pick(lang, "快速开始", "QUICKSTART"), title, "", body)


# ---------------------------------------------------------------- enterprise / trust / family / faq / footer

def enterprise_section(lang, name):
    cards = [(pick(lang, "增值税发票", "Invoices"), pick(lang, "增值税普通发票、增值税专用发票（专票）都能开，按实际充值金额开具。", "Invoices for every top-up, including Chinese VAT general and special invoices.")),
      (pick(lang, "对公转账", "Bank transfer"), pick(lang, "支持企业对公转账充值。", "Top up by corporate bank transfer.")),
      (pick(lang, "签订合同", "Contracts"), pick(lang, "可签订服务合同，配合采购与法务流程。", "Sign a service agreement for procurement and legal review.")),
      (pick(lang, "专属对接", "Dedicated support"), pick(lang, "专属客服和技术对接。", "Dedicated support and a technical contact."))]
    grid = "".join(f'<article class="mi-ent"><span class="mi-num">{i:02d}</span><h3>{h(t)}</h3><p>{h(d)}</p></article>' for i, (t, d) in enumerate(cards, 1))
    pay = payments.pay_row(lang, "mi").strip()
    actions = ('<div class="mi-actions">' + button(pick(lang, "联系企业客服", "Talk to sales"), SUPPORT)
        + button(pick(lang, "先注册试用", "Start with a free account"), REG, "line") + "</div>")
    return section("enterprise", pick(lang, "企业接入", "ENTERPRISE"), pick(lang, f"企业接入 {name} API", f"{name} API for teams and enterprises"),
            pick(lang, "研发、财务、法务和采购可以一起完成接入。", "Everything engineering, finance, legal and procurement need to sign off."),
            f'<div class="mi-ents">{grid}</div>{pay}{actions}', "mi-tone")


def trust_section(lang):
    items = "".join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in trust.ITEMS[lang])
    return section("trust", pick(lang, "信任与保障", "TRUST"), trust.HEAD[lang][0], h(trust.HEAD[lang][1]),
     f'<ul class="trust-list">{items}</ul><div class="mi-actions">'
     + button(pick(lang, "先注册领取 200 万 tokens", "Sign up for 2M free tokens"), REG) + "</div>")


def family_section(lang, slug):
    links = []
    current = ' aria-current="page"' if slug == "mimo" else ""
    links.append(f'<a href="/{lang}/models/mimo"{current}><span>Xiaomi MiMo API</span><small>{pick(lang, "全系总览", "Overview")}</small></a>')
    for m in MODELS:
        current = ' aria-current="page"' if m["slug"] == slug else ""
        tag = deal(lang) if not m["legacy"] else pick(lang, "官方已停用", "Retired")
        links.append(f'<a href="/{lang}/models/{m["slug"]}"{current}><span>{h(m["name"])}</span><small>{h(m["id"])} · {h(tag)}</small></a>')
    return section("family", pick(lang, "同系列模型", "FAMILY"), pick(lang, "Xiaomi MiMo 全系模型", "All Xiaomi MiMo models"), "",
            f'<div class="mi-family">{"".join(links)}</div>')


def faq_section(lang, faqs, model):
    name = model["name"] if model else "MiMo"
    body = '<div class="mi-faq">' + "".join(
 f'<details><summary><h3>{h(q)}</h3></summary><div class="mi-answer"><p>{h(a)}</p></div></details>' for q, a in faqs) + "</div>"
    return section("faq", "FAQ", pick(lang, f"{name} API 常见问题", f"{name} API FAQ"), "", body)


def final(lang, slug, model):
    other = "en" if lang == "zh" else "zh"
    name = model["name"] if model else "Xiaomi MiMo"
    heading = pick(lang, f"把 {name} 接入你的下一个产品", f"Build your next product with {name}")
    primary = button(pick(lang, "获取 API Key", "Get an API key"), REG, "light")
    if model and model["legacy"]:
        succ = MODEL_BY_SLUG[model["successor"]]
        heading = pick(lang, f"迁移到 {succ['name']}", f"Move to {succ['name']}")
        primary = button(pick(lang, f"查看 {succ['name']}", f"View {succ['name']}"), f"/{lang}/models/{succ['slug']}", "light")
    links = [(f"/{lang}/models/", pick(lang, "全部模型专题", "All model guides")), (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
      (doc(lang), pick(lang, "API 文档", "API documentation")), (f"/{other}/models/{slug}", pick(lang, "English version", "中文版"))]
    link_html = "".join(f'<li><a href="{h(u)}"{" hreflang=" + chr(34) + pick(other, "zh-CN", "en") + chr(34) if u.startswith("/" + other) else ""}>{h(t)}</a></li>' for u, t in links)
    footer_links = [(f"/{lang}/models/", pick(lang, "模型专题", "Model guides")), (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
      (CONSOLE, pick(lang, "控制台", "Console")), (SUPPORT, pick(lang, "联系客服", "Support")),
      ("/privacy", pick(lang, "隐私政策", "Privacy")), ("/terms", pick(lang, "服务条款", "Terms"))]
    legal = pick(lang, "Xiaomi MiMo、MiMo 是小米公司的商标，AnyAIGC 是独立 API 服务商，与其无隶属关系。模型使用与商用条款以小米 MiMo 官方条款为准；页面中的官方评测图表与示例素材来自小米 MiMo 官方。",
   "Xiaomi MiMo and MiMo are trademarks of Xiaomi. AnyAIGC is an independent API provider and is not affiliated with Xiaomi. Model use and commercial terms follow Xiaomi MiMo's official terms; benchmark charts and demo media on this page are from Xiaomi MiMo.")
    return (f'<section class="mi-final" aria-labelledby="final-title"><div class="mi-wrap">{mark("#ffffff", "mi-final-mark", 56)}'
     f'<h2 id="final-title">{h(heading)}</h2>'
     f'<p>{h(pick(lang, "注册 AnyAIGC，新用户送 200 万 tokens，一个 API Key 调用 300+ 模型。", "Sign up for AnyAIGC, get 2M free tokens, and call 300+ models with one API key."))}</p>'
     '<div class="mi-actions">' + primary
            + button(pick(lang, "查看模型广场", "Open the model catalog"), PRICING_URL, "ghost") + "</div>"
     f'<ul class="mi-final-links">{link_html}</ul></div></section></main>\n'
     '<footer class="mi-footer"><div class="mi-wrap"><a class="mi-brand" href="/">AnyAIGC</a>'
     f'<nav aria-label="{pick(lang, "页脚", "Footer")}">' + "".join(f'<a href="{h(u)}">{h(t)}</a>' for u, t in footer_links)
     + f'</nav><p class="mi-legal">{h(legal)}</p></div></footer>\n')


def render(lang, slug):
    model = MODEL_BY_SLUG.get(slug)
    faqs = faq_items(lang, model)
    out = head(lang, slug, model, faqs) + topbar(lang, model) + nav(lang, slug) + hero(lang, model) + banner(lang, model)
    if model is None:
        out += models_section(lang) + pricing_section(lang, None) + bench_section(lang, None) + showcase_section(lang, None)
    elif model["legacy"]:
        out += specs_section(lang, model) + migration_section(lang, model) + pricing_section(lang, model)
    else:
        out += specs_section(lang, model) + pricing_section(lang, model) + bench_section(lang, model) + showcase_section(lang, model)
    out += (uses_section(lang, model) + platform_section(lang) + quickstart_section(lang, model)
     + enterprise_section(lang, model["name"] if model else "MiMo") + trust_section(lang) + family_section(lang, slug)
     + faq_section(lang, faqs, model) + final(lang, slug, model))
    return out + f'<script src="/assets/models/mimo.js?v={VER}" defer></script>\n</body>\n</html>\n'


def main():
    for lang in ("zh", "en"):
        for slug in SLUGS:
            path = ROOT / lang / "models" / f"{slug}.html"
            path.write_text(render(lang, slug), encoding="utf-8", newline="\n")
            print(lang, slug)


if __name__ == "__main__":
    main()
