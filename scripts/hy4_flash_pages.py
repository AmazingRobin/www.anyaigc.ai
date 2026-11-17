"""Build the Tencent Hy4 flash topic pages: python scripts/hy4_flash_pages.py

Writes zh/models/hy4-flash.html and en/models/hy4-flash.html. Facts and prices live in
hy4_flash_data.py. It reuses assets/models/hy4.css and hy4.js (the Hunyuan style), so no
stylesheet or script changes are needed. Post-process afterwards with the SEO scripts
listed in AGENTS.md.
"""

from decimal import Decimal
from html import escape, unescape
from pathlib import Path
import json
import re

from hy4_flash_data import (PRICES, LABEL, CHECKED_DATE, RELEASE_DATE, PRICING_URL, OFFICIAL_URL,
                            DOC_CHAT, SLUG, MODEL_ID, NAME)
import payments
import trust

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.anyaigc.ai"
REG = "https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9"
SUPPORT = "https://anyaigc.ai/customersupport"
CONSOLE = "https://anyaigc.ai/console"
DOC_MESSAGES = "https://docs.anyaigc.ai/reference/minimax/v1/messages?leaf=264600675"
VER = "20261113"
LOGO = (ROOT / "assets/icons/hunyuan-color.svg").read_text(encoding="utf-8")
DEAL_ZH, DEAL_EN = "约官方 4 折", "About 60% off list"


def pick(lang, zh, en):
    return zh if lang == "zh" else en


def h(value):
    return escape(str(value), quote=True)


def url(lang):
    return f"{SITE}/{lang}/models/{SLUG}"


def doc(lang, link=DOC_CHAT):
    return link if lang == "zh" else link.replace("https://docs.anyaigc.ai/", "https://docs.anyaigc.ai/en/", 1)


def money(value):
    return format(Decimal(value).normalize(), "f")


def usd(value):
    whole, _, frac = money(value).partition(".")
    return whole + "." + frac.ljust(2, "0")


def width(text):
    return sum(2 if ord(c) > 0x2E7F else 1 for c in text)


def mark(cls="hy-mark", size=28):
    body = re.search(r"<svg[^>]*>(.*)</svg>", LOGO, re.S).group(1)
    body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="{size}" height="{size}" '
            f'aria-hidden="true" focusable="false">{body}</svg>')


def price_of(key):
    return next(p for p in PRICES if p["key"] == key)


def label(lang, key):
    return pick(lang, *LABEL[key])


def unit(lang):
    return pick(lang, "百万 tokens", "1M tokens")


def deal(lang):
    return pick(lang, DEAL_ZH, DEAL_EN)


def button(text, href, kind="dark", arrow=True):
    tail = ' <span aria-hidden="true">→</span>' if arrow else ""
    return f'<a class="hy-btn hy-btn-{kind}" href="{h(href)}">{h(text)}{tail}</a>'


def section(sid, kicker, title, lead, body, tone=""):
    cls = f"hy-section {tone}".strip()
    lead_html = f'<p class="hy-lead">{lead}</p>' if lead else ""
    return (f'<section class="{cls}" id="{sid}" aria-labelledby="{sid}-title"><div class="hy-wrap">'
            f'<header class="hy-head"><p class="hy-kicker">{h(kicker)}</p>'
            f'<h2 id="{sid}-title">{h(title)}</h2>{lead_html}</header>\n{body}\n</div></section>\n')


# ---------------------------------------------------------------- metadata

def metadata(lang):
    p, o = price_of("input"), price_of("output")
    title = pick(lang, "Hy4 Flash API 价格与接入｜约官方 4 折 - AnyAIGC",
                 "Hy4 Flash API Pricing | Save 60% - AnyAIGC")
    desc = pick(lang,
                f"腾讯混元 Hy4 Flash API 价格与接入：约官方 4 折，输入 ${p['amount']}/百万 tokens，输出 ${o['amount']}，支持图像理解与 1M 上下文，并发不限，支持对公转账、合同与增值税专票。",
                f"Tencent Hy4 Flash API at about 60% off list: ${p['amount']}/1M input tokens, ${o['amount']} output, 1M context, image input, unlimited concurrency, VAT invoices.")
    assert (width(title) <= 64 if lang == "zh" else len(title) <= 65), (lang, width(title), title)
    assert (60 <= len(desc) <= 120 if lang == "zh" else 120 <= len(desc) <= 160), (lang, len(desc), desc)
    return title, desc


def keywords(lang):
    return ",".join(pick(lang,
        ["Hy4 Flash API", "混元 Hy4 Flash API", "Hy4 flash API 价格", "Hy4 Flash API key", "Hy4 Flash API 企业", "Hy4 Flash API 发票", "腾讯混元 API", "Hy4 flash 图像理解 API"],
        ["Hy4 Flash API", "Tencent Hy4 flash API", "Hy4 Flash API pricing", "Hy4 Flash API key", "Hy4 Flash API for business", "Tencent Hunyuan API", "Hy4 Flash vision API"]))


# ---------------------------------------------------------------- FAQ

def faq_items(lang):
    p, o, c = price_of("input"), price_of("output"), price_of("cache")
    items = [
        (pick(lang, "Hy4 Flash API 多少钱？比官方便宜多少？", "How much does the Hy4 Flash API cost, and how far below list price is it?"),
         pick(lang,
              f"按 token 计费，单位 USD/百万 tokens：输入 ${p['amount']}（官方 ${p['official']}）、输出 ${o['amount']}（官方 ${o['official']}）、缓存命中 ${c['amount']}（官方 ${c['official']}）。腾讯混元官方发布页给出的 API 价格为输入 ¥{p['cny']}、输出 ¥{o['cny']}、缓存命中 ¥{c['cny']}，美元官方价按约 7.19 元/美元折算。AnyAIGC 输入和输出约为官方价的 40%，缓存命中约 43%，整体约官方 4 折。腾讯云 TokenHub 在 2026-11-30 前另有限时 5 折活动，本页不以活动价作对比基线。实时价格以模型广场为准。",
              f"Billed per token in USD per 1M tokens: input ${p['amount']} (list ${p['official']}), output ${o['amount']} (list ${o['official']}), cache hit ${c['amount']} (list ${c['official']}). Tencent Hunyuan's release notes list ¥{p['cny']} input, ¥{o['cny']} output and ¥{c['cny']} cache hit; USD list prices use about 7.19 CNY per USD. AnyAIGC input and output are about 40% of list and cache hits about 43%, roughly 60% off overall. Tencent Cloud TokenHub also runs a limited 50%-off promotion until 2026-11-30; this page does not use the promo price as its baseline. See the model catalog for live rates.")),
        (pick(lang, "Hy4 flash 和 Hy4 有什么区别？", "What is the difference between Hy4 flash and Hy4?"),
         pick(lang,
              "据腾讯混元官方发布页（2026-11-16），Hy4 flash 总参数 224B（含 64B Engram 参数）、激活参数 12B，API 价格为输入 ¥0.5、输出 ¥2，Hy4 为 ¥6、¥18。官方称 flash 的 KV cache 只有 Hy4 的 1/6，解码速度超过 150 tps；在 WorkBuddy 日常任务评测里，平均耗时比 Hy4 少 70%、平均成本约为 Hy4 的 1/15，日常任务效果基本持平，Coding 长程任务小幅下降。官方建议日常任务用 flash，长程软件工程等复杂任务用 Hy4。以上为官方自述，AnyAIGC 未独立复测。",
              "Per Tencent Hunyuan's release notes (2026-11-16), Hy4 flash has 224B total parameters (64B of them Engram) and 12B active, and its API price is ¥0.5 input and ¥2 output against ¥6 and ¥18 for Hy4. Tencent says flash's KV cache is one sixth of Hy4's and decoding exceeds 150 tps. In its WorkBuddy everyday-task evaluation, average task time is 70% lower and average cost about one fifteenth of Hy4's, with broadly equal quality on everyday tasks and a small drop on long-horizon coding. Tencent recommends flash for everyday work and Hy4 for complex tasks such as long-horizon software engineering. These are Tencent's own figures; AnyAIGC has not re-tested them.")),
        (pick(lang, "Hy4 Flash 支持图片输入吗？", "Does Hy4 Flash accept image input?"),
         pick(lang,
              "支持。模型广场的说明写明支持图片理解，官方称 Hy4 flash 为多模态模型。在 POST /v1/chat/completions 里用 image_url 内容块传入图片链接或 base64，输出为文本。AnyAIGC 文档目前没有给出图片尺寸与数量的限制，请以文档为准。",
              "Yes. The model catalog lists image understanding and Tencent describes Hy4 flash as multimodal. Send an image URL or base64 data in an image_url content part on POST /v1/chat/completions; the output is text. The AnyAIGC docs do not currently state image size or count limits, so follow the docs.")),
        (pick(lang, "应该使用哪个 API 接口？", "Which API endpoint should I use?"),
         pick(lang,
              "两种格式都支持：OpenAI 兼容的 POST https://anyaigc.ai/v1/chat/completions，以及 Anthropic 格式的 POST https://anyaigc.ai/v1/messages，鉴权都用 Authorization: Bearer <API Key>，model 填 hy4-flash。OpenAI SDK 只需把 base_url 设为 https://anyaigc.ai/v1。",
              "Both formats work: the OpenAI-compatible POST https://anyaigc.ai/v1/chat/completions and the Anthropic-style POST https://anyaigc.ai/v1/messages, both with Authorization: Bearer <API Key> and model set to hy4-flash. With the OpenAI SDK, set base_url to https://anyaigc.ai/v1.")),
        (pick(lang, "并发有限制吗？", "Is concurrency limited?"),
         pick(lang, "AnyAIGC 的 Hy4 Flash 接入并发不限，所有用户默认享有。长文本和 Agent 类请求耗时更长，请在应用里设置合理的超时与重试。",
              "AnyAIGC offers Hy4 Flash with unlimited concurrency for every account by default. Long-context and agent requests take longer, so set sensible timeouts and retries.")),
        (pick(lang, "生成内容可以商用吗？", "Can I use the output commercially?"),
         pick(lang, "模型与输出的使用条款以腾讯混元官方条款为准。AnyAIGC 是独立 API 服务商，与腾讯无隶属关系。",
              "Use of the model and its output is governed by Tencent Hunyuan's official terms. AnyAIGC is an independent API provider and is not affiliated with Tencent.")),
    ]
    enterprise = [
        (pick(lang, "AnyAIGC 能开发票吗？支持增值税专票吗？", "Can AnyAIGC issue invoices, including VAT special invoices?"),
         pick(lang, "支持。可按实际充值金额开具增值税普通发票和增值税专用发票，联系企业客服办理即可。",
              "Yes. AnyAIGC issues invoices for actual top-ups, including Chinese VAT general and VAT special invoices. Contact enterprise support to arrange them.")),
        (pick(lang, "企业可以对公转账和签合同吗？", "Can my company pay by bank transfer and sign a contract?"),
         pick(lang, "可以。支持企业对公转账充值，可签订服务合同，并提供专属客服与技术对接。",
              "Yes. Companies can top up by corporate bank transfer, sign a service agreement, and work with dedicated support and a technical contact.")),
    ]
    items = items + enterprise + [(payments.Q[lang], payments.A[lang])] + trust.FAQ[lang]
    assert 10 <= len(items) <= 13, len(items)
    return items


# ---------------------------------------------------------------- head / nav

def breadcrumb_items(lang):
    return [(pick(lang, "模型专题", "Model guides"), f"{SITE}/{lang}/models/"), (NAME, url(lang))]


def head(lang, faqs):
    title, desc = metadata(lang)
    me = url(lang)
    image = f"{SITE}/assets/og/{SLUG}-{lang}.png"
    amounts = [Decimal(p["amount"]) for p in PRICES]
    offers = [{"@type": "Offer", "name": f'{MODEL_ID} {label(lang, p["key"])} / {unit(lang)}',
               "price": p["amount"], "priceCurrency": "USD", "url": me + "#pricing"} for p in PRICES]
    crumbs = [{"@type": "ListItem", "position": i, "name": n, "item": u}
              for i, (n, u) in enumerate(breadcrumb_items(lang), 1)]
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": SITE + "/#org", "name": "AnyAIGC", "url": "https://www.anyaigc.ai/", "logo": SITE + "/logo.webp"},
        {"@type": "WebSite", "@id": SITE + "/#website", "name": "AnyAIGC", "url": SITE + "/", "publisher": {"@id": SITE + "/#org"}},
        {"@type": "WebPage", "@id": me + "#webpage", "url": me, "name": title, "description": desc,
         "inLanguage": pick(lang, "zh-CN", "en"), "dateModified": CHECKED_DATE, "isPartOf": {"@id": SITE + "/#website"},
         "breadcrumb": {"@id": me + "#breadcrumb"}, "mainEntity": {"@id": me + "#product"}},
        {"@type": "BreadcrumbList", "@id": me + "#breadcrumb", "itemListElement": crumbs},
        {"@type": "Product", "@id": me + "#product", "name": "Hy4 Flash API (AnyAIGC)", "description": desc,
         "sku": MODEL_ID, "image": image, "brand": {"@type": "Brand", "name": "Tencent Hunyuan"},
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
<meta name="keywords" content="{h(keywords(lang))}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#f9f9f9">
<link rel="canonical" href="{me}">
<link rel="alternate" hreflang="zh-CN" href="{url('zh')}">
<link rel="alternate" hreflang="en" href="{url('en')}">
<link rel="alternate" hreflang="x-default" href="{url('en')}">
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
<meta property="og:image:alt" content="{NAME} API · AnyAIGC">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{h(title)}">
<meta name="twitter:description" content="{h(desc)}">
<meta name="twitter:image" content="{image}">
<link rel="stylesheet" href="/assets/models/scrollbar.css?v=20261024b">
<link rel="stylesheet" href="/assets/models/hy4.css?v={VER}">
<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
'''


def topbar(lang):
    text = pick(lang, "Hy4 Flash API 约官方 4 折，新用户注册送 200 万 tokens。",
                "Hy4 Flash API at about 60% off Tencent's list price. 2M free tokens for new accounts.")
    return (f'<div class="hy-bar"><p>{h(text)}{pick(lang, "", " ")}<a href="#pricing">{pick(lang, "查看价格", "See pricing")} '
            '<span aria-hidden="true">→</span></a></p></div>\n')


def nav(lang):
    other = "en" if lang == "zh" else "zh"
    links = [(f"/{lang}/models/", pick(lang, "模型专题", "Model guides")),
             (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
             ("#pricing", pick(lang, "价格", "Pricing")),
             ("#enterprise", pick(lang, "企业接入", "Enterprise")),
             (doc(lang), pick(lang, "API 文档", "API docs"))]
    items = "".join(f'<li><a href="{h(href)}">{h(text)}</a></li>' for href, text in links)
    return (f'<a class="hy-skip" href="#main">{pick(lang, "跳到主要内容", "Skip to main content")}</a>\n'
            '<header class="hy-nav"><div class="hy-wrap hy-nav-inner">'
            '<a class="hy-brand" href="/" aria-label="AnyAIGC">AnyAIGC</a><span class="hy-brand-x" aria-hidden="true">×</span>'
            f'<a class="hy-brand-hy" href="/{lang}/models/{SLUG}" aria-label="Tencent Hunyuan Hy4 Flash">{mark()}<span>{pick(lang, "腾讯混元 Hy4 Flash", "Tencent Hy4 Flash")}</span></a>'
            f'<nav id="hy-navigation" aria-label="{pick(lang, "主导航", "Main navigation")}"><ul class="hy-nav-links">{items}</ul></nav>'
            '<ul class="hy-nav-actions">'
            f'<li><a href="/{other}/models/{SLUG}" hreflang="{pick(other, "zh-CN", "en")}">{pick(lang, "EN", "中文")}</a></li>'
            f'<li><a href="{CONSOLE}">{pick(lang, "登录", "Log in")}</a></li>'
            f'<li>{button(pick(lang, "注册", "Sign up"), REG, arrow=False)}</li></ul>'
            f'<button class="hy-menu" type="button" aria-controls="hy-navigation" aria-expanded="false" aria-label="{pick(lang, "打开导航菜单", "Open navigation menu")}"><span></span></button>'
            '</div></header>\n')


# ---------------------------------------------------------------- hero

def hero_art(lang):
    """Line drawing in the spirit of hy.tencent.com's hero: axes, hatched triangle, dashed box, dots, serif wordmark."""
    hatch = []
    for x in range(132, 360, 12):
        y_top = 320 - (x - 120) * 200 / 240
        hatch.append(f"M{x} 320V{y_top:.1f}")
    ink = "#1a1a1a"
    label_text = pick(lang, "Hy4 Flash 线稿示意图", "Line drawing of Hy4 Flash")
    return (f'<figure class="hy-art"><svg viewBox="0 0 560 400" role="img" aria-label="{h(label_text)}">'
            f'<rect x="96" y="84" width="304" height="256" class="hy-draw hy-draw-dash" stroke="{ink}" fill="none" stroke-width="1.2"/>'
            f'<path class="hy-draw hy-draw-line" pathLength="1" stroke="{ink}" fill="none" stroke-width="1.2" d="M60 340H520M512 335l8 5-8 5"/>'
            f'<path class="hy-draw hy-draw-line d2" pathLength="1" stroke="{ink}" fill="none" stroke-width="1.2" d="M60 340V50M55 58l5-8 5 8"/>'
            f'<path class="hy-draw hy-draw-line d3" pathLength="1" stroke="{ink}" fill="none" stroke-width="1.2" d="M120 320H360V120Z"/>'
            f'<path class="hy-draw hy-draw-line d4" pathLength="1" stroke="{ink}" fill="none" stroke-width=".7" d="{"".join(hatch)}"/>'
            '<circle class="hy-dot d1" cx="120" cy="320" r="7" fill="#f6d46b"/>'
            '<circle class="hy-dot d2" cx="360" cy="120" r="7" fill="#7fd6ee"/>'
            '<circle class="hy-dot d3" cx="360" cy="320" r="7" fill="#f6d46b"/>'
            f'<text class="hy-word" x="376" y="246" font-size="72" font-family="Georgia, Times New Roman, serif" font-weight="700" fill="{ink}">Hy4</text>'
            f'<text class="hy-word" x="378" y="286" font-size="40" font-family="Georgia, Times New Roman, serif" font-weight="400" fill="{ink}">flash</text>'
            '</svg></figure>')


def hero(lang):
    items = breadcrumb_items(lang)
    crumbs = "".join(f'<li><a href="{h(u.removeprefix(SITE))}">{h(n)}</a></li>' for n, u in items[:-1])
    crumbs += f'<li aria-current="page">{h(items[-1][0])}</li>'
    p = price_of("input")
    sub = pick(lang, "腾讯混元面向日常工作的高性价比模型，支持图像理解", "Tencent Hunyuan's low-cost model for everyday work, with image understanding")
    lead = pick(lang,
                f"腾讯混元 Hy4 flash 面向日常工作：总参数 224B、激活参数 12B，支持多模态和 1M 上下文，官方称 API 价格相比 Hy4 大幅降低。通过 AnyAIGC 调用，OpenAI 与 Anthropic 两种接口格式都可用，并发不限。输入 <strong>${p['amount']} / 百万 tokens</strong>，官方 ${p['official']}。",
                f"Hy4 flash targets everyday work: 224B total and 12B active parameters, multimodal input and a 1M-token context, with API pricing Tencent says is far below Hy4. Call it through AnyAIGC in OpenAI or Anthropic format, with unlimited concurrency. Input is <strong>${p['amount']} / 1M tokens</strong> (list ${p['official']}).")
    detail = pick(lang, f"输入 ${p['amount']} · 官方 ${p['official']} / 百万 tokens", f"Input ${p['amount']} · list ${p['official']} / 1M tokens")
    chip = f'<a class="hy-deal" href="#pricing"><b>{h(deal(lang))}</b><span>{h(detail)}</span></a>'
    facts = [pick(lang, "并发不限", "Unlimited concurrency"), pick(lang, "OpenAI + Anthropic 格式", "OpenAI + Anthropic formats"),
             pick(lang, "300+ 模型 · 一个 Key", "300+ models · one key"), pick(lang, "对公 · 专票", "Contracts · invoices"),
             pick(lang, "注册送 200 万 tokens", "2M free tokens")]
    return ('<main id="main">\n<section class="hy-hero" aria-labelledby="hero-title"><div class="hy-wrap"><div class="hy-hero-grid"><div>'
            f'<nav class="hy-crumbs" aria-label="{pick(lang, "面包屑", "Breadcrumb")}"><ol>{crumbs}</ol></nav>'
            f'<h1 id="hero-title"><span class="hy-h1-main">{NAME} API</span><span class="hy-h1-sub">{h(sub)}</span></h1>{chip}'
            f'<p class="hy-hero-lead">{lead}</p><div class="hy-actions hy-actions-left">'
            + button(pick(lang, "获取 API Key", "Get an API key"), REG)
            + button(pick(lang, "查看 API 价格", "See API pricing"), "#pricing", "line")
            + button(pick(lang, "API 文档", "API docs"), doc(lang), "line")
            + '</div><ul class="hy-facts">' + "".join(f"<li>{h(f)}</li>" for f in facts) + "</ul></div>"
            + hero_art(lang) + "</div></div></section>\n")


# ---------------------------------------------------------------- specs / pricing

def specs_section(lang):
    specs = pick(lang,
                 [("输入模态", "文本、图像"), ("输出模态", "文本"), ("上下文长度", "1M tokens"), ("参数规模", "总 224B · 激活 12B")],
                 [("Input", "Text, image"), ("Output", "Text"), ("Context window", "1M tokens"), ("Parameters", "224B total · 12B active")])
    caps = pick(lang,
                ["图像理解", "工具调用", "结构化 JSON 输出", "深度思考", "文档与 PPT 处理", "1M 长上下文"],
                ["Image understanding", "Tool calling", "Structured JSON output", "Deep thinking", "Documents and slides", "1M-token context"])
    cells = "".join(f'<div><dt>{h(k)}</dt><dd>{h(v)}</dd></div>' for k, v in specs)
    cap_html = "".join(f"<li>{h(c)}</li>" for c in caps)
    note = pick(lang,
                f"规格来自腾讯混元官方发布页（{RELEASE_DATE} 发布，{CHECKED_DATE} 查询）和模型广场的模型说明。总参数含 64B Engram 参数；发布页没有给出最大输出长度，本页不写。",
                f"Specs come from Tencent Hunyuan's release notes (published {RELEASE_DATE}, checked {CHECKED_DATE}) and the model catalog's description. The 224B total includes 64B of Engram parameters; the release notes give no maximum output length, so this page leaves it out.")
    body = (f'<div class="hy-specs"><dl class="hy-spec-grid">{cells}</dl><div class="hy-caps"><h3>{pick(lang, "模型能力", "Capabilities")}</h3>'
            f'<ul>{cap_html}</ul></div></div><p class="hy-note">{h(note)} <a href="{OFFICIAL_URL}" rel="noopener">{pick(lang, "官方发布页", "Release notes")} ↗</a></p>')
    return section("specs", pick(lang, "模型规格", "SPECS"), pick(lang, "Hy4 Flash 模型规格", "Hy4 Flash specs"), "", body)


def cost(million_in, million_out, cached=Decimal(0)):
    p_in, p_out, p_cache = (Decimal(price_of(k)["amount"]) for k in ("input", "output", "cache"))
    o_in, o_out, o_cache = (Decimal(price_of(k)["official"]) for k in ("input", "output", "cache"))
    total = (million_in - cached) * p_in + cached * p_cache + million_out * p_out
    official = (million_in - cached) * o_in + cached * o_cache + million_out * o_out
    return total, official


def cost_card(lang, million_in, million_out, cached=Decimal(0)):
    total, official = cost(million_in, million_out, cached)
    p = {k: price_of(k)["amount"] for k in ("input", "output", "cache")}
    if cached:
        heading = pick(lang, f"{money(million_in)}M 输入（{money(cached)}M 命中缓存）+ {money(million_out)}M 输出",
                       f"{money(million_in)}M input ({money(cached)}M cached) + {money(million_out)}M output")
        calc = f"{money(million_in - cached)} × ${p['input']} + {money(cached)} × ${p['cache']} + {money(million_out)} × ${p['output']}"
    else:
        heading = pick(lang, f"{money(million_in)}M 输入 + {money(million_out)}M 输出", f"{money(million_in)}M input + {money(million_out)}M output")
        calc = f"{money(million_in)} × ${p['input']} + {money(million_out)} × ${p['output']}"
    compare = f'<p class="hy-cost-official">{h(pick(lang, "官方同用量", "Same usage at list price"))} <s>${usd(official)}</s></p>'
    return (f'<article class="hy-cost"><h3>{NAME}</h3><p class="hy-cost-use">{h(heading)}</p>'
            f'<p><code>{h(calc)}</code></p><strong>${usd(total)}</strong>{compare}</article>')


def pricing_section(lang):
    rows = [f'<tbody><tr class="hy-row-head"><th colspan="4" scope="rowgroup">{NAME} <span class="hy-tag hy-tag-deal">{h(deal(lang))}</span>'
            f'<code class="hy-row-id">{MODEL_ID}</code></th></tr>']
    for p in PRICES:
        official = f'<s>${h(p["official"])}</s> <small>¥{h(p["cny"])}</small>'
        rows.append(f'<tr><th scope="row">{h(label(lang, p["key"]))}</th><td><code>{MODEL_ID}</code></td>'
                    f'<td class="hy-official">{official}</td><td><strong>${h(p["amount"])}</strong> / {h(unit(lang))}</td></tr>')
    rows.append("</tbody>")
    table = (f'<div class="hy-table-wrap"><table class="hy-table"><caption>{pick(lang, "Hy4 Flash API 价格表（USD）", "Hy4 Flash API price table (USD)")}</caption>'
             f'<thead><tr><th scope="col">{pick(lang, "计费项", "Item")}</th><th scope="col">{pick(lang, "模型名", "Model")}</th>'
             f'<th scope="col">{pick(lang, "腾讯云官方价", "Tencent list price")}</th><th scope="col">{pick(lang, "AnyAIGC 单价", "AnyAIGC price")}</th></tr></thead>'
             + "".join(rows) + "</table></div>")
    pi, po = price_of("input"), price_of("output")
    savings = (f'<div class="hy-savings"><strong>{h(deal(lang))}</strong><p>'
               + h(pick(lang,
                        f"输入 ${pi['amount']}、输出 ${po['amount']}，腾讯云官方同项为 ${pi['official']}、${po['official']}（¥{pi['cny']}、¥{po['cny']}），约为官方价的 40%，即约官方 4 折。",
                        f"Input is ${pi['amount']} and output ${po['amount']}, versus Tencent Cloud's ${pi['official']} and ${po['official']} (¥{pi['cny']} and ¥{po['cny']}). That is about 40% of list, roughly 60% off."))
               + pick(lang, "", " ") + f'<a href="{OFFICIAL_URL}" rel="noopener">{pick(lang, "官方价格来源", "Official price source")} ↗</a></p></div>')
    billing = ('<ul class="hy-billing">'
               f'<li><strong>{pick(lang, "按 token 计费", "Per-token billing")}</strong>{pick(lang, "输入、输出、缓存命中分别计价。", "Input, output and cache hits are priced separately.")}</li>'
               f'<li><strong>{pick(lang, "并发不限", "Unlimited concurrency")}</strong>{pick(lang, "并发不设限制，所有用户默认享有。", "No concurrency limit, for every account.")}</li>'
               f'<li><strong>{pick(lang, "余额通用", "Shared balance")}</strong>{pick(lang, "一个 Key 调用 300+ 模型，$1 起充。", "One key for 300+ models; top up from $1.")}</li></ul>')
    note = pick(lang,
                f"单位 USD/百万 tokens，按成功请求的实际 tokens 计费，实时价格以模型广场为准。官方价取腾讯云人民币挂牌价（输入 ¥{pi['cny']}、输出 ¥{po['cny']}、缓存命中 ¥{price_of('cache')['cny']}），美元数值按约 7.19 元/美元折算（{CHECKED_DATE} 查询），仅作对比。",
                f"Prices are USD per 1M tokens, charged on the actual tokens of successful requests; see the model catalog for live rates. List prices are Tencent Cloud's CNY rates (¥{pi['cny']} input, ¥{po['cny']} output, ¥{price_of('cache')['cny']} cache hit) converted at about 7.19 CNY per USD (checked {CHECKED_DATE}), shown for comparison.")
    note += pick(lang, f" 腾讯云 TokenHub 在 2026-11-30 前另有限时 5 折活动，本页不以活动价作为对比基线。",
                 f" Tencent Cloud TokenHub also runs a limited 50%-off promotion until 2026-11-30; this page does not use the promo price as its baseline.")
    examples = [cost_card(lang, Decimal(1), Decimal("0.25")), cost_card(lang, Decimal(10), Decimal("2.5")),
                cost_card(lang, Decimal(10), Decimal("2.5"), Decimal(8))]
    body = (savings + billing + table + f'<p class="hy-note">{h(note)}</p>'
            + f'<h3 class="hy-sub">{pick(lang, "成本示例", "Cost examples")}</h3><div class="hy-costs">{"".join(examples)}</div>'
            + '<div class="hy-actions hy-actions-left">' + button(pick(lang, "获取 API Key", "Get an API key"), REG)
            + f'<a class="hy-text-link" href="{PRICING_URL}">{pick(lang, "在模型广场查看", "View in the model catalog")} ↗</a></div>')
    return section("pricing", pick(lang, "价格", "PRICING"), pick(lang, "Hy4 Flash API 价格", "Hy4 Flash API pricing"),
                   pick(lang, "直接对照腾讯云官方价，每一项单价都写在表里。", "Every rate side by side with Tencent Cloud's list price."), body, "hy-tone")


def vs_hy4_section(lang):
    pi, po, pc = price_of("input"), price_of("output"), price_of("cache")
    items = [
        (pick(lang, f"输入 ¥{pi['cny']}，输出 ¥{po['cny']}", f"Input ¥{pi['cny']}, output ¥{po['cny']}"),
         pick(lang, f"官方 API 价格每百万 tokens：Hy4 flash 输入 ¥{pi['cny']}、输出 ¥{po['cny']}、缓存命中 ¥{pc['cny']}，Hy4 为 ¥6、¥18、¥0.3。",
              f"Official API prices per 1M tokens: Hy4 flash is ¥{pi['cny']} input, ¥{po['cny']} output and ¥{pc['cny']} cache hit, against ¥6, ¥18 and ¥0.3 for Hy4.")),
        (pick(lang, "总 224B，激活 12B", "224B total, 12B active"),
         pick(lang, "总参数含 64B Engram 参数，支持多模态和 1M 上下文。官方称 KV cache 只有 Hy4 的 1/6，解码速度超过 150 tps。",
              "The total includes 64B Engram parameters, with multimodal input and a 1M-token context. Tencent says the KV cache is one sixth of Hy4's and decoding exceeds 150 tps.")),
        (pick(lang, "日常任务效果基本持平", "Everyday tasks stay on par"),
         pick(lang, "官方 WorkBuddy 评测：与 Hy4 相比，平均任务耗时减少 70%，平均成本约为 1/15，日常工作任务效果基本持平，Coding 长程任务小幅下降。",
              "In Tencent's WorkBuddy evaluation, average task time is 70% lower than Hy4 and average cost about one fifteenth, with broadly equal results on everyday tasks and a small drop on long-horizon coding.")),
        (pick(lang, "怎么选", "How to choose"),
         pick(lang, "官方建议深度搜索、文档处理、PPT 生成、简单前端展示、computer use 等日常任务用 Hy4 flash，长程软件工程等复杂任务用智能上限更高的 Hy4。",
              "Tencent recommends Hy4 flash for deep search, document work, slide generation, simple front-end pages and computer use, and Hy4 for complex work such as long-horizon software engineering.")),
    ]
    html = "".join(f'<article class="hy-adv"><span>{i:02d}</span><h3>{h(t)}</h3><p>{h(d)}</p></article>' for i, (t, d) in enumerate(items, 1))
    note = pick(lang, f"以上数据来自腾讯混元官方发布页（{RELEASE_DATE}），为官方自述，AnyAIGC 未独立复测。",
                f"These figures come from Tencent Hunyuan's release notes ({RELEASE_DATE}) and are Tencent's own claims; AnyAIGC has not re-tested them.")
    body = (f'<div class="hy-advs">{html}</div><p class="hy-note">{h(note)} <a href="{OFFICIAL_URL}" rel="noopener">{pick(lang, "官方发布页", "Release notes")} ↗</a> '
            f'<a href="/{lang}/models/hy4">{pick(lang, "Hy4 专题页", "Hy4 guide")} →</a></p>')
    return section("vs-hy4", pick(lang, "相比 HY4", "VS HY4"), pick(lang, "Hy4 flash 和 Hy4 怎么选", "Hy4 flash or Hy4"), "", body)


def uses_section(lang):
    scenes = [
        (pick(lang, "规模化 Agent 与编程辅助", "Agents at scale and coding help"),
         pick(lang, "模型广场的说明把规模化 Agent 和编程辅助列为适用场景；解码速度快、KV Cache 开销低，适合高并发放量。",
              "The model catalog lists agents at scale and coding help as target uses; fast decoding and a small KV cache suit high-volume traffic.")),
        (pick(lang, "文档、PPT 与长文档解析", "Documents, slides and long-document parsing"),
         pick(lang, "官方推荐用于深度搜索、文档处理和 PPT 生成；1M 上下文可以一次放入较长的资料。",
              "Tencent recommends it for deep search, document processing and slide generation; the 1M-token context holds long source material in one request.")),
        (pick(lang, "图表识别与批量办公自动化", "Chart reading and batch office automation"),
         pick(lang, "把截图、图表或文档页面和文字一起交给模型，提取要点；适合批量处理的日常办公任务。",
              "Send screenshots, charts or document pages with text and extract key points, for everyday office tasks run in bulk.")),
    ]
    cards = "".join(f'<article class="hy-card"><span class="hy-num">0{i}</span><h3>{h(t)}</h3><p>{h(d)}</p></article>' for i, (t, d) in enumerate(scenes, 1))
    return section("use-cases", pick(lang, "使用场景", "USE CASES"), pick(lang, "从一个具体任务开始", "Start with a concrete task"), "", f'<div class="hy-cards">{cards}</div>')


def platform_section(lang):
    items = [(pick(lang, "300+ 模型，一个 Key", "300+ models, one key"), pick(lang, "统一 API Key 与余额，在 Hy4 Flash 与其他模型之间按任务切换。", "One API key and balance across Hy4 Flash and other models.")),
             (pick(lang, "国内直连，并发不限", "Unlimited concurrency"), pick(lang, "通过 AnyAIGC 域名从国内直接调用，并发不设限制。", "No concurrency limit, for every account by default.")),
             (pick(lang, "约官方 4 折，单价透明", "About 60% off, clear rates"), pick(lang, "输入、输出、缓存命中分别计价，控制台可查每次调用的 tokens 与扣费。", "Input, output and cache hits priced separately, with per-request usage in the console.")),
             (pick(lang, "两种接口格式", "Two API formats"), pick(lang, "OpenAI 兼容和 Anthropic 格式都能调用 hy4-flash，现有项目改 base_url 与 model 即可。", "Call hy4-flash in OpenAI-compatible or Anthropic format; point an existing project at the new base_url and model."))]
    cards = "".join(f'<article class="hy-card"><span class="hy-num">0{i}</span><h3>{h(t)}</h3><p>{h(d)}</p></article>' for i, (t, d) in enumerate(items, 1))
    return section("platform", "AnyAIGC", pick(lang, "为什么通过 AnyAIGC 接入", "Why use Hy4 Flash through AnyAIGC"), "",
                   f'<div class="hy-cards hy-cards-4">{cards}</div>', "hy-tone")


# ---------------------------------------------------------------- quickstart

def examples(lang):
    zh = lang == "zh"
    prompt = "用三句话介绍你自己，并说明你擅长的任务。" if zh else "Introduce yourself in three sentences and say what tasks you are best at."
    payload = json.dumps({"model": MODEL_ID, "messages": [{"role": "user", "content": prompt}]}, ensure_ascii=False, indent=2)
    curl = ('curl https://anyaigc.ai/v1/chat/completions \\\n'
            '  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            f"  -d '{payload}'")
    python = ("# pip install openai\n"
              "import os\n"
              "from openai import OpenAI\n\n"
              'client = OpenAI(api_key=os.environ["ANYAIGC_API_KEY"], base_url="https://anyaigc.ai/v1")\n\n'
              "completion = client.chat.completions.create(\n"
              f'    model="{MODEL_ID}",\n'
              f'    messages=[{{"role": "user", "content": "{prompt}"}}],\n'
              ")\n"
              "print(completion.choices[0].message.content)\n")
    stream = ("# pip install openai\n"
              "import os\n"
              "from openai import OpenAI\n\n"
              'client = OpenAI(api_key=os.environ["ANYAIGC_API_KEY"], base_url="https://anyaigc.ai/v1")\n\n'
              "stream = client.chat.completions.create(\n"
              f'    model="{MODEL_ID}",\n'
              f'    messages=[{{"role": "user", "content": "{prompt}"}}],\n'
              "    stream=True,\n"
              ")\n"
              "for chunk in stream:\n"
              "    if chunk.choices and chunk.choices[0].delta.content:\n"
              '        print(chunk.choices[0].delta.content, end="", flush=True)\n'
              "print()\n")
    node = ("// Node.js 18+，保存为 hy4-flash.mjs 后运行：node hy4-flash.mjs\n" if zh else "// Node.js 18+. Save as hy4-flash.mjs and run: node hy4-flash.mjs\n") + (
        'const res = await fetch("https://anyaigc.ai/v1/chat/completions", {\n'
        '  method: "POST",\n'
        "  headers: {\n"
        "    Authorization: `Bearer ${process.env.ANYAIGC_API_KEY}`,\n"
        '    "Content-Type": "application/json",\n'
        "  },\n"
        "  body: JSON.stringify({\n"
        f'    model: "{MODEL_ID}",\n'
        f'    messages: [{{ role: "user", content: "{prompt}" }}],\n'
        "  }),\n"
        "});\n"
        "const data = await res.json();\n"
        "console.log(data.choices[0].message.content);\n")
    question = "这张图里有什么？请列出关键信息。" if zh else "What is in this image? List the key details."
    image = json.dumps({"model": MODEL_ID, "messages": [{"role": "user", "content": [
        {"type": "text", "text": question},
        {"type": "image_url", "image_url": {"url": "https://example.com/chart.png"}}]}]}, ensure_ascii=False, indent=2)
    image_code = ('curl https://anyaigc.ai/v1/chat/completions \\\n'
                  '  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
                  '  -H "Content-Type: application/json" \\\n'
                  f"  -d '{image}'")
    msg = json.dumps({"model": MODEL_ID, "max_tokens": 2048, "messages": [{"role": "user", "content": prompt}]}, ensure_ascii=False, indent=2)
    messages_code = ('curl https://anyaigc.ai/v1/messages \\\n'
                     '  -H "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
                     '  -H "Content-Type: application/json" \\\n'
                     f"  -d '{msg}'")
    return [("cURL", curl), ("Python", python), (pick(lang, "Python 流式", "Python streaming"), stream), ("Node.js", node),
            (pick(lang, "图像理解", "Image input"), image_code), (pick(lang, "Anthropic 格式", "Anthropic format"), messages_code)]


def quickstart_section(lang):
    tabs = examples(lang)
    buttons, panels = [], []
    for i, (name, code) in enumerate(tabs):
        pid = f"hy-code-{i}"
        buttons.append(f'<button type="button" data-panel="{pid}" aria-selected="{"true" if i == 0 else "false"}">{h(name)}</button>')
        panels.append(f'<div class="hy-code" id="{pid}"{"" if i == 0 else " hidden"}><div class="hy-code-head"><span>{h(name)}</span>'
                      f'<button class="hy-copy" type="button" data-copy="{pid}-src">{pick(lang, "复制", "Copy")}</button></div>'
                      f'<pre><code id="{pid}-src">{h(code)}</code></pre></div>')
    steps = [pick(lang, "注册 AnyAIGC，在控制台创建 API Key。", "Sign up and create an API key in the console."),
             pick(lang, "把 Key 写入环境变量 ANYAIGC_API_KEY。", "Put the key in the ANYAIGC_API_KEY environment variable."),
             pick(lang, "请求 /v1/chat/completions 或 /v1/messages，model 填 hy4-flash。", "Call /v1/chat/completions or /v1/messages with model hy4-flash.")]
    steps_html = "".join(f"<li><b>{i:02d}</b><span>{h(s)}</span></li>" for i, s in enumerate(steps, 1))
    note = pick(lang,
                "Chat Completions 返回 OpenAI 格式的 JSON：用量在 usage.prompt_tokens、usage.completion_tokens，缓存命中见 usage.prompt_tokens_details.cached_tokens。Anthropic 格式的示例来自 API 文档，图片、工具、思考等扩展参数在 hy4-flash 上的支持情况以 API 文档为准。",
                "Chat Completions returns OpenAI-format JSON: usage reports prompt_tokens and completion_tokens, and cache hits appear in usage.prompt_tokens_details.cached_tokens. The Anthropic-format example follows the API docs; check the docs for image, tool and thinking parameters on hy4-flash.")
    body = (f'<ol class="hy-steps">{steps_html}</ol>'
            f'<div class="hy-endpoint"><code>POST https://anyaigc.ai/v1/chat/completions</code><a href="{doc(lang)}">{pick(lang, "Chat Completions 文档", "Chat Completions reference")} ↗</a>'
            f'<a href="{doc(lang, DOC_MESSAGES)}">{pick(lang, "Messages 文档", "Messages reference")} ↗</a></div>'
            f'<div class="hy-tabs" aria-label="{pick(lang, "代码示例", "Code examples")}">{"".join(buttons)}</div>{"".join(panels)}<p class="hy-note">{h(note)}</p>')
    return section("quickstart", pick(lang, "快速开始", "QUICKSTART"), pick(lang, "三步接入 Hy4 Flash API", "Call Hy4 Flash in three steps"), "", body)


# ---------------------------------------------------------------- enterprise / trust / faq / footer

def enterprise_section(lang):
    cards = [(pick(lang, "增值税发票", "Invoices"), pick(lang, "增值税普通发票、增值税专用发票（专票）都能开，按实际充值金额开具。", "Invoices for every top-up, including Chinese VAT general and special invoices.")),
             (pick(lang, "对公转账", "Bank transfer"), pick(lang, "支持企业对公转账充值。", "Top up by corporate bank transfer.")),
             (pick(lang, "签订合同", "Contracts"), pick(lang, "可签订服务合同，配合采购与法务流程。", "Sign a service agreement for procurement and legal review.")),
             (pick(lang, "专属对接", "Dedicated support"), pick(lang, "专属客服和技术对接。", "Dedicated support and a technical contact."))]
    grid = "".join(f'<article class="hy-ent"><span class="hy-num">{i:02d}</span><h3>{h(t)}</h3><p>{h(d)}</p></article>' for i, (t, d) in enumerate(cards, 1))
    pay = payments.pay_row(lang, "hy").strip()
    actions = ('<div class="hy-actions">' + button(pick(lang, "联系企业客服", "Talk to sales"), SUPPORT)
               + button(pick(lang, "先注册试用", "Start with a free account"), REG, "line") + "</div>")
    return section("enterprise", pick(lang, "企业接入", "ENTERPRISE"), pick(lang, "企业接入 Hy4 Flash API", "Hy4 Flash API for teams and enterprises"),
                   pick(lang, "研发、财务、法务和采购可以一起完成接入。", "Everything engineering, finance, legal and procurement need to sign off."),
                   f'<div class="hy-ents">{grid}</div>{pay}{actions}', "hy-tone")


def trust_section(lang):
    items = "".join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in trust.ITEMS[lang])
    return section("trust", pick(lang, "信任与保障", "TRUST"), trust.HEAD[lang][0], h(trust.HEAD[lang][1]),
                   f'<ul class="trust-list">{items}</ul><div class="hy-actions">'
                   + button(pick(lang, "先注册领取 200 万 tokens", "Sign up for 2M free tokens"), REG) + "</div>")


def faq_section(lang, faqs):
    body = '<div class="hy-faq">' + "".join(
        f'<details><summary><h3>{h(q)}</h3></summary><div class="hy-answer"><p>{h(a)}</p></div></details>' for q, a in faqs) + "</div>"
    return section("faq", "FAQ", pick(lang, "Hy4 Flash API 常见问题", "Hy4 Flash API FAQ"), "", body)


def final(lang):
    other = "en" if lang == "zh" else "zh"
    links = [(f"/{lang}/models/", pick(lang, "全部模型专题", "All model guides")), (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
             (doc(lang), pick(lang, "API 文档", "API documentation")), (f"/{other}/models/{SLUG}", pick(lang, "English version", "中文版"))]
    link_html = "".join(f'<li><a href="{h(u)}"{" hreflang=" + chr(34) + pick(other, "zh-CN", "en") + chr(34) if u.startswith("/" + other) else ""}>{h(t)}</a></li>' for u, t in links)
    footer_links = [(f"/{lang}/models/", pick(lang, "模型专题", "Model guides")), (PRICING_URL, pick(lang, "模型广场", "Model catalog")),
                    (CONSOLE, pick(lang, "控制台", "Console")), (SUPPORT, pick(lang, "联系客服", "Support")),
                    ("/privacy", pick(lang, "隐私政策", "Privacy")), ("/terms", pick(lang, "服务条款", "Terms"))]
    legal = pick(lang, "Hy4 Flash、腾讯混元是腾讯公司的商标，AnyAIGC 是独立 API 服务商，与其无隶属关系。模型使用与商用条款以腾讯混元官方条款为准。",
                 "Hy4 Flash and Tencent Hunyuan are trademarks of Tencent. AnyAIGC is an independent API provider and is not affiliated with Tencent. Model use and commercial terms follow Tencent Hunyuan's official terms.")
    return (f'<section class="hy-final" aria-labelledby="final-title"><div class="hy-wrap">{mark("hy-final-mark", 56)}'
            f'<h2 id="final-title">{h(pick(lang, "把 Hy4 Flash 接入你的下一个产品", "Build your next product with Hy4 Flash"))}</h2>'
            f'<p>{h(pick(lang, "注册 AnyAIGC，新用户送 200 万 tokens，一个 API Key 调用 300+ 模型。", "Sign up for AnyAIGC, get 2M free tokens, and call 300+ models with one API key."))}</p>'
            '<div class="hy-actions">' + button(pick(lang, "获取 API Key", "Get an API key"), REG, "light")
            + button(pick(lang, "查看模型广场", "Open the model catalog"), PRICING_URL, "ghost") + "</div>"
            f'<ul class="hy-final-links">{link_html}</ul></div></section></main>\n'
            '<footer class="hy-footer"><div class="hy-wrap"><a class="hy-brand" href="/">AnyAIGC</a>'
            f'<nav aria-label="{pick(lang, "页脚", "Footer")}">' + "".join(f'<a href="{h(u)}">{h(t)}</a>' for u, t in footer_links)
            + f'</nav><p class="hy-legal">{h(legal)}</p></div></footer>\n')


def render(lang):
    faqs = faq_items(lang)
    out = (head(lang, faqs) + topbar(lang) + nav(lang) + hero(lang) + specs_section(lang) + pricing_section(lang)
           + vs_hy4_section(lang) + uses_section(lang) + platform_section(lang) + quickstart_section(lang)
           + enterprise_section(lang) + trust_section(lang) + faq_section(lang, faqs) + final(lang))
    return out + f'<script src="/assets/models/hy4.js?v={VER}" defer></script>\n</body>\n</html>\n'


def main():
    for lang in ("zh", "en"):
        path = ROOT / lang / "models" / f"{SLUG}.html"
        path.write_text(render(lang), encoding="utf-8", newline="\n")
        print(lang, SLUG)


if __name__ == "__main__":
    main()
